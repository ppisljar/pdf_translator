import cv2
import numpy as np
from tqdm import tqdm
from pathlib import Path
from pdf2image import convert_from_bytes, convert_from_path
from .base import LayoutBase 
from utils import LayoutAnalyzer

class DiTLayout(LayoutBase):
    def init(self, cfg: dict):
        self.layout_model = LayoutAnalyzer(
            model_root_dir= Path("models/unilm"), device=cfg['device']
        )

        self.DPI = cfg['DPI'] if 'DPI' in cfg else 200
 
    def get_layout(self, pdf_path_or_bytes: str, p_from, p_to) -> str:
        
        if isinstance(pdf_path_or_bytes, Path):
            pdf_images = convert_from_path(pdf_path_or_bytes, dpi=self.DPI)
        else:
            pdf_images = convert_from_bytes(pdf_path_or_bytes, dpi=self.DPI)

        data = []
        images = []

        for i, image in tqdm(enumerate(pdf_images)):
            if i < p_from: continue
            if i > p_to and p_to != 0: break

            result = self.get_single_layout(image)
            images.append(image)
            data.append(result)

        return data, images
    
    def get_single_layout(self, image):
        img = np.array(image, dtype=np.uint8)
        result = self.layout_model(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return result
                