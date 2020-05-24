import abc
import logging
from io import BytesIO

import numpy as np
from PIL import Image
from pynput import keyboard


from .utils import WebWrapper


class BasicAPI(abc.ABC):
    def __init__(self, url):
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.wrapper = WebWrapper(headless=False, window_size=(650, 650))

    def open(self):
        self.wrapper.driver.get(self.url)
        self.wrapper.wait_find(xpath='//*[@id="game_title"]')
        self.logger.info('Game loaded')
        self.wrapper.driver.switch_to_window(self.wrapper.driver.current_window_handle)

    @abc.abstractmethod
    def play(self):
        raise NotImplementedError

    @abc.abstractmethod
    def auto(self):
        raise NotImplementedError

    def close(self):
        self.wrapper.close()

    def ss(self):
        img_bytes = self.wrapper.driver.get_screenshot_as_png()
        return np.array(Image.open(BytesIO(img_bytes)))

    @abc.abstractmethod
    def gameover(self):
        raise NotImplementedError

    @staticmethod
    def user_stop(key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False
