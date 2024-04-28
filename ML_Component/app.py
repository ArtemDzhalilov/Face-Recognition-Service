import orjson
import requests
import sklearn
from tracker import Tracker
import cv2
from fastapi import FastAPI
import numpy as np
import pickle
import jsonpickle
from fastapi.responses import JSONResponse
from fastapi import Request
import json
from identification import Identification_model
from scipy.spatial.distance import cosine
from models import *
from Detector.detector import Detector
import torch
from db import DB
from sklearn import preprocessing
tracker = Tracker(150, 1, 5, 0)
device_name = "0"
database = DB("postgresql+psycopg2://postgres:postgres@localhost:5436/faces")

mtcnn = Detector(model_type="mtcnn", device="cuda:0", image_size=1000, output_size=128)

app = FastAPI()
ident_model = Identification_model("coatnet","model_weights/model.pth")


@app.get("/get_embedding")
async def get_embedding(req: Request):
    req = await req.json()
    image = req["image"]
    batch_boxes, cropped_images = mtcnn.detect_with_extractor(np.array(image).astype(np.uint8))
    if cropped_images is not None:
        if len(cropped_images) > 1:
            return JSONResponse(content={"embedding": None})
        res = ident_model.predict(x=cropped_images[0].view(1, 3, 128, 128).to(torch.device("cuda"))).detach().cpu().numpy()
        res = preprocessing.normalize(res)
        return JSONResponse(content={"embedding": res.tolist(), "image": image})
    else:
        return JSONResponse(content={"embedding": None, "image": image})

@app.get("/get_face")
async def get_name(req: Request):
    req = await req.json()
    image = pickle.loads(jsonpickle.decode(req["image"]))
    owner = req["owner"]
    all_faces = database.get_all_faces(Faces, [owner])
    mn = 0.1
    mn_index = -1
    result_names = []
    result_description = []
    embeddings = ident_model.predict(image.to(torch.device("cuda"))).detach().cpu().numpy()
    for embedding in embeddings:
        for s in range(0, len(all_faces)):
            float_list = json.loads(all_faces[s].embedding.tobytes())
            arr = np.array(float_list, dtype=np.float32)
            dist = cosine(embedding.flatten(), arr.flatten())*1000
            if dist < mn:
                mn = dist
                mn_index = s
        if mn_index == -1:
            result_names.append("Undetected")
            result_description.append("")
        else:
            result_names.append(all_faces[mn_index].fullname)
            result_description.append(all_faces[mn_index].description)
    return JSONResponse(content={"fullnames": result_names, "descriptions": result_description})

async def get_name_inter(image, owner):

    all_faces = database.get_all_faces(Faces, [owner])
    mn = 0.4
    mn_index = -1
    result_names = []
    result_description = []
    result_ages = []
    result_genders = []
    embeddings = ident_model.predict(image.to(torch.device("cuda"))).detach().cpu().numpy()
    embeddings = sklearn.preprocessing.normalize(embeddings)
    for embedding in embeddings:
        for s in range(0, len(all_faces)):
            float_list = json.loads(all_faces[s].embedding.tobytes())
            arr = np.array(float_list, dtype=np.float32)
            dist = cosine(embedding.flatten(), arr.flatten())*1000
            print(dist)
            if dist < mn:
                mn = dist
                mn_index = s
        if mn_index == -1:
            result_names.append("Undetected")
            result_description.append("")
        else:
            result_names.append(all_faces[mn_index].fullname)
            result_description.append(all_faces[mn_index].description)

    return result_names, result_description
@app.post("/send_video")
async def send_video(req: Request):
    req = await req.json()
    video = req["video"]
    model_type = req["model_type"]
    owner = req["owner"]
    await detect(model_type, video, owner)
    return JSONResponse(content={"status": "ok"})

@app.get("/check_useful_models")
def check_useful_models():
    return JSONResponse(content={'data': mtcnn.get_models()})

async def detect(model_type, video, owner):
    ids = {}
    frame_number = 0
    detect_model = Detector(model_type=model_type, device="cuda:0", image_size=1000, output_size=128)
    video = orjson.loads(jsonpickle.decode(video))
    for img0 in video:
        res= []
        ft = 0
        frame_number += 1
        img0 = cv2.cvtColor(np.array(img0).astype(np.uint8), cv2.COLOR_RGB2BGR)
        batch_boxes, cropped_images = detect_model.detect_with_extractor(img0)
        centers = []
        if cropped_images is not None:
            for s in range(len(cropped_images)):
                try:
                    centers.append(
                        (int(batch_boxes[s][0] + batch_boxes[s][2] / 2), int(batch_boxes[s][1] + batch_boxes[s][3] / 2)))
                except:
                    pass
            tracker.Update(np.array(centers))
            for s in range(len(cropped_images)):
                if tracker.tracks[s].track_id not in ids or frame_number%10==1:
                    if ft == 0:
                        res = []
                        ft = 1
                    res.append(cropped_images[s].numpy())


            if len(res) != 0:
                array = await get_name_inter(torch.Tensor(np.array(res)), owner)
                names, descrptions = array

                for i in range(len(tracker.tracks)):
                    try:
                        if tracker.tracks[i].track_id not in ids:
                            ids[tracker.tracks[i].track_id] = names[i]
                    except:
                        pass
            ls = list(ids.keys())
            c = 0
            for id in range(len(names)):
                try:
                    cv2.putText(img0, names[id], (int(batch_boxes[id][0]), int(batch_boxes[id][1]) - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 191, 0), 1)
                    cv2.rectangle(img0, (int(batch_boxes[id][0]), int(batch_boxes[id][1])),
                                  (int(batch_boxes[id][2]), int(batch_boxes[id][3])), (255, 191, 0), 2)
                    if names[id] == "Undetected":
                        continue
                    if mx < ls[id - 1]:
                        mx = ls[id - 1]
                        create_new_log(img0, names[id], descrptions[id], owner)
                except:
                    pass

    cv2.destroyAllWindows()



def create_new_log(image, name, description, owner):
    response = requests.post("http://localhost:8090/api/create_log", json={"device": device_name, "image": cv2.cvtColor(cv2.resize(image, (image.shape[0]//2, image.shape[1]//3)), cv2.COLOR_BGR2RGB).tolist(), "fullname": name, "description": description, 'owner': owner})
    return json.loads(response.text)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8070)