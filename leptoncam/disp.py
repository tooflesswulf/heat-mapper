import pickle
import numpy as np
import matplotlib.pyplot as plt
import sys

try:
	id = int(sys.argv[1])
except:
	id = 0

img = pickle.load(open('images.p', 'rb'))

img = img.reshape(-1,120,160)
# img = img.reshape(100,-1)
print(img.shape)

threshold = 10000
to_disp = img[id]
avg = np.mean(to_disp)
to_disp[np.abs(to_disp - avg) > threshold] = avg

print(avg)

# print(np.argwhere(np.abs(to_disp - avg) > 1000))

plt.figure("Image number {}".format(id))
plt.imshow(to_disp - avg)
plt.show()