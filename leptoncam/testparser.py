import numpy as np
import pickle
import matplotlib.pyplot as plt
import sys
import os

try:
	fname = sys.argv[1]
	if os.path.exists(fname):
		try:
			id = int(sys.argv[2])
		except:
			id = 0
	else:
		fname = 'Test.dat'
		id = int(sys.argv[1])
except:
	fname = 'Test.dat'
	id = 0

dt = np.dtype( [('w', np.intc),
				('h', np.intc),
				('low',np.intc),
				('high',np.intc),
				('int_temp',np.intc),
				('time','d'),
				('pad',np.intc),
				('img', np.uint16, (160*120,))
				])

a = np.fromfile(fname, dtype=dt)

img = a['img'].reshape(-1,120,160)
# img = img.reshape(100,-1)
print("Number of images: {}".format(img.shape[0]))

threshold = 1000
to_disp = img[id]

r=395653
b = 1428
f = 1
o = 156
t_k = b / np.log(r / (to_disp - o) + f)
disp_c = t_k - 273.15

avg = np.mean(to_disp)
# to_disp[np.abs(to_disp - avg) > threshold] = avg + 999

print("Mean value: {}".format(avg))

# a = to_disp[30:61,0:80].copy()
# to_disp[30:61, 0:80] = to_disp[30:61,80:]
# to_disp[30:61, 80:] = a

# a = to_disp[91:,0:80].copy()
# to_disp[91:, 0:80] = to_disp[91:,80:]
# to_disp[91:, 80:] = a

# to_disp[30:-1, 80:] = to_disp[31:, 80:]
# to_disp[60:-1, :80] = to_disp[61:, :80]
# to_disp[90:-1, 80:] = to_disp[91:, 80:]

# print(np.argwhere(np.abs(to_disp - avg) > 1000))



plt.figure("Image number {}".format(id))
try:	plt.imshow(disp_c)
except:	plt.imshow(img[id])
plt.show()
