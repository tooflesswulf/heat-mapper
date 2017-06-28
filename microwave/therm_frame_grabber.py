import numpy as np
import time
import glob
import heapq as pq

read_files = set([])
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


# Grabs thermal image frames from the .dat files.
def grab_frames(last_time):
    frame_list = np.array([])
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

        if fname != 'thermal.dat':
            read_files.add(fname)

    sort_order = np.argsort(times_list, axis=0)
    return frame_list[sort_order], times_list[sort_order]


# Checks the a set of images for splatter.
# Currently checks 3 frames around the target.
def check_splatter(images):
    assert images.shape[0] >= 3
    to_check = conv_celsius(images[-3:])
    diff = to_check[1] - 0.5 * to_check[0] - 0.5 * to_check[2]
    rmse = np.sqrt(np.mean(diff ** 2, axis=1))
    return rmse > 1.5

frames = grab_frames(0)
for i in range(1, len(frames)-2):
    check_splatter(frames[i-1:i+2])