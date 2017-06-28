# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2
import subprocess
from subprocess import Popen
import pickle
import threading

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
# therm_seg = therm_disp.copy()
images_list = []
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
    therm_disp = cv2.warpPerspective(th, warp_const, dsize = (r,c))
    return th


def check_splatter(images):
    assert images.shape[0] >= 3
    to_check = conv_celsius(images[-3:])
    diff = to_check[1] - 0.5*to_check[0] - 0.5*to_check[2]
    rmse = np.sqrt(np.mean(diff ** 2, axis=1))
    return rmse > 1.5


# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
 
    try:
        a = np.fromfile(therm_fname + '.dat', dtype=dt)
        t = a['time'][-1]
        therm_raw = a['img'].reshape(-1,120,160)[-3:]
        therm_img = process_thermal(therm_raw[-1])

    except IndexError:
        print('Thermal stream not started yet.')

    # show the frame
    cv2.imshow("Thermal", therm_disp/np.amax(therm_disp))
    # cv2.imshow("Thermal RAW", therm_img/np.amax(therm_img))
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


