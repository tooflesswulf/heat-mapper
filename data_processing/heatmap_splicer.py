import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
import sys
import os
import pickle
from data_parser import parse_data, conv_celsius
import cv2
from matplotlib.collections import PolyCollection


def get_image(fname, id):
	data, times = parse_data(fname)
	print('Displaying image number: {}'.format(id))
	print('This frame was taken at t={}'.format(times[id]-times[0]))

	image = conv_celsius(data[id])
	return image

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
 
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
 
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
 
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
 
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

def getgrad(im):
	sobelx = cv2.Sobel(im,cv2.CV_64F,1,0,ksize=5)
	sobely = cv2.Sobel(im,cv2.CV_64F,0,1,ksize=5)
	edges = np.sqrt(sobely**2 + sobelx**2)
	return edges

def imagerec_slices(fname, id):
	data = get_image(fname, id)

	data = cv2.convertScaleAbs(data)
	avgsob = getgrad(data)
	lapl_of_sobel = -cv2.Laplacian(avgsob,cv2.CV_64F)
	lapl_of_sobel[lapl_of_sobel<10] = 0
	lapl_of_sobel[lapl_of_sobel>80] = 80
	data2 = data - 2*np.amax(data)*lapl_of_sobel/np.amax(lapl_of_sobel)
	mean = np.mean(data)
	std = np.std(data)

	ret, thresh = cv2.threshold(data,0,1,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

	ret, sure_bg = cv2.threshold(data2, mean, 1,0)
	ret, sure_fg = cv2.threshold(data2, mean + 1*std, 1,0)


	# lapl = cv2.Laplacian(data,cv2.CV_64F)


	# im2 = data.copy()
	# im2[im2 < mean + .25*std] = np.nan


	fig = plt.figure()
	fig.add_subplot(221)
	plt.imshow(data2)
	# ax2 = fig.add_subplot(222)
	# ax2.imshow(lapl)
	fig.add_subplot(222)
	plt.imshow(data2*sure_bg)
	# plt.hist(data.flatten(), 50)
	fig.add_subplot(223)
	plt.imshow(data2*sure_fg)

	fig.add_subplot(224)
	plt.imshow(lapl_of_sobel)

	plt.show()


def get_sliced_images2(path):
	fnames = os.listdir(path)
	images = []
	for fn in fnames:
		if fn.endswith('.pkl'):
			images.append(pickle.load(open(path+fn, 'rb')))
	return images

def centered_slice(l1, l2):
	start = int((l1-l2)/2)
	end = int((l1+l2)/2)
	return slice(start, end)


def disp_sliced_images(fname, id):
	sliced_images = get_sliced_images2(fname)

	flat_vals = []
	shapes = []
	for a in sliced_images:
		flat_vals.append(a.flatten())
		shapes.append(a.shape)

	flat_vals = np.hstack(flat_vals)
	mx = np.amax(flat_vals)

	shapes = np.array(shapes).T
	x, y = np.amax(shapes, axis=1)
	newarr = np.zeros((len(sliced_images), x, y))
	for img, sto in zip(sliced_images, newarr):
		x2, y2 = img.shape
		sto[centered_slice(x, x2), centered_slice(y, y2)] = img

	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection='3d')
	fig2 = plt.figure()

	k = 1 #z-spacing on scatterplot
	for i, im in zip(range(len(newarr)), newarr):
		ax = fig2.add_subplot(4, 4, i+1)

		ax.imshow(im, vmin=0, vmax=mx)

		# x, y = im.shape
		nz = np.nonzero(im)
		locs = np.argwhere(im)[::1]
		yy, xx = locs.T
		ax1.scatter(xx, yy, k*i, alpha=.5, c=im[yy, xx], vmin=0, vmax=mx, depthshade=False)
	ax1.set_xlabel('x')
	ax1.set_ylabel('y')
	ax1.set_zlabel('z')
	ax1.set_zlim(1,5)
	plt.show()

if __name__ == '__main__':
	args = sys.argv[1:]

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
	disp_sliced_images(fname, id)
	# imagerec_slices(fname, id)

