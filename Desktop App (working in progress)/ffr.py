import asyncio
import sys
import numpy
import cv2
import numpy as np
import torch
import requests

from mtcnn import create_mtcnn
import aiohttp
import pickle
import jsonpickle
from tracker import Tracker
import os
import json
tracker = Tracker(150, 1, 5, 0)

numpy.set_printoptions(threshold=sys.maxsize)
device = "cpu"
model_dict = {
    "mtcnn": create_mtcnn(device=device),
}
model = model_dict[os.environ["MODEL_NAME"]]
device_name = os.environ["DEVICE_NAME"]
cam = os.environ["CAM"]
if cam=="0":
    cam = cv2.CAP_DSHOW

def encode(img):
    pckl = pickle.dumps(img)
    serialized = jsonpickle.encode(pckl)
    response = requests.get("http://localhost:8070/get_face", json={"image": serialized, "device": device_name})
    return json.loads(response.text)





def create_new_log(image, name, description):
    response = requests.post("http://localhost:8090/api/create_log", json={"device": device_name, "image": cv2.cvtColor(cv2.resize(image, (image.shape[0]//2, image.shape[1]//3)), cv2.COLOR_BGR2RGB).tolist(), "fullname": name, "description": description})
    return json.loads(response.text)
async def detect():
    print("starting")
    ids = {}
    frame_number = 0
    vdo = cv2.VideoCapture(cv2.CAP_DSHOW)
    print("camera is ready")
    names = []
    mx = -1
    while True:
        res= []
        ft = 0
        print(1)
        frame_number += 1
        ret, img0 = vdo.read()
        batch_boxes, cropped_images = model.detect_box(img0)
        centers = []
        if cropped_images is not None:
            for s in range(len(cropped_images)):
                centers.append(
                    (int(batch_boxes[s][0] + batch_boxes[s][2] / 2), int(batch_boxes[s][1] + batch_boxes[s][3] / 2)))
            tracker.Update(np.array(centers))
            for s in range(len(cropped_images)):
                if tracker.tracks[s].track_id not in ids or frame_number%10==1:
                    if ft == 0:
                        res = []
                        ft = 1
                    res.append(cropped_images[s].numpy())

            if len(res) != 0:
                array = encode(torch.Tensor(np.array(res)))
                names, descrptions = array["fullnames"], array["descriptions"]

                for i in range(len(tracker.tracks)):
                    try:
                        if tracker.tracks[i].track_id not in ids:
                            ids[tracker.tracks[i].track_id] = names[i]
                    except:
                        pass
            ls = list(ids.keys())
            for id in range(len(names)):
                try:
                    #if names[id]=="Undetected":
                    #    continue
                    cv2.putText(img0, names[id], (int(batch_boxes[id][0]), int(batch_boxes[id][1]) - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 191, 0), 1)
                    cv2.rectangle(img0, (int(batch_boxes[id][0]), int(batch_boxes[id][1])),
                              (int(batch_boxes[id][2]), int(batch_boxes[id][3])), (255, 191, 0), 2)
                    print(mx, ls[id])
                    if mx < ls[id]:
                        mx = ls[id]
                        create_new_log(img0, names[id], descrptions[id])
                except Exception as e:
                    print(e)

        if len(names) <= 1:
            cv2.imwrite(f"./test/{frame_number}.jpg", img0)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break


async def main():
    await detect()


if __name__ == "__main__":
    asyncio.run(main())