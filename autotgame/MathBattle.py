import re
import logging
import operator
from time import sleep

import pyautogui
from pynput import keyboard

from .BasicAPI import BasicAPI


class MathBattle(BasicAPI):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        url = 'https://tbot.xyz/math/'
        super(MathBattle, self).__init__(url)

    def play(self):
        self.wrapper.wait_and_click('/html/body/div/div[3]/div/div[2]/div[1]/div/div[3]')
        self.auto()

    def auto(self):
        listener = keyboard.Listener(on_press=self.user_stop)
        listener.start()

        while not self.gameover():
            res = self.evaluate_task(*self.get_task())
            if listener.is_alive():
                self.act(res)
            else:
                self.act(not res)
            sleep(.2)

    def get_task(self):
        task_xpath = '//*[@id="task"]'
        task = self.wrapper.wait_find(task_xpath)
        equation, result = task.text.split('\n')
        result = result.strip('= ')
        self.logger.debug(f'{equation} = {result}')
        return equation, result

    def evaluate_task(self, equation, result):
        a, op, b = re.search(r'(\d+)\s([–+/×])\s(\d+)', equation).groups()
        return self.map_operator(op)(int(a), int(b)) == int(result)

    @staticmethod
    def map_operator(op):
        return {
            '–': operator.sub,
            '+': operator.add,
            '/': operator.floordiv,
            '×': operator.mul
        }[op]

    @staticmethod
    def act(flag):
        if flag:
            pyautogui.press('left')
        else:
            pyautogui.press('right')

    def gameover(self):
        elem = self.wrapper.driver.find_element_by_xpath('/html/body/div/div[2]/div/div[2]/div[2]').text
        return 'YOU SCORED' in elem
