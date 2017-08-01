import numpy as np
import matplotlib.pyplot as plt
import sys
import cv2
import glob
import time

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


def conv_celsius(temps):
    r=395653
    b = 1428
    f = 1
    o = 156
    t_k = b / np.log(r / (temps - o) + f)
    return t_k - 273.15


def disp_img(num):
    a = disp['a']
    try:
        assert(num >= 0)
        a[num]
    except:
        print('Invalid index.')
    else:
        plt.clf()

        therm = np.rot90(a[num][0])
        bgr_img = a[num][1][...,::-1]
        t = a[num][2]

        plt.subplot(122)
        t_im = plt.imshow(therm)
        plt.colorbar(t_im)
        plt.subplot(121)
        plt.imshow(bgr_img)
        disp['x'] = num
        plt.gcf().canvas.set_window_title( 'FRAME: {}, TIME: {}'.format(num, t))

        plt.draw()


def on_key(event):
    print(event.key)
    if disp['mode'] == 'show':
        if event.key == 'right':
            x = disp['x'] + 1
            disp_img(x)
        elif event.key == 'left':
            x = disp['x'] - 1
            disp_img(x)
        elif event.key in ['q']:
            plt.close()
        elif event.key in ['j']:
            disp['mode'] = 'type'
            disp['input'] = ''
    if disp['mode'] == 'type':
        if event.key in '1234567890':
            disp['input'] += event.key
        elif event.key == '-':
            if disp['input'] == '':
                disp['input'] = '-'
        elif event.key == 'enter':
            x = int(disp['input'])
            del disp['input']
            disp['mode'] = 'show'
            print(x)
            disp_img(x)
        elif event.key == 'escape':
            del disp['input']
            disp['mode'] = 'show'


def init_gui(path, fname):
    a = np.fromfile(path+fname, dtype=dt)
    images = conv_celsius(a['img'])
    images = images.reshape(-1, 120, 160)
    times = a['time']
    therms = dict(zip(times, images))

    rgbs = load_rgb_files(path)

    links = link_dicts(therms, rgbs)
    # combined_images = (list(therms.values()), list(therms.values()))

    tzero = min(links[0])

    combined_images = []
    print('reading {} files.'.format(len(links)))
    for i, (k1, k2) in enumerate(links):
        print('reading {}/{}.'.format(i, len(links)), end='\r')
        approx_time = (k1+k2)/2-tzero
        combined_images.append((therms[k1], cv2.imread(rgbs[k2]), approx_time))

    disp['a'] = combined_images

    fig = plt.figure(1)
    # for i in range(len(links)):
    #     print('Saving frame {}/{}'.format(i, len(links)), end='\r')
    #     disp_img(i)
    #     plt.savefig('dump/{}.png'.format(str(i).zfill(4)), dpi=300)
    disp_img(0)
    disp['mode'] = 'show'
    cid2 = fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()


def load_rgb_files(path):
    rgb_images = {}
    images_filenames = glob.glob(path+'*.jpg')
    for i, f in enumerate(images_filenames):
        try:
            fn = f.split('/')[-1]

            t = fn[3:-4] # Strips the prefix and suffix off the filename.
            t = float(t)
            rgb_images[t] = f
        except Exception as e:
            print(f+' did not open properly.')
    return rgb_images


# Returns an array, where each element is
#  the index of the closest member in <targ> to the corresponding member of <arr>.
# Both arrays must be 1-dimensional.
def closest_indices(arr, targ):
    assert(len(arr.shape) == 1)
    assert(len(targ.shape) == 1)

    arrlen, = arr.shape

    targ_expand = np.tile(targ, (arrlen, 1))
    distsarr = np.abs(targ_expand - arr[:,np.newaxis])
    return np.argmin(distsarr, axis=1)


def link_dicts(d1, d2):
    k1 = np.array(sorted(d1.keys()))
    k2 = np.array(sorted(d2.keys()))

    close1 = closest_indices(k1 ,k2)
    close2 = closest_indices(k2 ,k1)

    # links = [(d1[k1[i]], d2[k2[val]]) for i, val in enumerate(close1) if close2[val] == i]
    links = []
    for i, val in enumerate(close1):
        if close2[val] == i:
            links.append((k1[i], k2[val]))
    return links



if __name__ == '__main__':
    path = sys.argv[1]
    slash_loc = [pos for pos, char in enumerate(path) if char == '/']
    if len(slash_loc) == 0:
        slash_loc = [0]
    folder = path[:slash_loc[-1]+1]
    file = path[slash_loc[-1]+1:]

    init_gui(folder, file)
