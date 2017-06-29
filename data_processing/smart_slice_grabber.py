import matplotlib.pyplot as plt
import pickle
import os
import numpy as np
import sys

args = sys.argv[1:]
summ_loc = 'summary/'

try:
    fname = args[0]
    if os.path.exists(fname):
        try:
            frame_num = int(args[1])
        except:
            frame_num = 0
    else:
        fname = 'Test.dat'
        frame_num = int(args[0])
except:
    fname = 'Test.dat'
    frame_num = 0