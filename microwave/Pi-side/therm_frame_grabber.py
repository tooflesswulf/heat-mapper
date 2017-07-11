import numpy as np
import glob
import threading
import time
import cv2

read_files = set([])
soup_rad = 30 #px
dt = np.dtype([('w', np.intc),
               ('h', np.intc),
               ('low', np.intc),
               ('high', np.intc),
               ('int_temp', np.intc),
               ('pad', np.intc),
               ('time', 'd'),
               ('img', np.uint16, (160 * 120,))
               ])


def conv_celsius(temps):
    r = 395653
    b = 1428
    f = 1
    o = 156
    t_k = b / np.log(r / (temps - o) + f)
    return t_k - 273.15


# Creates a circle mask with some radius and center.
def cmask(center, radius, array_like):
    a, b = center
    nx, ny = array_like.shape
    y, x = np.ogrid[-a:nx-a,-b:ny-b]
    mask = x*x + y*y <= radius*radius
    return mask


class ObjectStorer(object):
    def __init__(self, init):
        self.value = init
        self.time = 0

    def store(self, init):
        self.value = init

    def storet(self, t):
        self.time = t


# Grabs thermal image frames from the .dat files.
def grab_frames(last_time):
    frame_list = np.array([]).reshape(0,19200)
    times_list = np.array([])
    dat_files = set( glob.glob('*.dat') )
    to_read = dat_files - read_files
    for fname in to_read:
        a = np.fromfile(fname, dtype=dt)
        ts = a['time']
        imgs = a['img']

        mask = ts>=last_time
        frame_list = np.concatenate((frame_list, imgs[mask]), axis=0)
        times_list = np.concatenate((times_list, ts[mask]))

        if ts[mask].shape[0] == 0 and fname != 'thermal.dat':
            read_files.add(fname)

    sort_order = np.argsort(times_list, axis=0)
    return frame_list[sort_order], times_list[sort_order]


def get_lapl(img):
    lapl = cv2.Laplacian(img, cv2.CV_64F)
    r, c = img.shape
    cm = cmask((r/2, c/2), soup_rad, img)
    lapl[cm] = np.nan
    # lapl[np.abs(lapl) > 7] = 0
    m = np.nanmean(lapl)
    lapl[cm] = m
    return lapl


# Checks the a set of images for splatter.
# Currently checks the target and previous frame.
# Takes the Laplacian of both images, and if there is any significant increase greater than 10(?), it marks a splatter.
# I don't actually know the units, just guessing with this magic number right now.
def check_splatter(images):
    assert images.shape[0] == 2

    # Strip the first few cols b/c theres some distortions.
    i1 = images[1].reshape(120,160)[5:-5]
    i2 = images[0].reshape(120,160)[5:-5]

    l1 = get_lapl(i1)
    l2 = get_lapl(i2)
    # diff = to_check[1] - 0.5 * to_check[0] - 0.5 * to_check[2]
    diff = l2 - l1

    score = np.amax(diff) - np.mean(diff)

    # if score > 10:
    #     print('DEBUG')
    #     print(cm.shape)
    #     print(images.shape)
    #     print(score)
    #     print('END DEBUG')

    return score > 5


# Main thread loop. Grabs the latest few frames, and checks them for splatter.
# When it finds splatter, call on_splatter().
# Repeat.
def thread_loop(latest_img, on_splatter):
    last_time = 0
    while True:
        frames, times = grab_frames(last_time)
        if len(frames) > 0:
            last = np.rot90(conv_celsius(frames[-1].reshape(120,160)))
            latest_img.store(last)
            latest_img.storet(times[-1])
        if len(frames) >= 3:
            frames = conv_celsius(frames)
            for i in range(1, len(frames) - 1):
                if check_splatter(frames[i - 1:i+1]):
                    on_splatter(times[i])
            last_time = times[-2]


def start_thread(on_splatter=None):
    latest_img = ObjectStorer( np.zeros((120*160)) )
    if on_splatter:
        th = threading.Thread(target=thread_loop, args=[latest_img, on_splatter])
    else:
        th = threading.Thread(target=thread_loop, args=[latest_img, lambda x: print('Splatter at t={}'.format(x))])
    th.setDaemon(True)
    th.start()
    return latest_img

if __name__ == '__main__':
    img = start_thread()
    time.sleep(3)
    print('Python time is ', time.time())
