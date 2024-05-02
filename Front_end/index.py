import base64
import os
import tempfile
import time
import orjson
import imageio.v3 as iio
import cv2
import numpy as np
import pywebio
import torch
from pywebio.platform.tornado_http import start_server
from pywebio.input import *
from pywebio.output import put_html, put_text, put_buttons, put_image
import requests
from PIL import Image
import matplotlib.pyplot as plt
import io
import numpy
from functools import partial
import hashlib

login, password = '', ''
from pywebio.input import input, PASSWORD
from pywebio.output import put_text, put_buttons, put_html, popup
from pywebio.session import run_js, hold
import requests
import socket


def hashing_elem(elem):
    salt = 'devatdvasem'
    dataBase_password = elem + salt
    hashed = hashlib.md5(dataBase_password.encode()).hexdigest()
    return hashed

def auth_l():
    global login, password


    # Display the custom HTML with dark theme styles
    put_html("Please log in:<br>If you don't have an account, please register:")
    put_buttons(['Register'], onclick=lambda x: run_js(
        'window.location.replace("http://localhost:2305/?app=auth_r");'))

    # Input fields for login
    login_group = input_group("Login", [
        input("Enter your username:", name="login", required=True),
        input("Enter your password:", name="password", type=PASSWORD, required=True),

    ])
    login1, password1 = login_group["login"], hashing_elem(login_group["password"])

    # Construct the data for the POST request
    data = {
        'login': login1,
        'password': password1,
        "ip": socket.gethostbyname(socket.gethostname())
    }

    # Make the POST request to the login API
    resp = requests.post('http://localhost:8010/api/login/', json=data)

    # Check the response from the server
    if resp.status_code == 200:
        login = login1
        password = password1
        # Inform the user of a successful login
        put_text("Login successful!")
        run_js('window.location.replace("http://10.82.107.96:2305/?app=app");')
    else:
        # Inform the user that the login failed
        popup("Login failed", 'Please check your username and password and try again.')

    hold()

# This function should be called within a PyWebIO application context
# For example, use start_server(auth_l, port=2305) to start the app
def auth_r():
    global login, password
    put_text("Please register:")
    put_text("If you already have an account, please log in:")
    put_buttons(["Login"],
                onclick=[partial(pywebio.session.run_js,
                                 'window.location.replace("http://10.82.107.96:2305/?app=auth_l");')])
    login1 = input("Enter your username:")
    password1 = input("Enter your password:", type=PASSWORD)

    password1 = hashing_elem(password1)
    data = {
        'login': login1,
        'password': password1,
        'ip': socket.gethostbyname(socket.gethostname()),

    }
    resp = requests.post('http://localhost:8010/api/register/', json=data)
    print(resp.status_code)
    if resp.status_code == 200:
        login = login1
        password = password1
        put_text("Registration successful!")
        pywebio.session.run_js('window.location.replace("http://10.82.107.96:2305/?app=app");')
    else:
        put_text("Registration failed!")
    hold()

def fetch_data(owner):
    data = {
        'owner': owner
    }
    data1 = {
        'login': owner,
        'password': password
    }
    try:

        devices = requests.post('http://localhost:8080/api/get_devices/', json=data).json()
        faces = requests.post('http://localhost:8080/api/get_faces/', json=data).json()
        logs = requests.post('http://localhost:8090/api/get_logs/', json=data).json()
        model_types = requests.get('http://localhost:8070/check_useful_models/').json()
        api_key = requests.get('http://localhost:8927/get_api_key', json=data1).json()

        return devices, faces, logs, model_types, api_key
    except Exception as e:
        return {"data": []}, {"data": []}, {"data": []}, {"data": []}, {"data": ''}
def check_auto_login():
    if login == '' and password == '':
        return False
    else:
        try:
            res = requests.post('http://localhost:8010/api/login/', json={'login': login, 'password': password, 'ip': socket.gethostbyname(socket.gethostname())})
            if res.status_code == 200:
                return True
            else:
                return False
        except:
            return False




def app():
    if not check_auto_login():
        pywebio.session.run_js('window.location.replace("http://10.82.107.96:2305/?app=auth_l");')

    devices, faces, logs, models, api = fetch_data(login)

    put_html("<h2>API key</h2>")
    put_text(f"API key: {api['api_key']}")
    put_buttons(['Create'], onclick=[partial(create_api_key)])

    put_html("<h2>Devices</h2>")
    put_buttons(['Create'], onclick=[partial(create_device, login)])
    for device in devices["data"]:
        put_text(f"Device Name: {device['name']}")
        put_buttons(['Modify', 'Delete'], onclick=[partial(modify_device, device['name'], login), partial(delete_device, device['name'], login)])

    put_html("<h2>User Faces</h2>")
    put_buttons(['Create'], onclick=[partial(create_face, login)])
    for face in faces["data"]:
        put_text(f"User Face: {face['fullname']}, Description: {face['description']}")
        numpy_img = numpy.array(face['image'])
        if face['image'] == []:
            continue
        img = numpy_img.astype(numpy.uint8)
        img = Image.fromarray(img)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        put_image(img, width="112px", height="112px", format="png")
        put_text("")
        put_buttons(['Modify', 'Delete'], onclick=[partial(modify_face, face, login), partial(delete_face, face, login)])

    put_html("<h2>Logs</h2>")
    put_buttons(['Clear'], onclick=[partial(clear_logs, login)])
    for log in logs["data"]:
        if log['image']==[]:
            continue

        numpy_img = numpy.array(log['image'])

        numpy_img = numpy_img.astype(numpy.uint8)
        # Convert numpy array to PIL image
        img = Image.fromarray(numpy_img)

        # Create a BytesIO object
        img_byte_arr = io.BytesIO()

        # Save PIL image to byte array
        img.save(img_byte_arr, format='PNG')

        put_text(f"Log: {log['fullname']}, Description: {log['description']}, Device: {log['device']}")
        T = log['enter_time'].find('T')
        rdot = log['enter_time'].rfind('.')
        put_text(f"Enter Date: {log['enter_time'][:T]}")
        put_text(f"Enter Time: {log['enter_time'][T+1:rdot]}")
        put_text('Predicted Age: ' + str(log['age']))
        put_text('Predicted Gender: ' + log['gender'])
        put_buttons(["Delete"], onclick=[partial(delete_log, log, login)])
        put_image(img, width="112px", height="112px", format="png")

    put_text("Video input:")
    video_group = input_group("Video input", [
        file_upload("Upload video", name='video', accept='video/*', max_size='3000M'),
    ])
    model_type = select("Select model type", options=models['data'])
    put_buttons(["Send"], onclick=[partial(send_video, login, video_group['video']['content'], model_type)])

def create_api_key():
    json_data = {
        'login': login,
        'password': password
    }
    resp = requests.post('http://localhost:8927/create_api_key', json=json_data)
    if resp.status_code == 200:
        put_text("API key successfully created")
    else:
        put_text("Failed to create API key")

def send_video(user_name, video, model_type):
    frames = iio.imread(video, index=None, format_hint=".mp4")
    st = time.time()
    frames_new = np.array([cv2.resize(frames[frame], (frames.shape[1]//2, frames.shape[2]//2)) for frame in range(0, len(frames), 3)])
    serializes = orjson.dumps(frames_new, option=orjson.OPT_SERIALIZE_NUMPY)
    data = {
        'owner': user_name,
        'video': serializes,
        'model_type': model_type
    }
    resp = requests.post('http://localhost:8070/send_video', json=data)
    if resp.status_code == 200:
        put_text("Video processing is ready, refresh the page to see the result")
    else:
        put_text("Video processing failed, try again")


def modify_device(device_name, user_name):
    device_details = input_group("Enter new device details", [
        input("Enter new device name", name='name'),
    ])
    json_data = {
        'owner': user_name,
        'name': device_details['name'],
        'old_name': device_name
    }

    response = requests.put('http://localhost:8080/api/update_device/', json=json_data)
    if response.status_code == 200:
        put_text('Device successfully modified')
    else:
        put_text('Failed to modify device')


def delete_device(device, user_name):
    device_sure = input_group("Are you sure you want to delete this device?", [
        input(f"Enter device name, to confirm (current device name: {device})", name='name'),
    ])
    json_data = {
        'owner': user_name,
        'name': device
    }
    if device_sure["name"] == device:
        response = requests.delete('http://localhost:8080/api/delete_device/', json=json_data)
        if response.status_code == 200:
            put_text('Device successfully deleted')
        else:
            put_text('Failed to delete device')
    else:
        put_text('Device name did not match')

def modify_face(face, user_name):
    device_details = input_group("Enter new face details", [
        input("Enter new fullname", name='fullname'),
        input("Enter new description", name='description'),
        file_upload("Upload new image", name='image', accept='image/*'),
    ])
    if device_details["image"] is None:
        put_text("No image was uploaded")
        return
    if device_details["fullname"] == face["fullname"] and device_details["description"] == face["description"]:
        put_text("No changes were made")
        return
    if device_details["fullname"] == '' or device_details["description"] == '':
        put_text("Fullname and description cannot be empty")
        return
    uploaded_file = device_details["image"]["content"]
    image = Image.open(io.BytesIO(uploaded_file))
    arr = numpy.array(image)
    json_data = {
        "fullname": device_details["fullname"],
        "description": device_details["description"],
        "image": arr.tolist(),
        "owner": user_name,
        "old_fullname": face["fullname"],
        "old_description": face["description"],
    }
    response = requests.put('http://localhost:8080/api/update_face/', json=json_data)
    if response.status_code == 200:
        put_text('Face successfully modified')
    else:
        put_text('Failed to modify face')

def delete_face(face, user_name):
    face_sure = input_group("Are you sure you want to delete this face?", [
        input(f"Enter face name, to confirm (current face name: {face['fullname']})", name='name'),
    ])
    json_data = {
        'owner': user_name,
        'fullname': face["fullname"],
        "description": face["description"],
    }
    if face_sure["name"] == face["fullname"]:
        response = requests.delete('http://localhost:8080/api/delete_face/', json=json_data)
        if response.status_code == 200:
            put_text('Face successfully deleted')
        else:
            put_text('Failed to delete face')
    else:
        put_text('Face name did not match')
def create_device(user_name):
    device_details = input_group("Enter device details", [
        input("Enter device name", name='name'),
    ])
    device_details["owner"] = user_name

    response = requests.post('http://localhost:8080/api/create_device/', json=device_details)
    if response.status_code == 200:
        put_text('Device successfully created')
    else:
        put_text('Failed to create device')

def create_face(user_name):
    face_details = input_group("Enter face details", [
        input("Enter fullname", name='fullname'),
        input("Enter description", name='description'),
        file_upload("Upload image", name='image', accept='image/*'),
    ])
    uploaded_file = face_details["image"]["content"]
    image = Image.open(io.BytesIO(uploaded_file))
    arr = numpy.array(image)
    json_data = {
        "fullname": face_details["fullname"],
        "description": face_details["description"],
        "image": arr.tolist(),
        "owner": user_name
    }


    response = requests.post('http://localhost:8080/api/create_face/', json=json_data)
    if response.status_code == 200:
        put_text('Face successfully created')
    else:
        put_text('Failed to create device')
def delete_log(log, user_name):
    json_data = {
        'owner': user_name,
        'fullname': log['fullname'],
        'description': log['description'],
        'image': log['image'],
        'enter_time': log['enter_time'],
    }
    response = requests.delete('http://localhost:8090/api/delete_log/', json=json_data)
    if response.status_code == 200:
        put_text('Log successfully deleted')
    else:
        put_text('Failed to delete log')
def clear_logs(user_name):
    json_data = {
        'owner': user_name,
    }
    response = requests.delete('http://localhost:8090/api/delete_logs/', json=json_data)
    if response.status_code == 200:
        put_text('Logs successfully cleaned')
    else:
        put_text('Failed to clean logs')



if __name__ == "__main__":

    start_server({"app": app, "auth_l": auth_l, "auth_r": auth_r}, port=2305, max_payload_size="40000M", host='localhost')
