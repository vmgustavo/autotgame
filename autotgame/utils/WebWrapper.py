import tarfile
import os
import math
import stat
import logging

import requests
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

DRIVER_DIR = f'{os.getcwd()}/driver'
DOWN_URL = 'https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz'


class WebWrapper:
    def __init__(self, headless, window_size):
        self.logger = logging.getLogger(__name__)

        if not os.path.exists(DRIVER_DIR):
            os.mkdir(DRIVER_DIR)
        self.driver_path = self.download_driver(driver_name='geckodriver')

        firefox_options = webdriver.FirefoxOptions()
        if headless:
            firefox_options.add_argument('--headless')
        firefox_options.add_argument('--no-sandbox')

        self.driver = webdriver.Firefox(firefox_options=firefox_options, executable_path=self.driver_path)
        self.driver.set_window_size(*window_size)

    def wait_find(self, xpath):
        try:
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((By.XPATH, xpath)))
        finally:
            return self.driver.find_element_by_xpath(xpath)

    def wait_and_click(self, xpath):
        actions = webdriver.ActionChains(self.driver)
        element = self.wait_find(xpath=xpath)
        self.driver.implicitly_wait(1)
        self.driver.execute_script('arguments[0].scrollIntoView();', element)
        actions.move_to_element(element)
        actions.click()
        actions.perform()

    def get_driver(self):
        return self.driver

    def download_driver(self, driver_name):
        driver_path = f'{DRIVER_DIR}/{driver_name}'
        if not os.path.exists(driver_path):
            r = requests.get(DOWN_URL, stream=True)
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024
            wrote = 0
            with open(f'{DRIVER_DIR}/output.bin', 'wb') as f:
                for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size // block_size), unit='KB',
                                 unit_scale=True):
                    wrote = wrote + len(data)
                    f.write(data)
            if total_size != 0 and wrote != total_size:
                self.logger.error('DOWNLOAD ERROR, something went wrong')
            self.logger.info('Unzipping downloaded file')
            tar = tarfile.open(f'{DRIVER_DIR}/output.bin', 'r:gz')
            tar.extractall(path=DRIVER_DIR)
            tar.close()
            os.remove(f'{DRIVER_DIR}/output.bin')
            self.logger.info(f'File extracted to {driver_path}')
        else:
            self.logger.info(f'File already downloaded at {driver_path}')

        st = os.stat(driver_path)
        os.chmod(driver_path, st.st_mode | stat.S_IEXEC)
        return driver_path

    def close(self):
        # Close webdriver connection
        self.driver.quit()
