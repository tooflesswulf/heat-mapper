import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# picam = cv2.imread('checkers.jpg')
# lepton = cv2.imread('checkers-h2.jpg')

picam = cv2.imread('egg.jpg')
lepton = cv2.imread('egg-heat.jpg')

lepton = np.rot90(lepton) * 100

rgbpts = np.array( [[933,300], [1190,300], [1457,318],
                    [900,417], [1183,431], [1473,427],
                    [871,558], [1180,557], [1488,567],
                    [833,735], [1174,732], [1510,737],
                    [780,935], [1159,928], [1536,929],
                    [729,1173],[1139,1155],[1588,1163]] )

leppts = np.array( [[38,61], [50,61], [63,61],
                    [37,67], [50,67], [64,67],
                    [33,74], [49,74], [65,73],
                    [32,82], [49,81], [67,82],
                    [30,93], [48,93], [69,91],
                    [27,104],[48,103],[70,103]] )

mask = np.array((0,2,-3,-1))

src = np.array([[38,61],[63,61],[27,104],[70,103]],np.float32)
dst = np.array([[933,300],[1457,318],[729,1173],[1588,1163]],np.float32)

ret = cv2.getPerspectiveTransform(src,dst)


# rgbpts = rgbpts[mask].astype(np.float32)
# leppts = leppts[mask].astype(np.float32)

# print(rgbpts.shape)

rainbow = cm.rainbow(np.linspace(0,1,rgbpts.shape[0]))

plt.subplot(121)
plt.imshow(picam)
plt.scatter(*rgbpts.T, color=rainbow, s=5)
plt.subplot(122)
r, c, _ = picam.shape
im = cv2.warpPerspective(lepton, ret, dsize=(c, r))
plt.imshow(im)
plt.scatter(*rgbpts.T, color=rainbow, s=5)
# plt.scatter(*leppts.T, color=rainbow, s=5)
plt.show()



