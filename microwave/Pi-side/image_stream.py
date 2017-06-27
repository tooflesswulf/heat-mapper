# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2
import subprocess
from subprocess import Popen
import pickle

therm_fname = 'thermal'
warp_const = pickle.load(open('persp_mat.p','rb'))

dt = np.dtype( [('w', np.intc),
                ('h', np.intc),
                ('low',np.intc),
                ('high',np.intc),
                ('int_temp',np.intc),
                ('pad',np.intc),
                ('time','d'),
                ('img', np.uint16, (160*120,))
                ])

def conv_celsius(temps):
    r=395653
    b = 1428
    f = 1
    o = 156
    t_k = b / np.log(r / (temps - o) + f)
    return t_k - 273.15

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.vflip = True
camera.hflip = True
camera.resolution = (640, 480)
r, c = camera.resolution
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(r, c))
thermstream = Popen('~/heat-mapper/leptoncam/leptonTest '+therm_fname, stdout=subprocess.PIPE, shell=True)


print('leptonTest pid: ', thermstream.pid)

# allow the camera to warmup
time.sleep(0.1)

therm_img = np.zeros((120,160))
therm_disp = np.zeros((r,c))
therm_seg = therm_disp.copy()
i = 0
t = 0

def on_click(event, x, y, flags, param):
    if event==cv2.EVENT_LBUTTONDOWN:
        print("LOCATION: ({}, {})\nDISP TEMP:{}\tDETECTED LEVEL:{}\tMAX TEMP:{}".format(
                x, y, therm_disp[y, x], therm_seg[y,x], np.amax(therm_disp)))

cv2.namedWindow("Thermal")
cv2.setMouseCallback("Thermal", on_click)


def process_thermal(therm_img):
    global therm_disp
    global therm_seg
    th = np.rot90(conv_celsius(therm_img))
    chunks = get_chunk_thresholds(th)
    segmented = th.copy()
    for i, (e1, e2) in enumerate(zip(chunks[:-1], chunks[1:])):
        segmented[(e1 <= th) & (th <= e2)] = i
    therm_disp = cv2.warpPerspective(th, warp_const, dsize = (r,c))
    therm_seg = cv2.warpPerspective(segmented, warp_const, dsize = (r,c))
    return th

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

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
 
    try:
        a = np.fromfile(therm_fname + '.dat', dtype=dt)
        t = a['time'][-1]
        therm_raw = a['img'].reshape(-1,120,160)[-1]
        therm_img = process_thermal(therm_raw)

    except IndexError:
        print('Thermal stream not started yet.')

    # show the frame
    cv2.imshow("Thermal", therm_seg/np.amax(therm_seg))
    cv2.imshow("Thermal RAW", therm_img/np.amax(therm_img))
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    if key == ord("s"):
        pickle.dump((t,therm_img), open('therm{}.pkl'.format(i), 'wb'))
        pickle.dump((t, image), open('rgb{}.pkl'.format(i), 'wb'))
        i+=1
        print('Saved current images.')

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

print('Terminating thermal stream.')
thermstream.kill()


