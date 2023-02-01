from selenium import webdriver
from selenium.webdriver.common.by import By
import tempfile
import sqlite3
import shutil
from pathlib import Path
import json

con = sqlite3.connect('./samples.db')
cur = con.cursor()

driver = webdriver.Chrome()
driver.implicitly_wait(10)

def open_file(html_path):
    driver.get(html_path.absolute().as_uri())
    driver.set_window_size(1, 480)

def take_screenshot(screenshot_path):
    driver.save_screenshot(screenshot_path)

def get_element_rect(xpath):
    element = driver.find_element(By.XPATH, xpath)
    if not element.is_displayed():
        raise Exception(f"{xpath} did not identify a displayed element")
    return element.rect

# Need this because there's pixel scaling going on. When we take a
# screenshot, its dimensions are double what the DOM reports as its
# size.
def scale_rect(rect):
    result = {}
    for dim in rect:
        result[dim] = rect[dim]*2
    return result

def save_rects(rect_path):
    name_rect = get_element_rect('//div[@data-sid="user-name"]')
    number_rect = get_element_rect('//span[@data-sid="user-nhs-number"]')
    data_to_save = {'name': scale_rect(name_rect), 'number': scale_rect(number_rect)}
    rect_path.write_text(json.dumps(data_to_save))

screenshotdir_path = Path('./screenshots').absolute()
screenshotdir_path.mkdir(exist_ok=True)

with tempfile.TemporaryDirectory() as tmpdir:
    tmppath = Path(tmpdir)

    shutil.copytree('source-template/HomeScreen_files', tmppath / 'HomeScreen_files')

    for id, html in cur.execute("select id, html from samples"):
        screenshot_path = screenshotdir_path / f"{id}.png"
        rect_path = screenshotdir_path / f"{id}.rect.json"
        html_path = tmppath / "HomeScreen.html"
        html_path.write_text(html)

        if not screenshot_path.exists():
            print("Screenshotting to ", screenshot_path)
            open_file(html_path)
            take_screenshot(screenshot_path)

        if not rect_path.exists():
            print("Recording rects to ", rect_path)
            open_file(html_path)
            save_rects(rect_path)
