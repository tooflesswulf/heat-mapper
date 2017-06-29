import stirrer
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
import threading

img_store_loc = 'chicken/'

def is_ready(s):
    return s.getCurrentPos()[0]==98

def wait_ready(s):
    while not is_ready(s):
        pass

def save_img(img):
    timestamp = time.time()
    cv2.imwrite(img_store_loc + '{}.jpg'.format(timestamp), img)


def img_thread(img):
    if threading.active_count() < 20:
        thread = threading.Thread(target=save_img, args=[img])
        thread.start()
    else:
        print('Too many threads! Aborting.')


s = stirrer.StirrerControl(port='/dev/ttyUSB0',addr=1)
s.controlLights(3)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
camera.vflip = True
camera.hflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))

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
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    if is_ready(s):
        break

s.close()