import matplotlib.pyplot as plt
import pickle
import numpy as np
import sys
from data_parser import parse_data, conv_celsius
import cv2
from matplotlib.widgets import Slider
import os

args = sys.argv[1:]
summ_loc = 'summary/'
save_loc = 'summary/slices/'

fname = args[0]
period_loc = [pos for pos, char in enumerate(fname) if char == '.']
slash_loc = [pos for pos, char in enumerate(fname) if char == '/']
if len(slash_loc) == 0:
    slash_loc = [0]
folder = fname[:slash_loc[-1] + 1]

maxes = pickle.load(open(folder+summ_loc+'maxes.pkl', 'rb'))
bigmeans = pickle.load(open(folder + summ_loc + 'bigmeans.pkl', 'rb'))
bigmins = pickle.load(open(folder + summ_loc + 'bigmins.pkl', 'rb'))
bigstds = pickle.load(open(folder + summ_loc + 'bigstds.pkl', 'rb'))
bigmedians = pickle.load(open(folder + summ_loc + 'bigmedians.pkl', 'rb'))

images, times = parse_data(fname)
images = conv_celsius(images)

disp = {}
disp['thresh'] = 0
disp['marker'] = -1


def show_summary():
    plt.clf()
    plt.gcf().canvas.set_window_title('Summary')

    n = bigmeans.shape[0]
    plt.errorbar(np.arange(n), bigmeans, yerr=bigstds, errorevery=n // 40, elinewidth=1,
                 label='Mean and 1 SD')
    plt.plot(bigmins, label='Guessed min.')
    plt.plot(maxes, label='Max')
    plt.plot(bigmedians, label='Median')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=0, borderaxespad=0.)

    disp['mode'] = 'summary'
    plt.draw()


def show_img():
    plt.clf()
    plt.gcf().canvas.set_window_title('Frame number {}'.format(disp['loc']))
    plt.imshow(images[disp['loc']])
    plt.draw()

    disp['mode'] = 'image'


# Calculates several
def get_segments():
    im = images[disp['loc']]
    threshval = disp['thresh']
    markerid = disp['marker']

    thresh = cv2.convertScaleAbs((im > threshval).astype(int))
    ret, markers = cv2.connectedComponents(thresh)

    if markerid != -1:
        thresh[markers != markerid] = 0

    ylocs, xlocs = np.where(thresh)  # where filtered.nonzero()
    try:
        x_minmax = np.amin(xlocs), np.amax(xlocs) + 1
        y_minmax = np.amin(ylocs), np.amax(ylocs) + 1
    except ValueError:
        slice_zone = None
    else:
        slice_zone = slice(*y_minmax), slice(*x_minmax)

    maskimg = im * thresh
    reversemask = im * (1 - thresh)

    return im, maskimg, markers+reversemask, slice_zone


def show_segments():
    plt.clf()
    plt.gcf().canvas.set_window_title('Inspecting frame number {}'.format(disp['loc']))

    im, maskimg, cutout, slicezone = get_segments()

    plt.subplot(221)
    plt.imshow(im)
    plt.subplot(222)
    mask = plt.imshow(maskimg)
    cutout_ax = plt.subplot(223)
    plt.imshow(cutout)
    final_ax = plt.subplot(224)
    if slicezone:
        plt.imshow(maskimg[slicezone])
        disp['final'] = maskimg[slicezone]
    elif 'final' in disp.keys():
        del disp['final']

    ax_cmin = plt.axes([0.25, 0.0, 0.65, 0.03])
    s_cmin = Slider(ax_cmin, 'Threshold value', 10, 40, valinit = disp['thresh'])

    def update():
        im, maskimg, cutout, slicezone = get_segments()

        mask.set_data(maskimg)
        cutout_ax.clear()
        cutout_ax.imshow(cutout)
        final_ax.clear()
        if slicezone:
            final_ax.imshow(maskimg[slicezone])
            disp['final'] = maskimg[slicezone]
        elif 'final' in disp.keys():
            del disp['final']

        plt.draw()

    def update_slider(val):
        disp['thresh'] = val
        disp['marker'] = -1
        update()

    def onclick_cutout(event):
        if event.inaxes == cutout_ax:
            im = cutout_ax.get_images()[0]
            marker_id = im.get_cursor_data(event)
            if marker_id == int(marker_id):
                disp['marker'] = int(marker_id)
                update()


    s_id = s_cmin.on_changed(update_slider)
    c_id = plt.gcf().canvas.mpl_connect('button_press_event', onclick_cutout)

    disp['slider'] = s_cmin
    disp['slider_listener'] = s_id
    disp['click_listener'] = c_id
    disp['mode'] = 'seg'
    plt.draw()


def onclick(event):
    if disp['mode'] == 'summary':
        onclick_summary(event)
    # if disp['mode'] == 'seg':
    #     if event.inaxes == disp['selection_axes']:
    #         x, y = event.xdata, event.ydata
    #         im = disp['selection_axes'].get_images()[0]
    #         print(im.get_cursor_data(event))
    #         print(x, y)


def onclick_summary(event):
    disp['loc'] = int(round(event.xdata))
    show_img()


def change_img(event):
    if disp['mode'] == 'image':
        if event.key == 'right':
            disp['loc'] += 1
            try:
                show_img()
            except IndexError:
                disp['loc'] -= 1
                print('You have reached the last frame.')
        elif event.key == 'left':
            if disp['loc'] == 0:
                print('You have reached the first frame.')
            else:
                disp['loc'] -= 1
                show_img()
        elif event.key in ['r', 'q']:
            show_summary()
            plt.draw()
        elif event.key == 's':
            show_segments()

    elif disp['mode'] == 'seg':
        if event.key in ['r', 'q']:
            disp['slider'].disconnect(disp['slider_listener'])
            plt.gcf().canvas.mpl_disconnect(disp['click_listener'])
            show_img()
        if event.key == 's':
            if 'final' in disp.keys():
                to_save = disp['final']
                frame_num = disp['loc']
                savefile = 'f' + str(frame_num).zfill(4) + '.pkl'
                print('Saving into ' + savefile + '.')
                if not os.path.exists(folder + save_loc):
                    os.makedirs(folder + save_loc)
                    print('Made folder ' + folder + save_loc)
                pickle.dump(to_save, open(folder + save_loc + savefile, 'wb'))

    elif disp['mode'] == 'summary':
        if event.key == 'q':
            plt.close()

fig = plt.figure(1)
show_summary()
cid = fig.canvas.mpl_connect('button_press_event', onclick)
cid2 = fig.canvas.mpl_connect('key_press_event', change_img)

plt.rcParams['keymap.save'] = ''
plt.show()
