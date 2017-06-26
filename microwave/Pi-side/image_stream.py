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

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.vflip = True
camera.hflip = True
camera.resolution = (640, 480)
r, c = camera.resolution
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(r, c))
thermstream = Popen('~/heat-mapper/leptoncam/leptonTest '+therm_fname, stdout=subprocess.PIPE, shell=True)

dt = np.dtype( [('w', np.intc),
				('h', np.intc),
				('low',np.intc),
				('high',np.intc),
				('int_temp',np.intc),
				('pad',np.intc),
				('time','d'),
				('img', np.uint16, (160*120,))
				])

print('leptonTest pid: ', thermstream.pid)

# allow the camera to warmup
time.sleep(0.1)
therm_img = np.zeros((120,160))

i = 0

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
 
    try:
        a = np.fromfile(therm_fname + '.dat', dtype=dt)
        therm_img = a['img'].reshape(-1,120,160)[-1]
        therm_img = therm_img * 100
        therm_img = np.rot90(therm_img)
        therm_img = cv2.warpPerspective(therm_img, warp_const, dsize=(r, c))
        # therm_img = cv2.resize(therm_img, (r,c))

    except IndexError:
        print('Thermal stream not started yet.')

    # show the frame
    cv2.imshow("Thermal", therm_img)
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    if key == ord("s"):
        pickle.dump(therm_img, open('therm{}.pkl'.format(i), 'wb'))
        pickle.dump(image, open('rgb{}.pkl'.format(i), 'wb'))
        i+=1
        print('Saved current images.')

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

print('Terminating thermal stream.')
thermstream.kill()
subprocess.call('rm {}*'.format(therm_fname))


