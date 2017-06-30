import numpy as np
from segment_hist import get_chunk_thresholds
import matplotlib.pyplot as plt
import pickle
import sys
import cv2
import glob

dt = np.dtype( [('w', np.intc),
                ('h', np.intc),
                ('low',np.intc),
                ('high',np.intc),
                ('int_temp',np.intc),
                ('pad',np.intc),
                ('time','d'),
                ('img', np.uint16, (160*120,))
                ])

disp = {}

soup_rad = 30

def o(fname):
    return pickle.load(open(fname, 'rb'))


def cmask(center, radius, array_like):
  a,b = center
  nx,ny = array_like.shape
  y,x = np.ogrid[-a:nx-a,-b:ny-b]
  mask = x*x + y*y <= radius*radius

  return mask


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


def disp_diff(d):
    plt.clf()

    a = disp['a']
    img = get_img(d + 1, a)
    img2 = get_img(d + 2, a)
    img3 = get_img(d, a)

    dyeiff = img - 0.5 * img2 - 0.5 * img3
    dyeiff = cv2.GaussianBlur(dyeiff,(5,5),0)

    r, c = img.shape
    cm = cmask((r/2, c/2), soup_rad, dyeiff)

    plt.subplot(221)
    plt.imshow(img)
    plt.subplot(222)

    plt.imshow(img * (1-cm))
    plt.subplot(223)
    plt.imshow(dyeiff)
    # plt.imshow(img2)
    # plt.imshow(img3)
    # if d in rgb_images.keys():
    #     plt.imshow(rgb_images[d][...,::-1])
    plt.subplot(224)
    plt.imshow(dyeiff * (1-cm))
    diff_rmse = np.mean(dyeiff) **2
    # plt.gcf().canvas.set_window_title( 'FRAME: {}\tNEW_RMSE DIFF: {}'.format(d, diff_rmse) )
    plt.gcf().canvas.set_window_title( 'FRAME: {}\tMAX DIFF: {}'.format(d, np.amax(dyeiff * (1-cm))) )
    disp['mode'] = 'single'
    disp['x'] = d

    plt.draw()


def on_click(event):
    if disp['mode'] == 'summ' and event.inaxes is not None:
        x = int(event.xdata)
        try:
            assert(x > 0)
            disp_diff(x)
        except (IndexError, AssertionError):
            print('Invalid index.')


def on_key(event):
    if disp['mode'] == 'single':
        if event.key == 'right':
            x = disp['x'] + 1
            try:
                assert (x > 0)
                disp_diff(x)
            except (IndexError, AssertionError):
                print('Invalid index.')
        elif event.key == 'left':
            x = disp['x'] - 1
            try:
                assert (x > 0)
                disp_diff(x)
            except (IndexError, AssertionError):
                print('Invalid index.')
        elif event.key in ['q', 'r']:
            plt.clf()
            plt.plot(disp['tot_diff'])
            has_img = np.array(list(rgb_images.keys()))
            plt.scatter(has_img, np.zeros_like(has_img), c='g')
            disp['mode'] = 'summ'
            plt.draw()
    elif disp['mode'] == 'summ':
        if event.key=='q':
            plt.close()
        elif event.key == 'z':
            disp['mode'] = 'zoom'
    elif disp['mode'] == 'zoom':
        if event.key in ['r','q']:
            disp['mode'] = 'summ'


def check_dat(fname):
    a = np.fromfile(fname, dtype=dt)
    disp['a'] = a
    images = conv_celsius(a['img'])
    times = a['time']
    link_rgb(times)

    diff = images[1:-1] - 0.5*images[2:] - 0.5*images[:-2]
    # maxes = np.amax(diff, axis=1)
    # mins = np.amin(diff, axis=1)

    tot_diff = np.sqrt(np.mean(diff**2, axis=1))
    # tot_diff = np.mean(diff, axis=1) **2
    outlier_locs = np.where(tot_diff > 1.5)

    fig = plt.figure(1)
    disp['mode'] = 'summ'
    disp['tot_diff'] = tot_diff
    plt.plot(tot_diff)
    has_img = np.array(list(rgb_images.keys()))
    plt.scatter(has_img, np.zeros_like(has_img), c='g')
    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    cid2 = fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()


rgb_images = {}
def load_rgb(path):
    pickle_files = glob.glob(path+'*.pkl')
    for p in pickle_files:
        images = pickle.load(open(p, 'rb'))
        for t, im in images:
            rgb_images[t] = im


def link_rgb(therm_t):
    global rgb_images
    assert len(therm_t.shape) == 1, 'Thermal temps are not 1-d vector?'
    rgb_oldk = rgb_images.keys()
    rgb_t = [float(k) for k in rgb_oldk]

    def get_closest_index(x):
        return np.argmin(np.abs(therm_t - x))

    rgb_keys = list(map(get_closest_index, rgb_t))
    new_rgb_images = {}
    for k, k_old in zip(rgb_keys, rgb_oldk):
        new_rgb_images[k] = rgb_images[k_old]

    rgb_images = new_rgb_images


if __name__ == '__main__':
    path = sys.argv[1]
    slash_loc = [pos for pos, char in enumerate(path) if char == '/']
    if len(slash_loc) == 0:
        slash_loc = [0]
    folder = path[:slash_loc[-1] + 1]

    rgbs = load_rgb(folder)
    check_dat(path)