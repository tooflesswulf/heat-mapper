import numpy as np
import pickle
import matplotlib.pyplot as plt
import sys

try:
	id = int(sys.argv[1])
except:
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

a = np.fromfile('Test.dat', dtype=dt)

img = a['img'].reshape(-1,120,160)
# img = img.reshape(100,-1)
# print(img.shape)

threshold = 1000
to_disp = img[id]
avg = np.mean(to_disp)
# to_disp[np.abs(to_disp - avg) > threshold] = avg + 999

print("Mean value: {}".format(avg))

a = to_disp[30:61,0:80].copy()
to_disp[30:61, 0:80] = to_disp[30:61,80:]
to_disp[30:61, 80:] = a

a = to_disp[91:,0:80].copy()
to_disp[91:, 0:80] = to_disp[91:,80:]
to_disp[91:, 80:] = a

to_disp[30:-1, 80:] = to_disp[31:, 80:]
to_disp[60:-1, :80] = to_disp[61:, :80]
to_disp[90:-1, 80:] = to_disp[91:, 80:]

# print(np.argwhere(np.abs(to_disp - avg) > 1000))

plt.figure("Image numbers {}".format(id))
try:	plt.imshow(to_disp - avg)
except:	plt.imshow(img[id])
plt.show()