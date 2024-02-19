import tempfile
from pathlib import Path
from typing import List, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import PyPDF2
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
#from starlette.middleware.wsgi import WSGIMiddleware
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field
from tqdm import tqdm
import gradio as gr


from utils import fw_fill, create_gradio_app, load_config, draw_text
from modules import load_translator, load_layout_engine, load_ocr_engine, load_font_engine




cfg = load_config('config.yaml', 'config.dev.yaml')
translator = load_translator(cfg['translator'])
layout_engine = load_layout_engine(cfg['layout'])
ocr_engine = load_ocr_engine(cfg['ocr'])
font_engine = load_font_engine(cfg['font'])



class InputPdf(BaseModel):
    """Input PDF file."""

    input_pdf: UploadFile = Field(..., title="Input PDF file")


class TranslateApi:
    """Translator API class.

    Attributes
    ----------
    app: FastAPI
        FastAPI instance
    temp_dir: tempfile.TemporaryDirectory
        Temporary directory for storing translated PDF files
    temp_dir_name: Path
        Path to the temporary directory
    font: ImageFont
        Font for drawing text on the image
    layout_model: PPStructure
        Layout model for detecting text blocks
    ocr_model: PaddleOCR
        OCR model for detecting text in the text blocks
    translate_model: MarianMTModel
        Translation model for translating text
    translate_tokenizer: MarianTokenizer
        Tokenizer for the translation model
    """

    DPI = 200

    def __init__(self, model_root_dir: Path = Path("/app/models/")):
        self.app = FastAPI()
        self.app.add_api_route(
            "/translate_pdf/",
            self.translate_pdf,
            methods=["POST"],
            response_class=FileResponse,
        )
        self.app.add_api_route(
            "/clear_temp_dir/",
            self.clear_temp_dir,
            methods=["GET"],
        )

        gradioapp = create_gradio_app(translator.get_languages())
        gr.mount_gradio_app(self.app, gradioapp, '/')

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = Path(self.temp_dir.name)

    
    def run(self):
        """Run the API server"""
        uvicorn.run(self.app, host="0.0.0.0", port=8765)

    async def translate_pdf(self, input_pdf: UploadFile = File(...), from_lang: str = Form(...), to_lang: str = Form(...), p_from: int = Form(...), p_to: int = Form(...), side_by_side: bool = Form(...) ) -> FileResponse:
        """API endpoint for translating PDF files."""
        input_pdf_data = await input_pdf.read()
        self._translate_pdf(input_pdf_data, self.temp_dir_name, from_lang, to_lang, p_from, p_to, side_by_side)

        return FileResponse(
            self.temp_dir_name / "translated.pdf", media_type="application/pdf"
        )

    async def clear_temp_dir(self):
        """API endpoint for clearing the temporary directory."""
        self.temp_dir.cleanup()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = Path(self.temp_dir.name)
        return {"message": "temp dir cleared"}

    def _translate_pdf(
        self, pdf_path_or_bytes: Union[Path, bytes], output_dir: Path, from_lang, to_lang, p_from, p_to, side_by_side
    ) -> None:
        """Backend function for translating PDF files.

        Translation is performed in the following steps:
            1. Convert the PDF file to images
            2. Detect text blocks in the images (layout detection)
            3. For each text block, detect text (ocr)
            4. translate the text
            5. detect font properties
            6. draw the new text        
            7. Merge all PDF files into one PDF file

        At 3, this function does not translate the text after
        the references section. Instead, saves the image as it is.

        Parameters
        ----------
        pdf_path_or_bytes: Union[Path, bytes]
            Path to the input PDF file or bytes of the input PDF file
        output_dir: Path
            Path to the output directory
        """

        if isinstance(pdf_path_or_bytes, Path):
            pdf_images = convert_from_path(pdf_path_or_bytes, dpi=self.DPI)
        else:
            pdf_images = convert_from_bytes(pdf_path_or_bytes, dpi=self.DPI)
        
        pdf_files = []
        
        reached_references = False
        for i, image in tqdm(enumerate(pdf_images)):
            if i < p_from: continue
            if i > p_to and p_to != 0: break
            result = layout_engine.get_single_layout(image)
            result = ocr_engine.get_all_text(result)
            result = translator.translate_all(result, from_lang, to_lang)
            result = font_engine.get_all_fonts(result)


            output_path = output_dir / f"{i:03}.pdf"
            if not reached_references:
                # this function does steps 2-6
                img, reached_references = self.__translate_one_page(
                    image=image,
                    result = result,
                    reached_references=reached_references,
                )
                if side_by_side:
                    fig, ax = plt.subplots(1, 2, figsize=(20, 14))
                    ax[0].imshow(image)
                    ax[1].imshow(img)
                    ax[0].axis("off")
                    ax[1].axis("off")
                else:
                    fig, ax = plt.subplots(1, 1, figsize=(10, 14))
                    ax.imshow(img)
                    ax.axis("off")
                plt.tight_layout()
                plt.savefig(output_path, format="pdf", dpi=self.DPI)
                plt.close(fig)
            else:
                (
                    image.convert("RGB")
                    .resize((int(1400 / image.size[1] * image.size[0]), 1400))
                    .save(output_path, format="pdf")
                )

            pdf_files.append(str(output_path))


        # 7. merge
        self.__merge_pdfs(pdf_files)


    def __translate_one_page(
        self,
        image,
        result,
        reached_references: bool,
    ) -> Tuple[np.ndarray, np.ndarray, bool]:
        """Translate one page of the PDF file."""
        img = np.array(image, dtype=np.uint8)
        for line in result:
            if line.type in ["text", "list"]:
                if line.text:

                    height = line.bbox[3] - line.bbox[1]
                    width = line.bbox[2] - line.bbox[0]
                    
                    # calculate text wrapping
                    processed_text = fw_fill(
                        line.translated_text,
                        width=int((width) / ((line.font['size'])/2.4))
                        - 1,
                    )

                    fnt = ImageFont.truetype('fonts/' + line.font['family'], line.font['size']) 
                    
                    # create new image block with new text
                    new_block = Image.new("RGB", ( width, height ), color=(255, 255, 255))
                    draw = ImageDraw.Draw(new_block)
                    draw_text(draw, processed_text, fnt, line.font['size'], width, line.font['ygain'])

                    # copy over original image
                    
                    new_block = np.array(new_block)
                    img[
                        int(line.bbox[1]) : int(line.bbox[3]),
                        int(line.bbox[0]) : int(line.bbox[2]),
                    ] = new_block
            
            elif line.type == "title":
                title = line.text
                if title.lower() == "references" or title.lower() == "reference":
                    reached_references = True

            else:
                # TODO: add list, table and image translation support
                print(f"\n\n\nunknown: {line.type}")

        return img, reached_references

    def __merge_pdfs(self, pdf_files: List[str]) -> None:
        """Merge translated PDF files into one file.

        Merged file will be stored in the temp directory
        as "translated.pdf".

        Parameters
        ----------
        pdf_files: List[str]
            List of paths to translated PDF files stored in
            the temp directory.
        """
        pdf_merger = PyPDF2.PdfMerger()

        for pdf_file in sorted(pdf_files):
            pdf_merger.append(pdf_file)
        pdf_merger.write(self.temp_dir_name / "translated.pdf")


if __name__ == "__main__":
    translate_api = TranslateApi()
    translate_api.run()
