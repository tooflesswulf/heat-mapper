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
import stirrer


s = stirrer.StirrerControl(port='/dev/ttyUSB0',addr=1)
s.waitReady()
s.controlLights(3)

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
default_time_record_threshold = 1.5 #seconds
therm_disp = np.zeros((r, c))
images_list = [(0, np.zeros((r,c)))]
i = 0


def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("LOCATION: ({}, {})\nDISP TEMP:{}\tMAX TEMP:{}".format(
            x, y, therm_disp[y, x], np.amax(therm_disp)))
cv2.namedWindow("Thermal")
cv2.setMouseCallback("Thermal", on_click)


def image_grabber(images_in_memory=200):
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


def get_nearby_images(time, thresh=default_time_record_threshold):
    while images_list[-1][0] <= time+thresh:
        pass
    try:
        min_idx = next(idx for idx, (t, im) in enumerate(images_list) if t >= time - thresh)
    except StopIteration:
        min_idx = 0
    try:
        max_idx = next(idx for idx, (t, im) in enumerate(images_list[min_idx:]) if t > time + thresh)
        max_idx += min_idx
    except StopIteration:
        to_save = images_list[min_idx:]
    else:
        to_save = images_list[min_idx:max_idx]
    return to_save

splat_times = np.array([])
def onsplat(time):
    global splat_times
    if any(np.abs(splat_times-time) < default_time_record_threshold*2):
        print('Splatter detected at {}. Images not saved due to proximity of another splatter.'.format(time))
        return
    splat_times = np.append(splat_times, time)
    to_save = get_nearby_images(time)

    pickle.dump(to_save, open('splatter_t_{}.pkl'.format(time), 'wb'))
    print('Splatter detected at {}. Images saved.'.format(time))

thermal = therm_frame_grabber.start_thread(onsplat)


def manual_save(t):
    to_save = get_nearby_images(t, 1)
    pickle.dump(to_save, open('manual_save_t_{}.pkl'.format(t), 'wb'))
    print('Done saving current images.')

while True:
    therm_img = thermal.value
    pi_t, pi_img = images_list[-1]
    therm_disp = cv2.warpPerspective(therm_img, warp_const, dsize=(r,c))
    cv2.imshow('Thermal', therm_disp / np.amax(therm_disp))
    cv2.imshow('Frame', pi_img)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        t = thermal.time
        print('Preparing to save curent images...')
        th = threading.Thread(target=manual_save, args=[t])
        th.start()

    if key == ord("q"):
        break

print('Terminating thermal stream.')
thermstream.kill()

print('Splatters detected at the following times:')
for t in splat_times:
    print(t)

s.close()
