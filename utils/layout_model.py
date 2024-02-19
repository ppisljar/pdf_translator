import sys
from pathlib import Path
import cv2
import numpy as np
from typing import Literal, Optional
from dataclasses import asdict, dataclass, field

from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.config import CfgNode as CN


def add_vit_config(cfg):
    """
    Add config for VIT.
    """
    _C = cfg

    _C.MODEL.VIT = CN()

    # CoaT model name.
    _C.MODEL.VIT.NAME = ""

    # Output features from CoaT backbone.
    _C.MODEL.VIT.OUT_FEATURES = ["layer3", "layer5", "layer7", "layer11"]

    _C.MODEL.VIT.IMG_SIZE = [224, 224]

    _C.MODEL.VIT.POS_TYPE = "shared_rel"

    _C.MODEL.VIT.DROP_PATH = 0.

    _C.MODEL.VIT.MODEL_KWARGS = "{}"

    _C.SOLVER.OPTIMIZER = "ADAMW"

    _C.SOLVER.BACKBONE_MULTIPLIER = 1.0

    _C.AUG = CN()

    _C.AUG.DETR = False


#from ditod import add_vit_config
#from ditod.VGTTrainer import DefaultPredictor

@dataclass
class Layout:
    type: Literal["text", "title", "list", "table", "figure"]
    bbox: tuple[int, ...]
    score: float
    image: np.ndarray = field(init=False)
    text: Optional[str] = None
    translated_text: Optional[str] = None
    line_cnt: Optional[int] = None
    font: Optional[dict] = None
    
    def to_dict(self):
        # Convert the dataclass to a dict
        d = asdict(self)
        # Handle the numpy array; here we're converting it to a list for simplicity
        # Another option is to convert to a base64 string if you need to save binary data
        d['image'] = 'test'  # For simplicity
        d['bbox'] = d['bbox'].tolist()
        d['score'] = float(d['score'])
        return d


class LayoutAnalyzer:
    def __init__(self, model_root_dir: Path, device: str = "cuda") -> None:
        self.predictor = self._load_model(model_root_dir, device=device)

    def __call__(self, image: np.ndarray) -> list[Layout]:
        #grid_path = args.grid_root + args.image_name + ".pdf.pkl"
        output = self.predictor(image)["instances"].to("cpu")

        layouts = []
        for class_id, box, score in zip(
            output.pred_classes.numpy(),
            output.pred_boxes.tensor.numpy().astype(int),
            output.scores.numpy(),
        ):
            if score > 0.8:
                layouts.append(
                    Layout(
                        type=self._id_to_class_names[class_id], bbox=box, score=score
                    )
                )

        #layouts = self._remove_overlapping_layouts(layouts)

        for layout in layouts:
            layout.image = self._get_image(image, layout.bbox)

        return layouts

    def _remove_overlapping_layouts(self, layouts: list[Layout]) -> list[Layout]:
        if not layouts:
            return []

        # Sort layouts by confidence score (high to low)
        layouts.sort(key=lambda x: x.score, reverse=True)

        non_overlapping_layouts = []
        while layouts:
            # Take the layout with the highest score
            current_layout = layouts.pop(0)
            non_overlapping = True

            for other_layout in non_overlapping_layouts:
                # If IoU is above a threshold (e.g., 0.5), consider it as overlapping
                if self._calculate_iou(current_layout.bbox, other_layout.bbox) > 0.5:
                    non_overlapping = False
                    break

            if non_overlapping:
                non_overlapping_layouts.append(current_layout)

        return non_overlapping_layouts

    def _get_image(self, image: np.ndarray, bbox: tuple[float, ...]) -> np.ndarray:
        x1, y1, x2, y2 = bbox
        return image[int(y1) : int(y2), int(x1) : int(x2)]

    @property
    def _id_to_class_names(self) -> dict[int, str]:
        return {
            0: "text",
            1: "title",
            2: "list",
            3: "table",
            4: "figure",
        }

    def _load_model(
        self, model_root_dir: Path, device: str = "cuda"
    ) -> DefaultPredictor:
        cfg = get_cfg()
        add_vit_config(cfg)
        cfg.merge_from_file(str(model_root_dir / "config/cascade_dit_base.yml"))
        cfg.MODEL.WEIGHTS = str(model_root_dir / "publaynet_dit-b_cascade.pth")
        cfg.MODEL.DEVICE = device
        return DefaultPredictor(cfg)

    def _calculate_iou(self, box1: tuple[float, ...], box2: tuple[float, ...]) -> float:
        x1, y1, x2, y2 = box1
        x1_, y1_, x2_, y2_ = box2

        # calculate the intersection coordinates
        xi1 = max(x1, x1_)
        yi1 = max(y1, y1_)
        xi2 = min(x2, x2_)
        yi2 = min(y2, y2_)
        inter_area = max(xi2 - xi1, 0) * max(yi2 - yi1, 0)

        # calculate each box area
        box1_area = (x2 - x1) * (y2 - y1)
        box2_area = (x2_ - x1_) * (y2_ - y1_)

        # calculate union area
        union_area = box1_area + box2_area - inter_area

        # compute the IoU
        return inter_area / union_area if union_area != 0 else 0


if __name__ == "__main__":
    layout_analyzer = LayoutAnalyzer(Path("models/"))
    image = cv2.imread("assets/sample1.png")
    print(layout_analyzer(image))
