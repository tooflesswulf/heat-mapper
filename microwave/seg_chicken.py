import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

#Assume we are in right place (LOL)

raws = 'chicken_jpegz/'
put = 'focuzzzz/'

brownish = [136, 106, 61]


def get_closest(centers, target):
    diff = centers - target
    scores = np.sum(diff ** 2, axis=1)
    return np.argmin(scores)


def get_clustered(img):
    Z = img.reshape((-1,3))

    # convert to np.float32
    Z = np.float32(Z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 8
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]

    chicken_color = get_closest(center[...,::-1], brownish) #center is bgr
    mask = label == chicken_color
    x,y,_ = img.shape
    mask = mask.reshape((x,y))

    res2 = res.reshape((img.shape))
    return res2, mask


def select_cluster(mask, img):
    msk = cv2.convertScaleAbs(mask.astype(int))

    kernel = np.ones((5, 5), np.uint8)
    msk = cv2.dilate(msk, kernel, iterations=12)

    ret, markers = cv2.connectedComponents(msk)
    mk_count = np.bincount(markers.flatten())
    mk_count[0] = 0
    whichmk = np.argmax(mk_count)

    markers[markers != whichmk] = 0
    markers = markers / whichmk

    markers = markers[..., np.newaxis]

    zz = markers.transpose(2, 1, 0) * img.transpose(2, 1, 0)

    return zz.transpose(2,1,0)


folders = os.listdir(raws)
for fold in folders:
    if os.path.isdir(raws+fold):
        if not os.path.exists(put+fold):
            os.mkdir(put+fold)
        for imname in os.listdir(raws+fold):
            if imname.endswith('.jpg'):
                img = cv2.imread(raws+fold+'/'+imname)

                print(raws+fold+'/'+imname)

                cl, mask = get_clustered(img)
                zz = select_cluster(mask, img)

                cv2.imwrite(put+fold+'/'+imname, zz)