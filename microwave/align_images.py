import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pickle
import sys

# picam = cv2.imread('checkers.jpg')[:,::-1,:]
# lepton = cv2.imread('checkers-h2.jpg')[:,::-1,:]

# picam = cv2.imread('egg.jpg')[:,::-1,:]
# lepton = cv2.imread('egg-heat.jpg')
# lepton = np.rot90(lepton) * 100
# lepton = lepton[:,::-1]

try:
  i = int(sys.argv[1])
except:
  i=0

picam = pickle.load(open('images/rgb%d.pkl'%i,'rb'))[...,::-1]
lepton = pickle.load(open('images/therm%d.pkl'%i,'rb'))/100

ret = pickle.load(open('persp_mat.p','rb'))

# print(picam.shape, picam.dtype)
# print(lepton[5,5])

a = np.zeros((8,2))
i=0
def onclick(event):
     global i
     a[i] = event.xdata, event.ydata
     i += 1
     print('xdata=%f, ydata=%f' %
          (event.xdata, event.ydata))

# fig = plt.figure()
# cid = fig.canvas.mpl_connect('button_press_event', onclick)

# plt.subplot(121)
# plt.imshow(picam)
# plt.subplot(122)
# plt.imshow(lepton)
# plt.show()

# a = a.reshape(2,4,2).astype(np.float32)
# print(a)

# ret = cv2.getPerspectiveTransform(a[1],a[0])
# print(ret)
# print('SAVED.')
# pickle.dump(ret, open('persp_mat.p','wb'))


# print(a)

r, c, _ = picam.shape
warp = cv2.warpPerspective(lepton, ret, dsize=(c,r))

plt.subplot(121)
plt.imshow(picam)
plt.subplot(122)
plt.imshow(warp)

plt.figure()
plt.imshow(warp, alpha=.7)
plt.imshow(picam, alpha=.6)

plt.show()




