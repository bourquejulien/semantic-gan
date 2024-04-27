#!/usr/bin/env python

import os

import numpy as np
import scipy.misc
import chainer
import imageio

import utils


class DatasetMixin(chainer.dataset.DatasetMixin):

    label_names = None
    mean_bgr = None

    def label_rgb_to_32sc1(self, label_rgb):
        assert label_rgb.dtype == np.uint8
        label = np.zeros(label_rgb.shape[:2], dtype=np.int32)
        label.fill(-1)
        cmap = utils.labelcolormap(len(self.label_names))
        cmap = (cmap * 255).astype(np.uint8)
        for l, rgb in enumerate(cmap):
            mask = np.all(label_rgb == rgb, axis=-1)
            label[mask] = l
        return label

    def img_to_datum(self, img):
        img = img.copy()
        datum = img.astype(np.float32)
        datum = datum[:, :, ::-1]  # RGB -> BGR
        datum -= self.mean_bgr
        datum = datum.transpose((2, 0, 1))
        return datum

    def datum_to_img(self, datum):
        datum = datum.copy()
        bgr = datum.transpose((1, 2, 0))
        bgr += self.mean_bgr
        rgb = bgr[:, :, ::-1]  # BGR -> RGB
        rgb = rgb.astype(np.uint8)
        return rgb


class PascalVOC2012Dataset(DatasetMixin):

    label_names = np.array([
        'background',
        'aeroplane',
        'bicycle',
        'bird',
        'boat',
        'bottle',
        'bus',
        'car',
        'cat',
        'chair',
        'cow',
        'diningtable',
        'dog',
        'horse',
        'motorbike',
        'person',
        'potted plant',
        'sheep',
        'sofa',
        'train',
        'tv/monitor',
    ])
    mean_bgr = np.array([104.00698793, 116.66876762, 122.67891434])

    def __init__(self, data_type):
        # get ids for the data_type
        dataset_dir = chainer.dataset.get_dataset_directory(
            'pascal/VOCdevkit/VOC2012')
        imgsets_file = os.path.join(
            dataset_dir,
            'ImageSets/Segmentation/{}.txt'.format(data_type))
        self.files = []
        for data_id in open(imgsets_file).readlines():
            data_id = data_id.strip()
            img_file = os.path.join(
                dataset_dir, 'JPEGImages/{}.jpg'.format(data_id))
            label_rgb_file = os.path.join(
                dataset_dir, 'SegmentationClass/{}.png'.format(data_id))
            self.files.append({
                'img': img_file,
                'label_rgb': label_rgb_file,
            })

    def __len__(self):
        return len(self.files)

    def get_example(self, i):
        data_file = self.files[i]
        # load image
        img_file = data_file['img']
        img = imageio.imread(img_file, mode='RGB')
        datum = self.img_to_datum(img)
        # load label
        label_rgb_file = data_file['label_rgb']
        label_rgb = imageio.imread(label_rgb_file, mode='RGB')
        label = self.label_rgb_to_32sc1(label_rgb)
        return datum, label
