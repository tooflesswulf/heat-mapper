import numpy as np
from segment_hist import get_chunk_thresholds
import matplotlib.pyplot as plt
import pickle
import sys
import cv2

dt = np.dtype( [('w', np.intc),
                ('h', np.intc),
                ('low',np.intc),
                ('high',np.intc),
                ('int_temp',np.intc),
                ('pad',np.intc),
                ('time','d'),
                ('img', np.uint16, (160*120,))
                ])

def o(fname):
    return pickle.load(open(fname, 'rb'))

def check_file():
    t, img = o(sys.argv[1])
    print('time: ', t)

    highs, lows, edges = get_chunk_thresholds(img, peak_spacing=5, less=True)
    chunks = edges[lows]
    lows = lows[:-1]
    segmented = img.copy()
    for i, (e1, e2) in enumerate(zip(chunks[:-1], chunks[1:])):
        segmented[(e1 <= img) & (img <= e2)] = i

    h, bins = np.histogram(img.flatten(), bins=50)

    plt.subplot(221)
    plt.imshow(img)
    plt.subplot(222)
    plt.imshow(segmented)
    plt.subplot(223)
    # plt.plot(bins[:-1], h)
    plt.plot(h)
    plt.scatter(lows, h[lows])
    plt.scatter(highs, h[highs])
    plt.show()

def conv_celsius(temps):
    r=395653
    b = 1428
    f = 1
    o = 156
    t_k = b / np.log(r / (temps - o) + f)
    return t_k - 273.15

def get_img(num, a):
    img = a['img'][num].reshape(120,160)
    img = np.rot90(img)
    return conv_celsius(img)

def check_dat():
    fname = sys.argv[1]
    try:
        fnum = int(sys.argv[2])
        diff = False
    except:
        diff = True
        print('Reading frame number failed. Showing difference.')

    a = np.fromfile(fname, dtype=dt)

    if not diff:
        img = get_img(fnum+1, a)
        img2 = get_img(fnum+2, a)
        img3 = get_img(fnum, a)

        plt.subplot(221)
        plt.imshow(img)
        plt.subplot(222)
        plt.imshow(img2)
        plt.subplot(223)
        plt.imshow(img3)
        plt.subplot(224)
        plt.imshow(img-0.5*img2-0.5*img3)
    else:
        images = conv_celsius(a['img'])
        diff = images[1:-1] - 0.5*images[2:] - 0.5*images[:-2]
        # maxes = np.amax(diff, axis=1)
        # mins = np.amin(diff, axis=1)

        tot_diff = np.sqrt(np.mean(diff**2, axis=1))
        outlier_locs = np.where(tot_diff > 1.5)
        # print(outlier_locs)
        try:
            print('first splatter guess:', outlier_locs[0][0])
        except IndexError:
            print('No splatter detected.')
        # plt.plot(tot_diff)

        for d in np.argsort(tot_diff)[::-1]:
            img = get_img(d + 1, a)
            img2 = get_img(d + 2, a)
            img3 = get_img(d, a)

            plt.subplot(221)
            plt.imshow(img)
            plt.subplot(222)
            plt.imshow(img2)
            plt.subplot(223)
            plt.imshow(img3)
            plt.subplot(224)
            dyeiff = img - 0.5 * img2 - 0.5 * img3
            plt.imshow(dyeiff)
            print('FRAME: {}\tRMSE DIFF: {}'.format(d, np.sqrt(np.mean(dyeiff**2))))
            plt.show()


    plt.show()

    # print(np.argsort(maxes)[-10:])
    # print(np.argsort(mins)[:10])

    # plt.figure()
    # plt.imshow(np.rot90(diff[fnum].reshape(120,160)))

if __name__ == '__main__':
   check_dat()