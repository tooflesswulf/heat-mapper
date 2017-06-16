import matplotlib.pyplot as plt
import pickle
import os
import numpy as np

basename = 'cheese_data/still (4)/'
pkl_loc = 'pkl/cheese_'
summ_loc = 'summary/'

dat = pickle.load(open('{}{}.pkl'.format(basename+pkl_loc, 1), 'rb'))
for i in range(2, 12):
	to_add = pickle.load(open('{}{}.pkl'.format(basename+pkl_loc, i), 'rb'))
	dat = np.append(dat, to_add, axis=0)
	print(dat.shape)

flatdat = dat.reshape(-1, 120*160)
maxes = np.amax(flatdat, axis=1)
means = np.mean(flatdat, axis=1)
stds = np.std(flatdat, axis=1)
medians = np.median(flatdat, axis=1)

onlybig = (flatdat.T - (means + 1.5*stds)).T
onlybig[onlybig < 0] = np.nan
onlybig = (onlybig.T + (means + 1.5*stds)).T

bigmeans = np.nanmean(onlybig, axis=1)
bigstds = np.nanstd(onlybig, axis=1)
bigmins = np.nanmin(onlybig, axis=1)
bigmedians = np.nanmedian(onlybig, axis=1)

# pickle.dump(maxes, open(basename+summ_loc+'maxes'+'.pkl', 'wb'))
# pickle.dump(bigmeans, open(basename+summ_loc+'bigmeans'+'.pkl', 'wb'))
# pickle.dump(bigstds, open(basename+summ_loc+'bigstds'+'.pkl', 'wb'))
# pickle.dump(bigmins, open(basename+summ_loc+'bigmins'+'.pkl', 'wb'))
# pickle.dump(bigmedians, open(basename+summ_loc+'bigmedians'+'.pkl', 'wb'))


# # plt.figure('Max')
# # plt.plot(maxes)
# # plt,subplot(212)
# # plt.figure('Means')
# # plt.plot(means)
# # plt.figure('Medians')
# # plt.plot(medians)

# plt.figure('big min, mean, max, and stddev')
# plt.errorbar(np.arange(bigmeans.shape[0]), bigmeans, yerr = bigstds, errorevery=100, elinewidth=1,
# 	label='Mean and 1 SD')
# plt.plot(bigmins, label = 'Guessed min.')
# plt.plot(maxes, label='Max')
# plt.plot(bigmedians, label='Guessed median.')
# # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# plt.show()
