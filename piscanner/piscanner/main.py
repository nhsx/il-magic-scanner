#!/usr/bin/env python

from gpiozero import Button

import asyncio
import logging
import sys
import json
from pathlib import Path

from .inference import Inference
from .graphics import overlay_rects, extract_subimages
from .camera import Camera
from .ocr import CliOcr, FastOcr
from .web import run_web_app, schedule_update
from .output import KeebdOutput

class App:
    def __init__(self, storage_path, button, camera, inference, ocr, output, state_output, logger):
        self.storage_path = storage_path
        self.button = button
        self.camera = camera
        self.inference = inference
        self.ocr = ocr
        self.output = output
        self.logger = logger
        self.state_output = state_output

        self.button.when_pressed = self.cv2_entrypoint 
    
    def img_path(self, name):
        return self.storage_path/f"{name}.jpg"

    def cv2_entrypoint(self):
        self.logger.info("button pressed")
        asyncio.run(self.callback_with_cv2())
            
    def pick_detection(self, detection_list):
        if len(detection_list) == 0:
            return None
        else:
            return sorted(detection_list, key=lambda det: det.confidence)[-1]

    async def callback_with_cv2(self):
        await self.state_output.processing()
        name_path = self.img_path('name')
        number_path = self.img_path('number')
        screen_path = self.img_path('image')
        
        self.logger.info("Image capture started")
        full_size_image = self.camera.take_pil_image()
        self.logger.info("Image captured, starting inference")
        detections = self.inference.infer(full_size_image)
        self.logger.info("Inference done, selecting detected areas")

        selected_name = self.pick_detection(detections['name'])
        selected_number = self.pick_detection(detections['number'])
        if selected_name and selected_number:
            resized_for_display = full_size_image.resize((820, 616))
            name_image, number_image = extract_subimages(resized_for_display, 
                    [s.norm_rect() for s in (selected_name, selected_number)])

            name_image.save(name_path)
            number_image.save(number_path)
            overlay_rects(resized_for_display, 
                    [s.norm_rect() for s in (selected_name, selected_number)])
            resized_for_display.save(screen_path)

            self.logger.info('images extracted')

            ocr_jobs = (self.ocr.read_name(name_path), 
                self.ocr.read_number(number_path))
            decoded_name, decoded_number = await asyncio.gather(*ocr_jobs)

            self.logger.info(f"Read: {repr(decoded_name)} {repr(decoded_number)}")

            await asyncio.gather(self.output.send(decoded_name, decoded_number),
                   schedule_update({'name': decoded_name, 'number': decoded_number}),
                   self.state_output.success())
            self.logger.info("Client notified")
            

        else:
            await self.state_output.ready()
            if not selected_name:
                logger.info("No name found")
            if not selected_number:
                logger.info("No number found")

class LEDDStateOutput:
    def __init__(self, logger):
        self.logger = logger

    async def _set_state(self, state_name):
        self.logger.info(f"setting state {state_name}")
        proc = await asyncio.create_subprocess_exec(
                "/usr/local/bin/ledd-set-state", 
                state_name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL)
        await proc.communicate()

    async def _go_to_ready_after_delay(self):
        await asyncio.sleep(3)
        await self.ready()

    async def start(self):
        return await self._set_state("start")

    async def ready(self):
        return await self._set_state("ready")

    async def processing(self):
        return await self._set_state("processing")

    async def success(self):
        await self._set_state("success")
        await asyncio.sleep(3)
        await self.ready()

    async def alert(self):
        return await self._force_state("alert")


logger = None

async def exec(argv):
    global logger

    quarter_size_settings = {
            'cfg_filename': 'model/scanner-224/scanner-yolov4-tiny.cfg',
            'weights_filename': 'model/scanner-224/backup/scanner-yolov4-tiny_final.weights',
            'input_dims': (224, 224)
            }

    class_labels = ['name', 'number']

    settings = quarter_size_settings

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    if '--debug' in argv:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    logging.getLogger('picamera2.request').setLevel(logging.WARN)

    state_output = LEDDStateOutput(logger)
    await state_output.start()

    logger.debug("Loading inference")
    if '--fake-inference' in argv:
        inference = Inference.fake(class_labels)
    else:
        inference = Inference(settings['cfg_filename'], 
                settings['weights_filename'], 
                settings['input_dims'], 
                class_labels)
    logger.debug("Inference loaded")

    logger.debug("Loading camera")
    if '--fake-camera' in argv:
        camera = Camera.fake('fakes/scan.png')
    else:
        camera = Camera()
    logger.debug("Camera loaded")

    if '--fake-typing' in argv:
        key_delay_ms = 50 
    else:
        key_delay_ms = 0

    if '--fake-output' in argv:
        output = KeebdOutput.fake()
    else:
        output = KeebdOutput(key_delay_ms)

    ocr = FastOcr()
    button = Button(17)
    storage_path = Path("/tmp/piscanner/images")
    storage_path.mkdir(parents=True, exist_ok=True)
    app = App(storage_path, button, camera, inference, ocr, output, state_output, logger)

    await run_web_app(storage_path)
    await state_output.ready()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(exec(sys.argv))
