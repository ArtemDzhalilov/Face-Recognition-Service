# Face-Recognition-Service

The full-fledged service for face recognition

## Description

This repository contains 4 back-end components, front-end, api module, factial face recognition model training example, and face detection models testing examples.

## Getting Started

You need to have [python](https://www.python.org/downloads/) and [golang](https://go.dev/doc/install) installed.

### Install Dependencies

```bash
pip install requirements.txt
```

### Simple Run Service

First download [factial face recognition model weights](https://drive.google.com/drive/folders/1UTwpAS8PI2iR0bthEl2T0vDGnrwSVlwG?usp=sharing) and [detection models weights](https://drive.google.com/drive/folders/1zTo0a2ZYPqVxgdMlQ0EmnW1apPRSrbA_?usp=sharing) and put them into [./ML Component/model_weights](https://github.com/ArtemDzhalilov/Face-Recognition-Service/tree/main/ML_Component/model_weights). Next you need to setup Postgres database [in docker](https://hub.docker.com/_/postgres) or [locally](https://www.postgresql.org/download/) and enter your database authentication data into [Auth_Component/.env](https://github.com/ArtemDzhalilov/Face-Recognition-Service/tree/main/Auth_Component/.env); [Admin_Component/.env](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Admin_Component/.env); [Logs_Component/.env](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Log_Component/.env); [ML_component/env.py](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/ML_Component/env.py). Then run [Admin_Component/main.go](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Admin_Component/main.go); [Auth_Component/main.go](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Auth_Component/main.go); [Logs_Component/main.go](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Log_Component/log_server/main.go); [ML_Component/app.py](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/ML_Component/app.py) and [Front-end/index.py](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Front_end/index.py).

Next go to your browser to url [localhost:4444](http://localhost:4444).

## Models Testing

### Factial Face Recognition

First download [factial face recognition testing weights](https://drive.google.com/drive/folders/1UI_u4BqWgU-k5Y-DPuMJyZ2t8JIgUFZ6?usp=sharing) and put them into [Train_model/model](https://github.com/ArtemDzhalilov/Face-Recognition-Service/tree/main/Train_model/model). Next download [becnhmarks binary files](https://drive.google.com/drive/folders/1tmD0cjMSrtnFu-iqJiqFWnFKkl6hL2cu?usp=sharing) and put them into [Train_model/eval](https://github.com/ArtemDzhalilov/Face-Recognition-Service/tree/main/Train_model/eval).
```bash
python Train_model/test.py --model path/to/model/weights --target (name of target benchmark)
```

### Face Detection

Models' performances on WiderFace Hard benchamark can be found [here](https://github.com/Yusepp/YOLOv8-Face), [here](https://paperswithcode.com/paper/joint-face-detection-and-alignment-using) and [here](https://paperswithcode.com/paper/dsfd-dual-shot-face-detector). For model speed testing, download yolo  [weights](https://drive.google.com/drive/folders/1zTo0a2ZYPqVxgdMlQ0EmnW1apPRSrbA_?usp=sharing) (weights of other models were downloaded with this repo) and put them into [Detector_tests/Detector](https://github.com/ArtemDzhalilov/Face-Recognition-Service/tree/main/Detector_tests/Detector) and run [Detectors_test/compare.py](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Detector_tests/compare.py).

```bash
python ./Detector_tests/test_speed.py
```
## Factial Model Training

First dowload [ms1m-returnaface](https://drive.google.com/file/d/1JgmzL9OLTqDAZE86pBgETtSQL4USKTFy/view) and unzip it into [Train_model/Data](https://github.com/ArtemDzhalilov/Face-Recognition-Service/tree/main/Train_model/Data), then run [Train_model/train.py](https://github.com/ArtemDzhalilov/Face-Recognition-Service/blob/main/Train_model/train.py).

## API Usage

### Todo

## Todo

1. Finish desktop app.
   
2. Make API documentation.
   
3. Create another identification model with linear asymptotics using mamba insted of attetion (more details about mamba usage in vision tasks can be found [here](https://arxiv.org/abs/2401.09417) and [here](https://arxiv.org/abs/2401.10166)).
   
## License

This project is licensed under the AGPL-3.0 License - see the LICENSE.md file for details.

## Acknowledgments

[CoAtNet](https://github.com/chinhsuanwu/coatnet-pytorch)

[Meta Pseudo Labels](https://github.com/kekmodel/MPL-pytorch)

[Dual Shot Face Detector](https://github.com/hukkelas/DSFD-Pytorch-Inference)

[MTCNN](https://github.com/timesler/facenet-pytorch)

[Ultra Light Fast Generic Face Detector](https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB)

[Train and evaluation code](https://github.com/zhongyy/Face-Transformer)




