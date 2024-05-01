from Detector.detector import Detector
import torch
import numpy as np
import time
import cv2
if __name__ == '__main__':
    zidane_img = cv2.imread("C:/Users/User/Desktop/python/to_github/Detector_tests/zidane.jpg")
    print(zidane_img.shape)
    detector = Detector(model_type="mtcnn", device="cpu", image_size=1000, output_size=128)
    zidane_t = torch.from_numpy(zidane_img)
    zidane_n = zidane_img.astype(np.uint8)
    st = time.time()
    boxes, faces = detector.detect_with_extractor(zidane_t.int())
    print("MTCNN (tensor input) time: ", time.time()-st)

    boxes, faces = detector.detect_with_extractor(zidane_n)
    print("MTCNN (numpy input) time: ", time.time()-st)
    del detector

    print("DSFD model not support tensor input")
    detector = Detector(model_type="dsfd", device="cpu", image_size=1000, output_size=128)
    boxes, faces = detector.detect_with_extractor(zidane_n)
    print("DSFD (numpy input) time: ", time.time()-st)
    del detector

    print("ULFDM big model not support tensor input")
    detector = Detector(model_type="ulfdm_big", device="cpu", image_size=1000, output_size=128)
    boxes, faces = detector.detect_with_extractor(zidane_n)
    print("ULFDM big (numpy input) time: ", time.time()-st)
    del detector

    print("ULFDM small model not support tensor input")
    detector = Detector(model_type="ulfdm_small", device="cpu", image_size=1000, output_size=128)
    boxes, faces = detector.detect_with_extractor(zidane_n)
    print("ULFDM small (numpy input) time: ", time.time()-st)
    del detector

    detector = Detector(model_type="yolon", device="cpu", image_size=1000, output_size=128)
    st= time.time()
    boxes, faces = detector.detect_with_extractor(zidane_t.int())
    print("YOLON (tensor input) time: ", time.time()-st)
    st = time.time()
    boxes, faces = detector.detect_with_extractor(zidane_n)
    print("YOLON (numpy input) time: ", time.time()-st)
    del detector

    detector = Detector(model_type="yolom", device="cpu", image_size=1000, output_size=128)
    st= time.time()
    boxes, faces = detector.detect_with_extractor(zidane_t.int())
    print("YOLOM (tensor input) time: ", time.time()-st)
    boxes, faces = detector.detect_with_extractor(zidane_n)
    print("YOLOM (numpy input) time: ", time.time()-st)
    del detector

    detector = Detector(model_type="yolol", device="cpu", image_size=1000, output_size=128)
    st= time.time()
    boxes, faces = detector.detect_with_extractor(zidane_t.int())
    print("YOLOL (tensor input) time: ", time.time()-st)
    boxes, faces = detector.detect_with_extractor(zidane_n)
    print("YOLOL (numpy input) time: ", time.time()-st)
    del detector


