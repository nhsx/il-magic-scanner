import cv2
import numpy as np
from PIL import ImageDraw

def overlay_rect(pil_image, normalised_rect):
    output_width, output_height = pil_image.size[:2]
    x_min = int(normalised_rect['x'] * output_width)
    x_max = int(x_min + normalised_rect['width'] * output_width)
    y_min = int(normalised_rect['y'] * output_height)
    y_max = int(y_min + normalised_rect['height'] * output_height)

    draw = ImageDraw.Draw(pil_image)
    draw.rectangle([(x_min, y_min), (x_max, y_max)], fill=None, outline=(255,0,0), width=2)
    return pil_image

def overlay_rects(image, rects):
    for rect in rects:
        overlay_rect(image, rect)

def extract_subimage(pil_image, normalised_rect):
    pix_width, pix_height = pil_image.size[:2]
    x = normalised_rect['x'] * pix_width
    width = normalised_rect['width'] * pix_width
    y = normalised_rect['y'] * pix_height
    height = normalised_rect['height'] * pix_height

    return pil_image.crop((x,y,x+width,y+height))

def extract_subimages(pil_image, normalised_rects):
    return [extract_subimage(pil_image, r) for r in normalised_rects]

def pil_to_cv2(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGR2RGB)


class Image:
    def __init__(self, pil_image):
        self.raw = pil_image

    def to_cv2(self):
        return pil_to_cv2(self.raw)

    def overlay_rects(self, rects):
        overlay_rects(self.raw, rects)
        return self

    def extract_subimage(self, norm_rect):
        return Image(extract_subimage(self.raw, norm_rect))

    def resize(self, dims):
        return Image(self.raw.resize(dims))

    def save(self, filename):
        self.raw.save(filename)
        return self

