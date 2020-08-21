#!/usr/bin/env python3

"""Main."""

import sys
import os
from cpu import *

dirpath = os.path.dirname(os.path.abspath(__file__))
program_file = dirpath + "/examples/stack.ls8"

cpu = CPU()

cpu.load(program_file)
cpu.run()