import numpy as np
import cv2
import pickle
import matplotlib.pyplot as plt

im_therm = pickle.load(open('images/therm0.pkl','rb'))
im_rgb = pickle.load(open('images/rgb0.pkl','rb'))[...,::-1]
warp_mat = pickle.load(open('persp_mat.p','rb'))


def get_chunk_thresholds(im_therm, binnum=50, peak_spacing=5):
    histo, edges = np.histogram(im_therm.flatten(), bins=binnum)
    grad = np.gradient(histo)
    grad[np.abs(grad)<.025*np.sum(histo)/binnum] = 0

    # Get the local maxima on the crieteria that the gradient changes sign from 0+ to -.
    # Store the lower or higher value since this is often unclear.
    highs = []
    for n, (g1, g2) in enumerate(zip(grad[:-1],grad[1:])):
        if g1 >= 0 > g2:
            if histo[n] < histo[n+1]:
                highs.append(n+1)
            else:
                highs.append(n)

    highs = np.array(highs)

    # Strip the highs of peaks that are too close to each other.  Prioritizes keeping higher peaks
    highs_ordered = [x for (y, x) in sorted(zip(histo[highs], highs), key=lambda pair: pair[0], reverse=True)]
    new_highs = np.array([])
    for h in highs_ordered:
        if not any(np.abs(new_highs-h) < peak_spacing):
            new_highs = np.append(new_highs, h)
    highs = np.sort(new_highs).astype(int)

    lows = [0]
    for h1, h2 in zip(highs[:-1], highs[1:]):
        min_index = np.argmin(histo[h1:h2]) + h1
        lows.append(min_index)
    lows.append(binnum)
    lows = np.array(lows)

    return edges[lows]

threshs = get_chunk_thresholds(im_therm)

im_zones = np.zeros_like(im_therm)
for i, (e1, e2) in enumerate(zip(threshs[:-1], threshs[1:])):
    im_zones[(e1 <= im_therm) & (im_therm <= e2)] = i


x,y,_ = im_rgb.shape

# plt.imshow(im_zones)
# plt.imshow(im_therm)
plt.imshow(cv2.warpPerspective(im_zones, warp_mat, (y,x)), alpha=.5)
plt.imshow(im_rgb, alpha=.5)
plt.show()