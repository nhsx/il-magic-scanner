from tesserocr import PyTessBaseAPI
from PIL import Image, ImageOps, ImageEnhance
from string import digits

class FastOcr:
    def __init__(self):
        self.name_tesseract = PyTessBaseAPI()
        self.number_tesseract = PyTessBaseAPI()
        self.number_tesseract.SetVariable("tessedit_char_whitelist", digits)

    def _read_file(self, tess, image_filename):
        in_image = Image.open(image_filename)
        stretched_image = ImageOps.autocontrast(in_image, 2) # chop 2% outliers off light and dark
        inverted_image = ImageOps.invert(stretched_image) # light background please
        black_and_white_image = inverted_image.convert('1', dither=Image.NONE)
        black_and_white_image.save(image_filename)

        tess.SetImage(black_and_white_image)
        return tess.GetUTF8Text().strip()

    async def read_name(self, image_filename):
        return self._read_file(self.name_tesseract, image_filename)

    async def read_number(self, image_filename):
        return self._read_file(self.number_tesseract, image_filename)
