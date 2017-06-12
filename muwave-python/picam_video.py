# USAGE

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import cv2
from datetime import datetime

from PIL import Image

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 80
rawCapture = PiRGBArray(camera, size=(320, 240))

# allow the camera to warmup
time.sleep(0.1)

file_name_root = "framerateTest"

i = 0

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array

	# show the frame
	cv2.imshow("Frame", image)

	key = cv2.waitKey(1) & 0xFF

	#with open(file_name_root + '_picam_npsave.dat','a') as picam_file:
        #	np.save(picam_file, image)
	#with open(file_name_root + '_picam.dat','a') as picam_file:
	#	picam_file.write(image) 

	#np.save("picam_frames/" + file_name_root + "_" + str(i) + "_" + str(datetime.utcnow()), image) 
	#np.savetxt("picam_frames/" + file_name_root + "_" + str(i) + "utc", datetime.utcnow() ) 
	
	t = datetime.utcnow()
	#np.save("picam_frames/" + file_name_root + "_" + str(i), [ image , (t - datetime(1970, 1, 1)).total_seconds() ]  )

	#frame.save("out.jpg", "JPEG", quality=80, optimize=True)

	i += 1

	if i == 30:
		timeNow = datetime.utcnow()


	if i == 80:
		timeUpdate = datetime.utcnow()	

	#if i == 81:
	#	print 50. / (timeUpdate - timeNow).total_seconds()
	#	break

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
    	    break


#dat_file.close()
del(camera)
del(rawCapture)
