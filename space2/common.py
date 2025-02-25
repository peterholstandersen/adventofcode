import sys
import os
import re
import math
from math import sqrt, sin, cos, degrees, radians, ceil, floor  # round is already there
import datetime
from random import randint
import signal
from copy import deepcopy
import time
import uuid
import pickle
import traceback

from world import *
from utils import *
from view import *

# ANSI: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
END = "\033[0m"

BG_LIGHT_CYAN = "\033[1;46m"
BG_CYAN = "\033[1;106m"
# https://i.sstatic.net/9UVnC.png
# LIGHT: (BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE) = range(40,48)
# Bright versions starts at 100 (ends at 107)

DEFAULT_COLOUR = END # LIGHT_WHITE
ROOT = "/home/peter/PycharmProjects/adventofcode/spacemaster"  # for now
AU = 149.6e+06  # 149.600.000 km

# define paths