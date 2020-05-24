# PYTHON DEFAULT
import logging

# INSTALLED
import click

# REPO MODULE
from autotgame import MathBattle

import MyLogger
MyLogger.Logger()
logger = logging.getLogger(__name__)


@click.command()
@click.option('-g', '--game', required=True, default=None, help='MathBattle')
def main(game):
    if game == 'MathBattle':
        game = MathBattle()
        game.open()
        game.play()


if __name__ == '__main__':
    main()
