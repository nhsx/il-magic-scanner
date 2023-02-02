import random
import cv2
from matplotlib import pyplot as plt
import sys
import json
from pathlib import Path
import sqlite3

import albumentations as A

transform = A.Compose([
    A.ShiftScaleRotate(shift_limit=0.0625,
                       scale_limit=0.5,
                       rotate_limit=10,
                       border_mode=cv2.BORDER_CONSTANT, value=(128,128,128),
                       p=0.75),
    A.GaussNoise(),
    A.Blur(blur_limit=3),
    A.OneOf([
        A.OpticalDistortion(p=0.3),
        A.GridDistortion(p=0.1),
    ], p=0.2),
    A.OneOf([
        A.CLAHE(),
        A.RandomBrightnessContrast(0.5)
    ], p=0.3),
    A.HueSaturationValue(p=0.3)
], bbox_params=A.BboxParams(format='coco', min_visibility=0.9, label_fields=['class_labels']))


def add_bbox(img, bbox):
    x_min, y_min, w, h = bbox
    x_min, x_max, y_min, y_max = int(x_min), int(x_min + w), int(y_min), int(y_min + h)
    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color=(255,0,0), thickness=1)
    return img

def visualize(transformed):
    image = transformed['image']
    print(transformed)
    for bbox in transformed['bboxes']:
        add_bbox(image, bbox)
    plt.figure(figsize=(10,10))
    plt.axis('off')
    return plt.imshow(image)

def read_file(filename):
    image = cv2.imread(str(filename))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def read_rects(filename):
    with open(filename) as f:
        return json.loads(f.read())


def augment(image, rects):
    class_labels = rects.keys()
    # coco format wants the rect to be handed in as a list, not as a dict
    bboxes = [
        [rects[t]['x'],
         rects[t]['y'],
         rects[t]['width'],
         rects[t]['height']]
        for t in class_labels
    ]
    return transform(image=image, bboxes=bboxes, class_labels=class_labels)

def wait(plot):
    return plt.waitforbuttonpress()

def generate_augment(img_filename, rect_filename):
    image = read_file(img_filename)
    rects = read_rects(rect_filename)
    return augment(image, rects)

def save_image(img_path, augmented):
    cv2.imwrite(str(img_path),
                cv2.cvtColor(augmented['image'], cv2.COLOR_RGB2BGR))

def save_rects(rects_path, augmented):
    class_labels = augmented['class_labels']
    bboxes = {}
    for i in range(len(class_labels)):
        class_label = class_labels[i]
        x, y, width, height = augmented['bboxes'][i]
        bboxes[class_label] = {'x': x, 'y': y, 'width': width, 'height': height}
    rects_path.write_text(json.dumps(bboxes))


def main()
    for set_name in range(1,6): # generate 5 datasets (in case one isn't enough)
        screenshots_path = Path('screenshots')
        augments_path = Path('augments') / str(set_name)
        augments_path.mkdir(parents=True, exist_ok=True)

        con = sqlite3.connect('samples.db')
        cur = con.cursor()
        for (id,) in cur.execute('SELECT id FROM samples'):
            out_img_path = augments_path / f"{id}.png"
            out_rect_path = augments_path / f"{id}.rect.json"
            if not (out_img_path.exists() and out_rect_path.exists()):
                print("Augmenting ", set_name, id)
                in_img_path = screenshots_path / f"{id}.png"
                in_rect_path = screenshots_path / f"{id}.rect.json"
                image = read_file(in_img_path)
                rects = read_rects(in_rect_path)
                done = False
                while not done:
                    augmented = augment(image, rects)
                    # Reject anything that doesn't give us both bboxes we're looking for
                    # We're fine saying "just scan it again"
                    done = len(augmented['bboxes']) == len(rects)
                    save_image(out_img_path, augmented)
                    save_rects(out_rect_path, augmented)

if __name__=="__main__":
    main()
