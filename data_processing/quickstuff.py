import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys
from heatmap_splicer import get_sliced_images2 as rimages
from matplotlib import collections
from matplotlib import cm

def get_surfaces(path):
	fnames = ['1_f.p','2_r.p','3_b.p','4_l.p']
	images = [pickle.load(open(path+fn, 'rb')) for fn in fnames]
	return images

def get_first_nonzero(img, dir):
	# 2
	#3 1
	# 0
	proj = img
	if dir%2==0:
		proj = img.T
	to_ret = []
	for r in proj:
		ra = r
		if dir < 2:
			ra = r[::-1]
		for v in ra:
			if v!=0:
				to_ret.append(v)
				break
	return np.array(to_ret)



if __name__ == '__main__':
	args = sys.argv[1:]

	fname = args[0]
	slices = rimages(fname)
	surfs = get_surfaces(fname)
	yvals = [ np.linspace(0, s.shape[0], len(slices)+1,endpoint=False)[1:] for s in surfs ]

	plt.figure()
	for i in range(4):
		plt.subplot(221+i)
		plt.imshow(surfs[i])
		immax = np.amax(surfs[i])
		r, c = surfs[i].shape
		cent = c/2
		for y, im in zip(yvals[i], slices):
			imr, imc = im.shape
			if i%2==0:
				linsegs = np.linspace(cent-imc/2, cent+imc/2, imc+1)
			else:
				linsegs = np.linspace(cent-imr/2, cent+imr/2, imr+1)
			colors = get_first_nonzero(im, i)
			for start, stop, c in zip(linsegs[:-1], linsegs[1:], colors):
				xp, yp = zip((start, y), (stop, y))
				plt.plot(xp,yp, c=cm.viridis(c/np.amax(colors)))
	plt.show()


