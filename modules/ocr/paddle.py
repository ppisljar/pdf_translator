import re
import numpy as np
from pathlib import Path
from tqdm import tqdm
from .base import OCRBase 
from utils import OCRModel

class PaddleOCR(OCRBase):
    def init(self, cfg: dict):
        self.ocr_model = OCRModel(
            model_root_dir= Path("models/paddle-ocr"), device=cfg['device']
        )
 
    def get_all_text(self, layout) -> str:

        for i, line in tqdm(enumerate(layout)):
            if line.type in ["text", "list", "title"]:
                # update this so image is created from images and layout bbox info
                image = line.image
                ocr_results = self.get_text(image)
                text = list(map(lambda x: x[0],ocr_results[1]))
                text = " ".join(text)
                clean_text = re.sub(r"\n|\t", " ", text)
                line.text = clean_text

                lasty = 0
                cnt = 0
                for x in ocr_results[0]:
                    if x[0][1] > lasty:
                        cnt+=1
                        lasty = x[2][1]

                line.line_cnt = cnt


        return layout
    
    def get_text(self, image):
        return self.ocr_model(image)
                