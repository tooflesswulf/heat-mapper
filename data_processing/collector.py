import numpy as np
import sys
import os

try:
	path = sys.argv[1]
	files = os.listdir(path)
except:
	path = 'Bananna_data/1/dat (30s)'
	files = os.listdir(path)

