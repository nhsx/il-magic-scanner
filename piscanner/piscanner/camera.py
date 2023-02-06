from picamera2 import Picamera2
from libcamera import Transform
from PIL import Image

class Camera:
    @classmethod
    def fake(cls, filename):
        return FakeCamera(filename)

    def __init__(self):
        self.picam2 = Picamera2()
        transform = Transform(hflip=True, vflip=True)
        config = self.picam2.create_still_configuration({"size": (3280, 2464)}, 
                queue=False, 
                transform=transform)
        self.picam2.align_configuration(config)
        self.picam2.configure(config)
        self.picam2.start()

    def take_pil_image(self):
        return self.picam2.capture_image("main")

class FakeCamera:
    def __init__(self, filename):
        self.filename = filename

    def take_pil_image(self):
        return Image.open(self.filename)

