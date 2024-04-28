import torch
import torch.nn as nn
import sys
from coatnet import CoAtNet
from util.utils import get_val_data, perform_val
from IPython import embed
import sklearn
import cv2
import numpy as np
from image_iter import FaceDataset
import torch.utils.data as data
import argparse
import os

def main(args):
    MULTI_GPU = False
    DEVICE = torch.device("cuda:0")
    DATA_ROOT = './Data/'
    with open(os.path.join(DATA_ROOT, 'property'), 'r') as f:
        NUM_CLASS, h, w = [int(i) for i in f.read().split(',')]

    model = CoAtNet(num_classes=NUM_CLASS)
    model.load_state_dict(torch.load(args.model), strict=False)
    model.to(DEVICE)
    model.eval()


    #debug

    #embed()
    TARGET = [i for i in args.target.split(',')]
    vers = get_val_data('./eval/', TARGET)
    acc = []

    for ver in vers:
        name, data_set, issame = ver
        accuracy, std, xnorm, best_threshold, roc_curve, accuracy1 = perform_val(MULTI_GPU, DEVICE, 512, args.batch_size,
                                                                      model, data_set, issame)
        print('[%s]XNorm: %1.5f' % (name, xnorm))
        print('[%s]Accuracy-Flip: %1.5f+-%1.5f' % (name, accuracy, std))
        print('[%s]Best-Threshold: %1.5f' % (name, best_threshold))
        acc.append(accuracy)
        print(accuracy1)
    print('Average-Accuracy: %1.5f' % (np.mean(acc)))

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='', help='training set directory')
    parser.add_argument('--target', default='lfw',
                        help='')
    parser.add_argument('--batch_size', type=int, help='', default=20)
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))