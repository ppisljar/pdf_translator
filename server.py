import copy
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple, Union
import json
import cv2
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
import yaml
import os

#sys.path.append(str(Path(__file__).parent))

from utils import LayoutAnalyzer, OCRModel, fw_fill, create_gradio_app

from .modules import load_translator


def load_config(base_config_path, override_config_path):
    with open(base_config_path, 'r') as base_file:
        base_config = yaml.safe_load(base_file)
    
    final_config = base_config

    if os.path.exists(override_config_path):
        with open(override_config_path, 'r') as override_file:
            override_config = yaml.safe_load(override_file)
            final_config = update(base_config, override_config)
    
    # Update the base config with the override config
    # This recursively updates nested dictionaries
    def update(d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    return final_config

cfg = load_config('config.yaml', 'config.dev.yaml')

translator = load_translator(cfg['translator'])

def draw_text(draw, processed_text, current_fnt, font_size, width, ygain):
    y = 0
    first = len(processed_text.split("\n")) > 1
    for l in processed_text.split("\n"):
        words = l.split(" ")
        words_length = sum(draw.textlength(w, font=current_fnt) for w in words)
        if first: words_length += 40
        space_length = (width - words_length) / (len(words))
        if (space_length > 40): space_length = font_size/2.4
        x = 0
        if first: x+= 40
        for word in words:
            draw.text((x, y), word, font=current_fnt, fill="black")
            x += draw.textlength(word, font=current_fnt) + space_length
        y += ygain
        first = False

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
    FONT_SIZE = 29

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

        gradioapp = create_gradio_app()
        gr.mount_gradio_app(self.app, gradioapp, '/')

        self.__load_models(model_root_dir)
        self.__load_fonts()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = Path(self.temp_dir.name)


    def __load_models(self, model_root_dir: Path, device: str = "cuda"):
        """Backend function for loading models.

        Called in the constructor.
        Load the layout model, OCR model, translation model and font.

        Parameters
        ----------
        model_root_dir: Path
            Path to the directory containing the models.
        device: str
            Device to use for the layout model.
            Defaults to "cuda".
        """
        self.device = device

        self.layout_model = LayoutAnalyzer(
            model_root_dir=model_root_dir / "unilm", device=self.device
        )
        self.ocr_model = OCRModel(
            model_root_dir=model_root_dir / "paddle-ocr", device=self.device
        )

    def __load_fonts(self):
        # load fonts
        # TODO: add font detection logic
        self.fnt = ImageFont.truetype("fonts/TimesNewRoman.ttf", self.FONT_SIZE) 
        self.fnt_small = ImageFont.truetype("fonts/TimesNewRoman.ttf", self.FONT_SIZE - 3) 
        self.fnt_xsmall = ImageFont.truetype("fonts/TimesNewRoman.ttf", self.FONT_SIZE - 6) 
        self.fnt_big = ImageFont.truetype("fonts/TimesNewRoman.ttf", self.FONT_SIZE + 6) 

    def get_font_size(self, width, height, cnt):
        font_size = height / cnt

        print(f"width: {width}, height: {height}, fs: {font_size}")
        if font_size > 46: 
            current_fnt = self.fnt_big
            font_size = self.FONT_SIZE + 6
            ygain = 40
        elif font_size > 31: 
            current_fnt = self.fnt
            font_size = self.FONT_SIZE
            ygain = 33
        elif font_size > 28.5: 
            current_fnt = self.fnt_small
            font_size = self.FONT_SIZE - 3
            ygain = 30
        else:
            current_fnt = self.fnt_xsmall
            font_size = self.FONT_SIZE - 6
            ygain = 22

        return current_fnt, font_size, ygain
    
    def run(self):
        """Run the API server"""
        uvicorn.run(self.app, host="0.0.0.0", port=8765)

    async def translate_pdf(self, input_pdf: UploadFile = File(...), from_lang: str = Form(...), to_lang: str = Form(...), p_from: int = Form(...), p_to: int = Form(...), side_by_side: bool = Form(...) ) -> FileResponse:
        """API endpoint for translating PDF files.

        Parameters
        ----------
        input_pdf: UploadFile
            Input PDF file

        Returns
        -------
        FileResponse
            Translated PDF file
        """
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


        # 1. convert pdf to images
        if isinstance(pdf_path_or_bytes, Path):
            pdf_images = convert_from_path(pdf_path_or_bytes, dpi=self.DPI)
        else:
            pdf_images = convert_from_bytes(pdf_path_or_bytes, dpi=self.DPI)

        pdf_files = []

        
        with open('out.json', 'w') as file:
            data = []
            reached_references = False
            for i, image in tqdm(enumerate(pdf_images)):
                if i < p_from: continue
                if i > p_to and p_to != 0: break
                output_path = output_dir / f"{i:03}.pdf"
                if not reached_references:
                    # this function does steps 2-6
                    img, original_img, reached_references, result = self.__translate_one_page(
                        image=image,
                        reached_references=reached_references,
                        from_lang=from_lang,
                        to_lang=to_lang
                    )
                    data.append(result)
                    if side_by_side:
                        fig, ax = plt.subplots(1, 2, figsize=(20, 14))
                        ax[0].imshow(original_img)
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

            json.dump(data, file)

        # 7. merge
        self.__merge_pdfs(pdf_files)


    def __translate_one_page(
        self,
        image: Image.Image,
        reached_references: bool,
        from_lang: str,
        to_lang: str,
    ) -> Tuple[np.ndarray, np.ndarray, bool]:
        """Translate one page of the PDF file.

        There are some heuristics to clean-up the results of translation:
            1. Remove newlines, tabs, brackets, slashes, and pipes

        Parameters
        ----------
        image: Image.Image
            Image of the page
        reached_references: bool
            Whether the references section has been reached.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, bool]
            Translated image, original image,
            and whether the references section has been reached.
        """

        # 2. run layout detection
        img = np.array(image, dtype=np.uint8)
        original_img = copy.deepcopy(img)
        result = self.layout_model(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

        out_result = []
        for line in result:

            out_line = line.to_dict()
            
            if line.type in ["text", "list"]:
                # 3. run ocr on every detected block
                ocr_r  =  self.ocr_model(line.image)

                # count number of lines
                lasty = 0
                cnt = 0
                for x in ocr_r[0]:
                    if x[0][1] > lasty:
                        cnt+=1
                        lasty = x[2][1]

                ocr_results = list(map(lambda x: x[0],ocr_r[1]))
                out_line['text_list'] = ocr_results
                out_result.append(out_line)

                if len(ocr_results) > 0:
                    text = " ".join(ocr_results)
                    text = re.sub(r"\n|\t|", " ", text)
                    #translated_text = self.__translate_sl(text)

                    # 4. translate text
                    translated_text = translator.translate(text, from_lang, to_lang)

                    height = line.bbox[3] - line.bbox[1]
                    width = line.bbox[2] - line.bbox[0]
                    
                    # 5. detect font properties
                    current_fnt, font_size, ygain = self.get_font_size(width, height, cnt)

                    # calculate text wrapping
                    processed_text = fw_fill(
                        translated_text,
                        width=int((line.bbox[2] - line.bbox[0]) / ((font_size)/2.4))
                        - 1,
                    )
                    
                    # create new image block with new text
                    new_block = Image.new(
                        "RGB",
                        (
                            line.bbox[2] - line.bbox[0],
                            line.bbox[3] - line.bbox[1],
                        ),
                        color=(255, 255, 255),
                    )
                    draw = ImageDraw.Draw(new_block)
                    draw_text(draw, processed_text, current_fnt, font_size, width, ygain)

                    # copy over original image
                    new_block = np.array(new_block)
                    img[
                        int(line.bbox[1]) : int(line.bbox[3]),
                        int(line.bbox[0]) : int(line.bbox[2]),
                    ] = new_block
            
            elif line.type == "title":
                # TODO: add title translation support
                try:
                    print("\n\ngot title ...")
                    title = self.ocr_model(line.image)[1][0][0]
                    print(f"title: {title}")
                except IndexError:
                    continue
                if title.lower() == "references" or title.lower() == "reference":
                    reached_references = True

            else:
                # TODO: add list, table and image translation support
                print(f"\n\n\nunknown: {line.type}")

        return img, original_img, reached_references, out_result

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
