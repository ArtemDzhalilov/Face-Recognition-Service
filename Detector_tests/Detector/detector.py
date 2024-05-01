import time

import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
from .dsfd.face_detection import build_detector
from .ulfdm.vision.ssd.mb_tiny_fd import create_mb_tiny_fd, create_mb_tiny_fd_predictor
from .ulfdm.vision.ssd.mb_tiny_RFB_fd import create_Mb_Tiny_RFB_fd, create_Mb_Tiny_RFB_fd_predictor
from ultralytics import YOLO
import torch
from torch import nn
import numpy as np
import os
import torchvision

from facenet_pytorch.models.utils.detect_face import extract_face
def fixed_image_standardization(image_tensor):
    processed_tensor = (image_tensor - 127.5) / 128.0
    return processed_tensor

class Detector:
    def __init__(self, model_type: str, device, image_size, output_size):
        self.model_type = model_type
        self.device = device
        self.image_size = image_size
        self.output_size = output_size
        self.margin = 0
        if model_type == 'mtcnn':
            self.detector = MTCNN(image_size = image_size, device = device)
        elif model_type == 'dsfd':
            self.detector = build_detector(
                "DSFDDetector",
                max_resolution=output_size
            )
        elif model_type=='ulfdm_small':
            net = create_mb_tiny_fd(2, is_test=False, device=self.device)
            self.detector = create_mb_tiny_fd_predictor(net, candidate_size=1000, device=self.device)
        elif model_type=='ulfdm_big':
            net = create_Mb_Tiny_RFB_fd(2, is_test=False, device=self.device)
            self.detector = create_Mb_Tiny_RFB_fd_predictor(net, candidate_size=1000, device=self.device)
        elif model_type=='yolon':
            self.detector = YOLO('./Detector/yolov8n-face.pt')
        elif model_type=='yolom':
            self.detector = YOLO('./Detector/yolov8m-face.pt')
        elif model_type=='yolol':
            self.detector = YOLO('./Detector/yolov8l-face.pt')
        else:
            raise Exception("The model type is wrong!")
        self.trans = torchvision.transforms.Compose([
            torchvision.transforms.Resize((output_size, output_size)),
        ])
        self.yolo_trans = torchvision.transforms.Compose([
            torchvision.transforms.Resize((640, 640)),
        ])

    def detect_with_extractor(self, image):
        if self.model_type == 'mtcnn':
            boxes = self.detector.detect(image)[0]
        elif self.model_type == 'dsfd':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = self.detector.detect(image)[:, :4]
        elif self.model_type=='ulfdm_small':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = self.detector.predict(image, False, 0.7)[0]
        elif self.model_type=='ulfdm_big':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = self.detector.predict(image, False, 0.7)[0]

        elif self.model_type=='yolon':
            if type(image) == torch.Tensor:
                image = image.view(1, image.shape[2], image.shape[0], image.shape[1])
                image = image.float()
                image = self.yolo_trans(image)
            elif type(image) == np.ndarray:
                image = image.astype(np.float32)
                image = cv2.resize(image, (640, 640))
            boxes = self.detector.predict(image, show=False, verbose=False)[0].boxes.xyxy
        elif self.model_type=='yolom':
            if type(image) == torch.Tensor:
                image = image.view(1, image.shape[2], image.shape[0], image.shape[1])
                image = image.float()
                image = self.yolo_trans(image)
            elif type(image) == np.ndarray:
                image = image.astype(np.float32)
                image = cv2.resize(image, (640, 640))
            boxes = self.detector.predict(image, show=False, verbose=False)[0].boxes.xyxy
        elif self.model_type=='yolol':
            if type(image) == torch.Tensor:
                image = image.view(1, image.shape[2], image.shape[0], image.shape[1])
                image = image.float()
                image = self.yolo_trans(image)
            elif type(image) == np.ndarray:
                image = image.astype(np.float32)
                image = cv2.resize(image, (640, 640))
            boxes = self.detector.predict(image, show=False, verbose=False)[0].boxes.xyxy
        if boxes is None:
            return None, None
        if boxes.shape[0]==0:
            return None, None
        try:
            faces = self.extract(image, boxes, None)
        except:
            return None, None
        if faces is None:
            return None, None
        faces = self.trans(faces)
        if type(faces) == torch.Tensor:
            faces = faces.numpy()
        return faces, boxes

    def extract(self, img, batch_boxes, save_path):
        # Determine if a batch or single image was passed
        batch_mode = True
        if (
                not isinstance(img, (list, tuple)) and
                not (isinstance(img, np.ndarray) and len(img.shape) == 4) and
                not (isinstance(img, torch.Tensor) and len(img.shape) == 4)
        ):
            img = [img]
            batch_boxes = [batch_boxes]
            batch_mode = False

        # Parse save path(s)
        if save_path is not None:
            if isinstance(save_path, str):
                save_path = [save_path]
        else:
            save_path = [None for _ in range(len(img))]

        # Process all bounding boxes
        faces = []
        for im, box_im, path_im in zip(img, batch_boxes, save_path):
            if box_im is None:
                faces.append(None)
                continue


            faces_im = []
            for i, box in enumerate(box_im):
                face_path = path_im
                if path_im is not None and i > 0:
                    save_name, ext = os.path.splitext(path_im)
                    face_path = save_name + '_' + str(i + 1) + ext

                face = extract_face(im, box, self.output_size, self.margin, face_path)
                face = fixed_image_standardization(face)
                faces_im.append(face)

            faces_im = faces_im[0]

            faces.append(faces_im)

        if not batch_mode:
            faces = faces[0]

        return faces