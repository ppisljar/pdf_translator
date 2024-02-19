import re
from tqdm import tqdm
from .base import FontBase 

class SimpleFont(FontBase):
    FONT_SIZE = 29

    def init(self, cfg: dict):
        self.cfg = cfg
 
    def get_all_fonts(self, layout) -> str:

        for i, line in tqdm(enumerate(layout)):
            if line.type in ["text", "list", "title"]:
                # update this so image is created from images and layout bbox info
                image = line.image
                ocr_results = self.get_font(image, line.line_cnt)
                text = list(map(lambda x: x[0],ocr_results[1]))
                text = " ".join(text)
                text = re.sub(r"\n|\t|", " ", text)
                line.text = text

                lasty = 0
                cnt = 0
                for x in ocr_results[0]:
                    if x[0][1] > lasty:
                        cnt+=1
                        lasty = x[2][1]

                line.line_cnt = cnt


        return layout
    
    def get_font(self, image, line_cnt = 1):
        width = image.size[0]
        height = image.size[1]

        font_size = height / line_cnt

        print(f"width: {width}, height: {height}, fs: {font_size}")
        if font_size > 46: 
            font_size = self.FONT_SIZE + 6
            ygain = 40
        elif font_size > 31: 
            font_size = self.FONT_SIZE
            ygain = 33
        elif font_size > 28.5: 
            font_size = self.FONT_SIZE - 3
            ygain = 30
        else:
            font_size = self.FONT_SIZE - 6
            ygain = 22

        return 'TimesNewRoman.ttf', font_size, ygain
                