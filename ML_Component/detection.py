from facenet_pytorch import MTCNN
from types import MethodType
import torch
import torchvision.transforms as transforms

def detect_box(self, img, save_path=None):
    batch_boxes, batch_probs, batch_points = self.detect(img, landmarks=True)
    if not self.keep_all:
        batch_boxes, batch_probs, batch_points = self.select_boxes(
            batch_boxes, batch_probs, batch_points, img, method=self.selection_method
        )
    faces = self.extract(img, batch_boxes, save_path)
    return batch_boxes, faces

class detection_model:
    def __init__(self):
        self.mtcnn = MTCNN(keep_all=True, device='cpu', image_size=112)
        self.mtcnn.detect_box = MethodType(detect_box, self.mtcnn)
        self.transforms1 = transforms.Compose([
            #transforms.Resize((128, 128)),
        ])
    def detect(self, img):
        batch_boxes, batch_probs = self.mtcnn.detect_box(torch.Tensor(img))
        batch_probs = self.transforms1(batch_probs)
        return batch_boxes, batch_probs


