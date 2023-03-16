"""
prepare_data.py script is used to process original images and create training, validation, and test subsets.
The output depends from image_size and stretch parameters, so the script should be executed initially and
after changing those two parameters.
"""
from settings import *
import numpy as np
import cv2 as cv
import random


def square_resize_image(img_input):
    img_out = img_input
    if not stretch:
        w, h = img_out.shape[1], img_out.shape[0]
        top, bottom, left, right = 0, 0, 0, 0
        if w >= h:
            top = (w - h) // 2
            bottom = (w - h) - top
        else:
            left = (h - w) // 2
            right = (h - w) - left
        img_out = cv.copyMakeBorder(img_out, top, bottom, left, right, cv.BORDER_CONSTANT, value=(0, 0, 0))
    img_out = cv.resize(img_out, (image_size, image_size), interpolation=cv.INTER_AREA)
    return img_out


copy_to_test_orig = False

classes = [fname for fname in os.listdir(original_data_folder)]
print(len(classes), classes)

for cls in classes:
    cls_folder = os.path.join(original_data_folder, cls)
    files = [fname for fname in os.listdir(cls_folder)]
    train_images = []
    val_images = []
    test_images = []
    for i in range(len(files)):
        fname = files[i]
        ext = ''
        idx = fname.rfind('.')
        if idx > 0:
            ext = fname[idx+1:].lower()
        if ext in ['jpg', 'png', 'jpeg', 'tif', 'tiff']:
            fold = i % len(subset_distribution)
            if subset_distribution[fold].upper() == 'T':
                train_images.append(fname)
            elif subset_distribution[fold].upper() == 'V':
                val_images.append(fname)
            else:
                test_images.append(fname)

    print(len(train_images), len(val_images), len(test_images), cls)

    train_cls_folder = os.path.join(train_folder, cls)
    if not os.path.exists(train_cls_folder):
        os.makedirs(train_cls_folder)
    val_cls_folder = os.path.join(val_folder, cls)
    if not os.path.exists(val_cls_folder):
        os.makedirs(val_cls_folder)
    test_cls_folder = os.path.join(test_folder, cls)
    if not os.path.exists(test_cls_folder):
        os.makedirs(test_cls_folder)

    if copy_to_test_orig:
        test_orig_folder = os.path.join(data_folder, 'test_original')
        if not os.path.exists(test_orig_folder):
            os.makedirs(test_orig_folder)
        test_orig_cls_folder = os.path.join(test_orig_folder, cls)
        if not os.path.exists(test_orig_cls_folder):
            os.makedirs(test_orig_cls_folder)

    for fname in train_images:
        fpath = os.path.join(cls_folder, fname)
        img = cv.imread(fpath)
        img = square_resize_image(img)
        cv.imwrite(os.path.join(train_cls_folder, fname[:-4] + '.jpg'), img)

    for fname in val_images:
        fpath = os.path.join(cls_folder, fname)
        img = cv.imread(fpath)
        img = square_resize_image(img)
        cv.imwrite(os.path.join(val_cls_folder, fname[:-4] + '.jpg'), img)

    for fname in test_images:
        fpath = os.path.join(cls_folder, fname)
        img = cv.imread(fpath)
        img = square_resize_image(img)
        cv.imwrite(os.path.join(test_cls_folder, fname[:-4] + '.jpg'), img)

        if copy_to_test_orig:
            fpath_test = os.path.join(test_orig_cls_folder, fname)
            shutil.copyfile(fpath, fpath_test)

