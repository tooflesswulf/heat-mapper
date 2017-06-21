import matplotlib.pyplot as plt
import numpy as np
import pickle
import cv2
import sys
import os
from data_parser import parse_data, conv_celsius

summ_loc = 'summary/slices/'
zone = slice(10,-10), slice(10,-10)
zonename = ''
markerid = -1

def get_image(fname, id):
	data, times = parse_data(fname)
	print('Displaying image number: {}'.format(id))
	print('This frame was taken at t={}'.format(times[id]-times[0]))

	image = conv_celsius(data[id])
	return image

def segment_image(im, alt):
	data = cv2.convertScaleAbs(im)
	# ret, thresh = cv2.threshold(data,0,1,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
	if alt:
		thresh = cv2.convertScaleAbs((im > np.mean(im) + 1.25*np.std(im)).astype(int))
		thresh = cv2.convertScaleAbs((im > 31).astype(int))
	else:
		ret, thresh = cv2.threshold(data,0,1,cv2.THRESH_OTSU)
	# filtered = thresh*data

	ret, markers = cv2.connectedComponents(thresh)
	if markerid == -1:
		binc = np.bincount(markers.flatten())
		to_del = np.argwhere(binc < 10)
		for d in to_del:
			markers[markers==d] = 0
			thresh[markers==d] = 0
	else:
		markers[markers != markerid] = 0
		thresh = markers/np.amax(markers)

	ylocs, xlocs = np.where(markers) #where filtered.nonzero()
	x_minmax = np.amin(xlocs), np.amax(xlocs)+1
	y_minmax = np.amin(ylocs), np.amax(ylocs)+1
	slicezone = slice(*y_minmax), slice(*x_minmax)

	maskimg = im * thresh

	plt.figure()
	plt.subplot(221)
	plt.imshow(im)
	plt.subplot(222)
	plt.imshow(maskimg)
	plt.subplot(223)
	plt.imshow(markers)
	plt.subplot(224)
	plt.imshow(maskimg[slicezone])
	plt.show()

	return maskimg[slicezone]



if __name__ == '__main__':
	args = sys.argv[1:]
	save = False
	if args[-1][-1]=='s':
		save = True
		args[-1] = args[-1][:-1]

	alt = False
	if args[-1][-1]=='a':
		alt = True
		args[-1] = args[-1][:-1]

	try:
		fname = args[0]
		if os.path.exists(fname):
			try:
				id = int(args[1])
			except:
				id = 0
		else:
			fname = 'Test.dat'
			id = int(args[0])
	except:
		fname = 'Test.dat'
		id = 0
	try:
		markerid = int(args[2])
	except:
		markerid = -1

	slash_loc = [pos for pos, char in enumerate(fname) if char == '/']
	folder = fname[:slash_loc[-1]+1]


	im = get_image(fname, id)

	to_save = segment_image(im[zone], alt)
	if save:
		savefile = zonename+'f'+str(id).zfill(4)+'.pkl'
		print('Saving into '+savefile+'.')
		if not os.path.exists(folder+summ_loc):
			os.makedirs(folder+summ_loc)
			print('Made folder '+folder+summ_loc)
		pickle.dump(to_save, open(folder+summ_loc+savefile, 'wb'))


