import stirrer
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
import threading
import sys

img_store_loc = 'chicken/'

try:
    msg = sys.argv[1]

except IndexError:
    show = True
else:
    if msg in ['show', '-show', '-s']:
        show = True
    else:
        show = False

def is_ready(s):
    return s.getCurrentPos()[0]==98

def wait_ready(s):
    while not is_ready(s):
        pass

def save_img(img, name):
    cv2.imwrite(name, img)


lastsave = 0
def img_thread(img, save_freq = .5):
    if threading.active_count() < 20: #Maximum 20 threads
        global lastsave
        timestamp = time.time()
        if timestamp - lastsave > save_freq:
            lastsave = timestamp
            save_name = img_store_loc + 'chicken_{}.jpg'.format(timestamp)
            thread = threading.Thread(target=save_img, args=[img, save_name])
            thread.start()
    else:
        print('Too many threads! Aborting.')


s = stirrer.StirrerControl(port='/dev/ttyUSB0',addr=1)
wait_ready(s)
s.controlLights(3)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1280, 960)
camera.framerate = 32
camera.vflip = True
camera.hflip = True
rawCapture = PiRGBArray(camera, size=camera.resolution)

# allow the camera to warmup
time.sleep(0.1)

s.moveAbsPos(4200)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    img_thread(image)

    # show the frame
    if show:
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF


    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if show and key == ord("q"):
        break
    if is_ready(s):
        break

s.close()