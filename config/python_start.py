import sys
from math import sqrt, log, exp, pi

# Colorful prompts
sys.ps1 = "\033[1;33m>>>\033[0m "
sys.ps2 = "\033[1;34m...\033[0m "

# Some constants
max_u64 = 2**64 - 1
max_i64 = 2**63 - 1
min_i64 = -(2**63)

max_u32 = 2**32 - 1
max_i32 = 2**31 - 1
min_i32 = -(2**31)

max_u16 = 2**16 - 1
max_i32 = 2**15 - 1
min_i32 = -(2**15)


def display_as_hex(item):
    """Display integers as hex by default"""
    __builtins__._ = item
    if isinstance(item, int) and not isinstance(item, bool):
        print(hex(item))
    elif item is not None:
        print(repr(item))


def display_as_bin(item):
    """Display integers as bin by default"""
    __builtins__._ = item
    if isinstance(item, int) and not isinstance(item, bool):
        print(bin(item))
    elif item is not None:
        print(repr(item))


def print_hex():
    sys.displayhook = display_as_hex


def print_bin():
    sys.displayhook = display_as_hex


def print_int():
    sys.displayhook = sys.__displayhook__
