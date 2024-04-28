import asyncio
import os
from typing import List

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QListWidget, QComboBox, QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, \
    QWidget, QLabel, QPlainTextEdit, QStackedWidget
import requests
import cv2
from PyQt6.QtWidgets import QHBoxLayout

import cv2
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def run(self):
        print("start")
        cap = cv2.VideoCapture(-1)
        while True:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.change_pixmap_signal.emit(qt_image)
class LogThread(QThread):
    append_log_signal = pyqtSignal(list)

    def run(self):
        while True:
            logs = requests.post("http://127.0.0.1:8090/api/get_logs_by_device", json={"owner": owner, "device_name": device_name}).json()['data']
            self.append_log_signal.emit(logs)
            self.sleep(1)

owner = ''
device_name = ''
model_name = 'mtcnn'

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Login')  # Set window title
        self.setStyleSheet('background-color: white;')  # Set window background color
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Login')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.submit_button = QPushButton("Submit")

        # Add a style to the submit button
        self.submit_button.setStyleSheet('''
            background-color: #007BFF;
            color: white;
            border-radius: 10px;
            padding: 6px;
            font-size: 15px;
            ''')
        self.submit_button.clicked.connect(self.login)

        registration_label = QLabel('Please, <a href="http://192.168.88.24:2305/?app=auth_r">register</a> if you do not have an account.')
        registration_label.setOpenExternalLinks(True)

        layout = QVBoxLayout()
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(registration_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def login(self):
        global owner
        login = self.login_input.text()
        password = self.password_input.text()
        print(login, password)
        resp = requests.post("http://127.0.0.1:8010/api/login", json={"login": login, "password": password})
        print(resp.status_code)
        if resp.status_code == 200:
            owner = login
            main_window.run()
            widget.setCurrentWidget(main_window)
        else:
            print("Login failed")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


    def detect(self, cam):
        model_name = self.model_name_box.currentText()
        model_name = model_name.split('(')[0][:-1]
        device_name = self.device_name_box.currentText()
        show_window.setup()
        widget.setCurrentWidget(show_window)
        show_window.run()
        asyncio.run(self.start_detection(cam, model_name, device_name))
    def run(self):
        self.start_button = QPushButton("Start detection")
        self.start_button.clicked.connect(self.detect)
        self.device_name_box = QComboBox()
        self.devices = requests.post("http://127.0.0.1:8080/api/get_devices", json={"owner": owner}).json()['data']
        self.models = ["DSFD (bigger, better and slower)", "mtcnn (middle)", "ULFD (smaller, worse and faster)"]
        self.device_name_box.addItems([device['name'] for device in self.devices])
        self.model_name_box = QComboBox()
        self.model_name_box.addItems(self.models)
        self.start_button.setStyleSheet('''
                            QPushButton {
                                background-color: #007BFF;
                                color: white;
                                border-radius: 10px;
                                padding: 6px;
                                font-size: 15px;
                            }
                        ''')
        layout = QVBoxLayout()
        layout.addWidget(self.device_name_box)
        layout.addWidget(self.model_name_box)
        layout.addWidget(self.start_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    async def start_detection(self, cam, model_name, device_name):
        cam = 0
        os.environ["CAM"] = str(cam)
        os.environ["MODEL_NAME"] = model_name
        os.environ["DEVICE_NAME"] = device_name
        os.system(f'python C:/Users/User/Desktop/folders/desktop_app_ffr/ffr.py')

class ShowWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def update_image(self, qt_image):
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def append_log(self, log_text):
        self.log_widget.clear()
        self.log_widget.addItems(log_text)

    def close(self):
        os.system("pkill -f ffr.py")
        self.video_thread.quit()
        self.log_thread.quit()
        widget.setCurrentWidget(main_window)

    def run(self):


        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_image)

        self.log_thread = LogThread()
        self.log_thread.append_log_signal.connect(self.append_log)
        self.video_thread.start()
        self.log_thread.start()

    def setup(self):
        self.owner = owner
        self.device_name = device_name
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.close)

        self.video_label = QLabel(self)
        self.log_widget = QComboBox(self)
        logs = requests.post("http://127.0.0.1:8090/api/get_logs_by_device",
                             json={"owner": owner, "device_name": device_name}).json()['data']
        self.log_widget.addItems(logs)

        layout = QVBoxLayout()
        subLayout = QHBoxLayout()
        subLayout.addWidget(self.video_label)
        subLayout.addWidget(self.log_widget)
        layout.addLayout(subLayout)
        self.container = QWidget()
        self.container.setLayout(layout)
        self.setCentralWidget(self.container)


app = QApplication([])
widget = QStackedWidget()
login_window = LoginWindow()
widget.addWidget(login_window)

main_window = MainWindow()
widget.addWidget(main_window)
show_window = ShowWindow()
widget.addWidget(show_window)
widget.setCurrentWidget(login_window)

widget.show()

app.exec()
