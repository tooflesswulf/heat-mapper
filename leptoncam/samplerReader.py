import numpy as np
from matplotlib import pyplot as plt
#%matplotlib inline

leptonHdrDtype = np.dtype( [('width',np.int32), \
                          ('height',np.int32), \
                          ('minVal',np.int32), \
                          ('maxVal',np.int32), \
                          ('intTemp',np.int32), \
                          ('timeStamp',np.float64), \
                          ('padBytes',np.uint32),
                         ('img',np.uint16, (19200,))] )

imgs = np.fromfile('/home/arvind/git/heat-mapper/leptoncam/Test.dat',dtype=leptonHdrDtype)

def plotImg(imgList,idx):
    w,h,minV,maxV,intTemp,tStamp,pBytes,img = imgList[idx]
    img = np.reshape( img, (120,160) )
    plt.imshow(img)
    plt.clim(3000,4000)
    plt.show()

plotImg(imgs,5) # PLot the 5th image in the sequence.
