import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
import sys
import os
from heatmap_splicer import get_sliced_images
from matplotlib.collections import PolyCollection


if __name__ == '__main__':
	args = sys.argv[1:]

	try:
		fname = args[0]
		if not os.path.exists(fname):
			fname = 'Test.dat'
	except:
		fname = 'Test.dat'
		id = 0

	zs = np.arange(000, 2501, 300)

	splices = []
	for i in zs:
		sliced = get_sliced_images(fname, i)
		sliced = np.hstack([a.flatten() for a in sliced])
		splices.append(sliced)
	splices = np.array(splices)

	# LOL ONE LINE SPAGHETTI
	# splices = np.array([	np.hstack([a.flatten() for a in get_sliced_images(fname, i)])
	# 				for i in np.arange(2000, 8001, 500)])


	print(splices.shape)
	verts = []
	for z, s in zip(zs, splices):
		vals, bins = np.histogram(s, bins=50)
		to_app = [(0,0)] + list(zip(bins, vals)) + [(2*bins[-1]-bins[-2],0)]

		verts.append(to_app)
	colors = cm.rainbow(1-np.linspace(0, 1, len(zs)))

	poly = PolyCollection(verts, alpha=.7, facecolors=colors)
	fig = plt.figure()
	ax = fig.gca(projection='3d')
	ax.add_collection3d(poly, zs=zs, zdir='y')
	ax.set_xlabel('X (temp)')
	ax.set_xlim3d(0,60)
	ax.set_ylabel('Y (time)')
	ax.set_ylim3d(0,3000)
	ax.set_zlabel('Z (time)')
	ax.set_zlim3d(0,800)

	plt.show()







