import os, argparse
import torch
import torch.nn as nn

from tensorboardX import SummaryWriter

from config import get_config
from image_iter import FaceDataset

from util.utils import get_val_data, perform_val, get_time, buffer_val, AverageMeter, train_accuracy
import time

from coatnet import CoAtNet
def need_save(acc, highest_acc):
    do_save = False
    save_cnt = 0
    if acc[0] > 0.98:
        do_save = True
    for i, accuracy in enumerate(acc):
        if accuracy > highest_acc[i]:
            highest_acc[i] = accuracy
            do_save = True
        if i > 0 and accuracy >=highest_acc[i]-0.002:
            save_cnt += 1
    if save_cnt >= len(acc)*3/4 and acc[0]>0.99:
        do_save = True
    print("highest_acc:", highest_acc)
    return do_save


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='for face verification')
    parser.add_argument("-w", "--workers_id", help="gpu ids or cpu", default='0', type=str)
    parser.add_argument("-e", "--epochs", help="training epochs", default=125, type=int)
    parser.add_argument("-b", "--batch_size", help="batch_size", default=16, type=int)
    parser.add_argument("-d", "--data_mode", help="use which database, [casia, vgg, ms1m, retina, ms1mr]",default='retina', type=str)
    parser.add_argument("-n", "--net", help="which network, ['VIT','VITs']",default='VITs', type=str)
    parser.add_argument("-head", "--head", help="head type, ['ArcFace', 'CosFace']", default='CosFace', type=str)
    parser.add_argument("-t", "--target", help="verification targets", default='lfw', type=str)
    parser.add_argument("-r", "--resume", help="resume model", default='', type=str)
    parser.add_argument('--outdir', help="output dir", default='./model', type=str)

    parser.add_argument('--opt', default="adamw", type=str, metavar='OPTIMIZER',
                        help='Optimizer (default: "adamw"')
    parser.add_argument('--opt-eps', default=1e-8, type=float, metavar='EPSILON',
                        help='Optimizer Epsilon (default: 1e-8)')
    parser.add_argument('--opt-betas', default=None, type=float, nargs='+', metavar='BETA',
                        help='Optimizer Betas (default: None, use opt default)')
    parser.add_argument('--momentum', type=float, default=0.9, metavar='M',
                        help='SGD momentum (default: 0.9)')
    parser.add_argument('--weight-decay', type=float, default=1e-2,
                        help='weight decay (default: 0.05)')
    parser.add_argument('--sched', default='cosine', type=str, metavar='SCHEDULER',
                        help='LR scheduler (default: "cosine"')
    parser.add_argument('--lr', type=float, default=5e-4, metavar='LR',
                        help='learning rate (default: 5e-4)')
    parser.add_argument('--lr-noise', type=float, nargs='+', default=None, metavar='pct, pct',
                        help='learning rate noise on/off epoch percentages')
    parser.add_argument('--lr-noise-pct', type=float, default=0.67, metavar='PERCENT',
                        help='learning rate noise limit percent (default: 0.67)')
    parser.add_argument('--lr-noise-std', type=float, default=1.0, metavar='STDDEV',
                        help='learning rate noise std-dev (default: 1.0)')
    parser.add_argument('--warmup-lr', type=float, default=1e-6, metavar='LR',
                        help='warmup learning rate (default: 1e-6)')
    parser.add_argument('--min-lr', type=float, default=1e-5, metavar='LR',
                        help='lower lr bound for cyclic schedulers that hit 0 (1e-5)')

    parser.add_argument('--decay-epochs', type=float, default=30, metavar='N',
                        help='epoch interval to decay LR')
    parser.add_argument('--warmup-epochs', type=int, default=3, metavar='N',
                        help='epochs to warmup LR, if scheduler supports')
    parser.add_argument('--cooldown-epochs', type=int, default=10, metavar='N',
                        help='epochs to cooldown LR at min_lr, after cyclic schedule ends')
    parser.add_argument('--patience-epochs', type=int, default=10, metavar='N',
                        help='patience epochs for Plateau LR scheduler (default: 10')
    parser.add_argument('--decay-rate', '--dr', type=float, default=0.1, metavar='RATE',
                        help='LR decay rate (default: 0.1)')
    args = parser.parse_args()

    cfg = get_config(args)

    SEED = cfg['SEED']
    torch.manual_seed(SEED)

    DATA_ROOT = cfg['DATA_ROOT']
    EVAL_PATH = "./eval"
    WORK_PATH = cfg['WORK_PATH']
    BACKBONE_RESUME_ROOT = cfg['BACKBONE_RESUME_ROOT']

    BACKBONE_NAME = cfg['BACKBONE_NAME']
    HEAD_NAME = cfg['HEAD_NAME']

    INPUT_SIZE = cfg['INPUT_SIZE']
    EMBEDDING_SIZE = 512
    BATCH_SIZE = cfg['BATCH_SIZE']
    NUM_EPOCH = cfg['NUM_EPOCH']

    DEVICE = "cuda"
    MULTI_GPU = cfg['MULTI_GPU']
    GPU_ID = cfg['GPU_ID']
    print('GPU_ID', GPU_ID)
    TARGET = cfg['TARGET']
    print("=" * 60)
    print("Overall Configurations:")
    print(cfg)
    with open(os.path.join(WORK_PATH, 'config.txt'), 'w') as f:
        f.write(str(cfg))
    print("=" * 60)

    writer = SummaryWriter(WORK_PATH)
    torch.backends.cudnn.benchmark = False

    with open(os.path.join(DATA_ROOT, 'property'), 'r') as f:
        NUM_CLASS, h, w = [int(i) for i in f.read().split(',')]
    assert h == INPUT_SIZE[0] and w == INPUT_SIZE[1]

    dataset = FaceDataset(os.path.join(DATA_ROOT, 'train.rec'), rand_mirror=True)
    trainloader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=len(GPU_ID), drop_last=True)

    print("Number of Training Classes: {}".format(NUM_CLASS))
    print(len(dataset))

    vers = get_val_data(EVAL_PATH, TARGET)
    highest_acc = [0.0 for t in TARGET]


    student = CoAtNet(num_classes=NUM_CLASS)
    teacher = CoAtNet(num_classes=NUM_CLASS)
    print("NUM_CLASS : " + str(NUM_CLASS))
    print("=" * 60)
    print(student)
    print("{} Models Generated".format(BACKBONE_NAME))
    print("=" * 60)

    LOSS = nn.CrossEntropyLoss()

    OPTIMIZER_S = torch.optim.SGD(student.parameters(), lr=3e-2, weight_decay=0.0005)
    OPTIMIZER_T = torch.optim.SGD(teacher.parameters(), lr=1.25e-1, weight_decay=0.0005)



    student = student.to(DEVICE)
    teacher = teacher.to(DEVICE)
    LOSS.to(DEVICE)

    DISP_FREQ = 10*(256//BATCH_SIZE)
    VER_FREQ = 20*(256//BATCH_SIZE)*10
    print(1)

    batch = 0

    losses = AverageMeter()

    student.train()
    teacher.train()
    for epoch in range(NUM_EPOCH):
        last_time = time.time()
        for inputs, labels in iter(trainloader):
            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE).long()



            t_outputs, _ = teacher(inputs.float(), labels)
            s_outputs, _ = student(inputs.float(), torch.argmax(t_outputs, dim=1))
            s_loss = LOSS(s_outputs, torch.argmax(t_outputs, dim=1))
            s_loss.backward()
            OPTIMIZER_S.step()

            s_outputs_new, _ = student(inputs.float(), labels)
            s_loss_new = LOSS(s_outputs_new, labels)
            OPTIMIZER_S.zero_grad()
            OPTIMIZER_T.zero_grad()
            s_loss_new.backward()
            OPTIMIZER_T.step()


            prec1 = train_accuracy(s_outputs, labels, topk=(1,))
            losses.update(s_loss.data.item(), inputs.size(0))
            if ((batch + 1) % DISP_FREQ == 0) and batch != 0:
                epoch_loss = losses.avg
                writer.add_scalar("Training/Training_Loss", epoch_loss, batch + 1)

                batch_time = time.time() - last_time
                last_time = time.time()

                print('Epoch {} Batch {}\t'
                      'Speed: {speed:.2f} samples/s\t'
                      'Training Loss {loss.val:.4f} ({loss.avg:.4f})\t'.format(
                    epoch + 1, batch + 1, speed=inputs.size(0) * DISP_FREQ / float(batch_time),
                    loss=losses))
                losses = AverageMeter()

            if ((batch + 1) % VER_FREQ == 0) and batch != 0:
                student.eval()
                for params in OPTIMIZER_S.param_groups:
                    lr = params['lr']
                    break
                print("Learning rate %f"%lr)
                print("Perform Evaluation on", TARGET, ", and Save Checkpoints...")
                acc = []
                for ver in vers:
                    name, data_set, issame = ver
                    accuracy, std, xnorm, best_threshold, roc_curve = perform_val(MULTI_GPU, DEVICE, EMBEDDING_SIZE, BATCH_SIZE, student, data_set, issame)
                    buffer_val(writer, name, accuracy, std, xnorm, best_threshold, roc_curve, batch + 1)
                    print('[%s][%d]XNorm: %1.5f' % (name, batch+1, xnorm))
                    print('[%s][%d]Accuracy-Flip: %1.5f+-%1.5f' % (name, batch+1, accuracy, std))
                    print('[%s][%d]Best-Threshold: %1.5f' % (name, batch+1, best_threshold))
                    acc.append(accuracy)

                if need_save(acc, highest_acc):
                    if MULTI_GPU:
                        torch.save(student.module.state_dict(), os.path.join(WORK_PATH, "Backbone_{}_Epoch_{}_Batch_{}_Time_{}_checkpoint.pth".format(BACKBONE_NAME, epoch + 1, batch + 1, get_time())))
                    else:
                        torch.save(student.state_dict(), os.path.join(WORK_PATH, "Backbone_accuracy_{}_epochs{}_batch_{}_checkpoint.pth".format(acc, epoch+1, batch+1)))
                student.train()

            batch += 1