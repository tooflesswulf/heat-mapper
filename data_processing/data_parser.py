import numpy as np
import pickle
import sys
import os

def parse_data(fname):
	print('Opening file at: '+fname)

	dt = np.dtype( [('w', np.intc),
					('h', np.intc),
					('low',np.intc),
					('high',np.intc),
					('int_temp',np.intc),
					('pad',np.intc),
					('time','d'),
					('img', np.uint16, (160*120,))
					])

	a = np.fromfile(fname, dtype=dt)
	img = a['img'].reshape(-1,120,160)
	# img = img.reshape(100,-1)
	print("Number of images: {}".format(img.shape[0]))
	return img, a['time']

def conv_celsius(temps):
	r=395653
	b = 1428
	f = 1
	o = 156
	t_k = b / np.log(r / (temps - o) + f)
	return t_k - 273.15




if __name__ == '__main__':
	args = sys.argv[1:]
	summ_loc = 'summary/'

	save = True
	if args[0] == '-nosave':
		save = False
		del args[0]

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

	period_loc = [pos for pos, char in enumerate(fname) if char == '.']
	slash_loc = [pos for pos, char in enumerate(fname) if char == '/']
	if len(slash_loc) == 0:
		slash_loc = [0]
	folder = fname[:slash_loc[-1]+1]

	img, times = parse_data(fname)
	threshold = 1000

	if save:
		img_celsius = conv_celsius(img)
		to_disp = img_celsius[id]
	else:
		to_disp = conv_celsius(img[id])
		print('Displaying image number: {}'.format(id))
		print('This frame was taken at t={} after the start of the program.'.format(times[id]-times[0]))

	avg = np.mean(to_disp)
	# to_disp[np.abs(to_disp - avg) > threshold] = avg + 999

	print("Mean value: {}".format(avg))



	if not save:
		plt.figure("Image number {}".format(id))
		mean = np.mean(to_disp)
		std = np.std(to_disp)
		raw = to_disp.copy()

		to_disp[to_disp < mean + .35*std] = np.nan
		plt.subplot(121)
		plt.imshow(to_disp, vmin = np.amin(raw))
		plt.subplot(122)
		plt.imshow(raw)
		plt.show()


	if not save:
		sys.exit('Not saving anything.')

	i = 0
	counter = 1;
	while(i < img_celsius.shape[0]):
		pfn = '{}pkl/{}_{}.pkl'.format(folder, fname[slash_loc[-1]+1:period_loc[-1]], counter)
		print("Saving images into " + pfn)
		if(i+250 <= img_celsius.shape[0]):
			with open(pfn, 'wb') as f:
				pickle.dump(img_celsius[i:i+250], f)
		else:
			with open(pfn, 'wb') as f:
				pickle.dump(img_celsius[i:], f)
		i += 250
		counter += 1

	# print("Saving images into " + pickle_fname)
	# with open(pickle_fname, 'wb') as f:
	# 	pickle.dump(img_celsius, f)

	flatdat = img_celsius.reshape(-1, 120*160)
	maxes = np.amax(flatdat, axis=1)
	means = np.mean(flatdat, axis=1)
	stds = np.std(flatdat, axis=1)
	# medians = np.median(flatdat, axis=1)

	onlybig = (flatdat.T - (means + 1.5*stds)).T
	onlybig[onlybig < 0] = np.nan
	onlybig = (onlybig.T + (means + 1.5*stds)).T

	bigmeans = np.nanmean(onlybig, axis=1)
	bigstds = np.nanstd(onlybig, axis=1)
	bigmins = np.nanmin(onlybig, axis=1)
	bigmedians = np.nanmedian(onlybig, axis=1)

	print("Saving summary statistics...")
	pickle.dump(maxes, open(folder+summ_loc+'maxes'+'.pkl', 'wb'))
	pickle.dump(bigmeans, open(folder+summ_loc+'bigmeans'+'.pkl', 'wb'))
	pickle.dump(bigstds, open(folder+summ_loc+'bigstds'+'.pkl', 'wb'))
	pickle.dump(bigmins, open(folder+summ_loc+'bigmins'+'.pkl', 'wb'))
	pickle.dump(bigmedians, open(folder+summ_loc+'bigmedians'+'.pkl', 'wb'))
	pickle.dump(times, open(folder+summ_loc+'times'+'.pkl', 'wb'))
	print("Done.")



