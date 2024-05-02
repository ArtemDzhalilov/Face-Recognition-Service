import fastapi
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
app = fastapi.FastAPI()
from db import Database
from env import *

database = Database(f"postgresql+psycopg2://{LOGIN}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}")
async def get_login_password(req: Request):
    req = await req.json()
    api_key = req["api_key"]
    login, password = database.get_login_password(api_key)
    if login is None:
        return JSONResponse(status_code=401, content={"login": None, "password": None, 'message': 'Wrong API key'})
    return JSONResponse(content={"login": login, "password": password, 'message': 'Success'})

@app.post("/create_api_key")
async def create_ip_key(req: Request):
    req = await req.json()
    login = req["login"]
    password = req["password"]
    api_key = database.create_ip_key(login, password)
    if api_key is None:
        return JSONResponse(status_code=401, content={"message": "Wrong login or password"})
    return JSONResponse(status_code=200, content={"api_key": api_key})
@app.get("/get_api_key")
async def get_api_key(req: Request):
    req = await req.json()
    login = req["login"]
    password = req["password"]
    api_key = database.get_api_key(login, password)
    if api_key is None:
        return JSONResponse(status_code=401, content={"message": "Wrong login or password"})
    return JSONResponse(status_code=200, content={"api_key": api_key})

@app.get("/api_send_video")
async def api_send_video(req: Request):
    req = await req.json()
    video = req["video"]
    model_type = req["model_type"]
    api_key = req["api_key"]
    owner, _ = get_login_password(api_key)
    res = requests.post("http://localhost:8070/send_video", json={"video": video, "model_type": model_type, "owner": owner})
    if res.status_code != 200:
        return JSONResponse(content={"status": "error"}, status_code=500)
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.get("/api_get_embedding")
async def api_get_embedding(req: Request):
    req = await req.json()
    image = req["image"]
    api_key = req["api_key"]
    owner, _ = get_login_password(api_key)
    if owner is None:
        return JSONResponse(content={"status": "api key is wrong"}, status_code=401)
    res = requests.post("http://localhost:8070/get_embedding", json={"image": image})
    if res.status_code != 200:
        return JSONResponse(content={"status": "error"}, status_code=500)
    return JSONResponse(content=res.json(), status_code=200)
@app.get("/api_get_name")
async def api_get_name(req: Request):
    req = await req.json()
    image = req["image"]
    api_key = req["api_key"]
    owner, _ = get_login_password(api_key)
    if owner is None:
        return JSONResponse(content={"status": "api key is wrong"}, status_code=401)
    res = requests.post("http://localhost:8070/get_name", json={"image": image, "owner": owner})
    if res.status_code != 200:
        return JSONResponse(content={"status": "error"}, status_code=500)
    return JSONResponse(content=res.json(), status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8927)


