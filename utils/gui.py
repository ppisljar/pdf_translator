from pathlib import Path
from typing import Any

import gradio as gr
import requests

TRANSLATE_URL = "http://localhost:8765/translate_pdf/"
CLEAR_TEMP_URL = "http://localhost:8765/clear_temp_dir/"


def translate_request(file: Any, from_lang: Any, to_lang: Any, from_page: int, to_page: int, both: bool) -> tuple[Path]:
    """Sends a POST request to the translator server to translate a PDF.

    Parameters
    ----------
    file : Any
        the PDF to be translated.

    Returns
    -------
    tuple[Path, list[Image.Image]]
        Path to the translated PDF and a list of images of the
        translated PDF.
    """
    response = requests.post(TRANSLATE_URL, files={"input_pdf": open(file.name, "rb")}, data={
        "from_lang": from_lang, "to_lang": to_lang, "p_from": from_page, "p_to": to_page, "side_by_side": both
    })

    if response.status_code == 200:
        with open("temp/translated.pdf", "wb") as f:
            f.write(response.content)

        return str("temp/translated.pdf")
    else:
        print(f"An error occurred: {response.status_code}")


def create_gradio_app(langs):
    with gr.Blocks(theme="Soft") as demo:
        with gr.Column():
            title = gr.Markdown("## PDF Translator")
            file = gr.File(label="select file")

            
            from_lang = gr.Dropdown(label='from language', choices=langs, value="English")
            to_lang = gr.Dropdown(label='to language', choices=langs, value="Slovenian")
            from_page = gr.Number(label='from page')
            to_page = gr.Number(label='to page')
            both = gr.Checkbox(label='render side by side', value=True)

            btn = gr.Button(value="convert")
            translated_file = gr.File(label="translated fie", file_types=[".pdf"])

            btn.click(
                translate_request,
                inputs=[file, from_lang, to_lang, from_page, to_page, both],
                outputs=[translated_file],
            )

        return demo

if __name__ == "__main__":
    app = create_gradio_app()
    app.launch(share=True)