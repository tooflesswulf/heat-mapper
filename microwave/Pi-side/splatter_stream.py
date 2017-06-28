# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2
import subprocess
from subprocess import Popen
import pickle
import therm_frame_grabber
import threading



# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.vflip = True
camera.hflip = True
camera.resolution = (640, 480)
r, c = camera.resolution
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(r, c))

therm_fname = 'thermal'
thermstream = Popen('~/heat-mapper/leptoncam/leptonTest ' + therm_fname, stdout=subprocess.PIPE, shell=True)
print('leptonTest pid: ', thermstream.pid)

# allow the camera to warmup
time.sleep(0.1)

warp_const = pickle.load(open('persp_mat.p', 'rb'))
time_record_threshold = 5 #seconds
therm_disp = np.zeros((r, c))
images_list = [(0, np.zeros((r,c)))]
i = 0


def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("LOCATION: ({}, {})\nDISP TEMP:{}\tMAX TEMP:{}".format(
            x, y, therm_disp[y, x], np.amax(therm_disp)))
cv2.namedWindow("Thermal")
cv2.setMouseCallback("Thermal", on_click)


def image_grabber(images_in_memory=100):
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        image = frame.array
        t = time.time()
        images_list.append( (t, image) )
        if len(images_list) > images_in_memory:
            del images_list[0]

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
thread = threading.Thread(target=image_grabber)
thread.setDaemon(True)
thread.start()

splat_times = np.array([])
def onsplat(time):
    if any(np.abs(splat_times-time) < time_record_threshold):
        return
    np.append(splat_times, time)
    min_idx = next(idx for idx, x in enumerate(images_list) if x >= time - time_record_threshold)
    try:
        max_idx = next(idx for idx, x in enumerate(images_list[min_idx:]) if x <= time + time_record_threshold)
        max_idx += min_idx
    except StopIteration:
        to_save = images_list[min_idx:]
    else:
        to_save = images_list[min_idx:max_idx]
    pickle.dump(to_save, open('splatter_t_{}'.format(time)))
    print('Splatter detected. Images saved.')

thermal = therm_frame_grabber.start_thread(onsplat)


while True:
    therm_img = thermal.value
    pi_t, pi_img = images_list[-1]
    therm_disp = cv2.warpPerspective(therm_img, warp_const, dsize=(r,c))
    cv2.imshow('Thermal', therm_disp / np.amax(therm_disp))
    cv2.imshow('Frame', pi_img)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        t = thermal.time
        pickle.dump((t, therm_img), open('therm{}.pkl'.format(i), 'wb'))
        pickle.dump((t, pi_img), open('rgb{}.pkl'.format(i), 'wb'))
        i += 1
        print('Saved current images.')

    if key == ord("q"):
        break

print('Terminating thermal stream.')
thermstream.kill()

print('Splatters detected at the following times:')
for t in splat_times:
    print(t)
