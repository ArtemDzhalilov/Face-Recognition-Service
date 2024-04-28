from types import MethodType

import torch
from facenet_pytorch import MTCNN

def detect_box(self, img, device="cpu", save_path=None):
    batch_boxes, batch_probs, batch_points = self.detect(torch.from_numpy(img).to(device), landmarks=True)
    if not self.keep_all:
        batch_boxes, batch_probs, batch_points = self.select_boxes(
            batch_boxes, batch_probs, batch_points, img, method=self.selection_method
        )
    faces = self.extract(img, batch_boxes, save_path)
    return batch_boxes, faces


def create_mtcnn(device="cpu"):
    mtcnn = MTCNN(keep_all=True, device=device, image_size=112)
    mtcnn.detect_box = MethodType(detect_box, mtcnn)
    return mtcnn