import asyncio
from .fastocr import FastOcr

class CliOcr:
    async def _ocr_image(self, image_filename, tesseract_command):
        mogrify_command = f"mogrify -auto-level -unsharp 5 -wavelet-denoise 25% -threshold 50% -negate {image_filename}" 
        command = f"{mogrify_command} && {tesseract_command}"
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stdout:
            return stdout.decode().strip()

    def read_name(self, image_filename):
        tesseract_command = f"tesseract {image_filename} stdout -c tessedit_do_invert=1 --dpi 76 --psm 7" 
        return self._ocr_image(image_filename, tesseract_command)

    def read_number(self, image_filename):
        tesseract_command = f"tesseract {image_filename} stdout -c tessedit_do_invert=1 --dpi 76 digits" 
        return self._ocr_image(image_filename,tesseract_command)


async def run_tests():
    print("loaded, starting")
    cli_ocr = CliOcr()
    name, number = await asyncio.gather(cli_ocr.read_name("fakes/name.jpg"), cli_ocr.read_name("fakes/number.jpg"))
    print(name, number)

    fast_ocr = FastOcr()
    new_name = fast_ocr.read_name("fakes/name.jpg")
    new_number = fast_ocr.read_number("fakes/number.jpg")
    print(new_name, new_number)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())
