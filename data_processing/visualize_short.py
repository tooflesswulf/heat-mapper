import matplotlib.pyplot as plt
import pickle
import os
import numpy as np
import sys

summ_loc = sys.argv[1]

maxes = pickle.load(open(summ_loc+'maxes.pkl', 'rb'))
bigmeans = pickle.load(open(summ_loc+'bigmeans.pkl', 'rb'))
bigmins = pickle.load(open(summ_loc+'bigmins.pkl', 'rb'))
bigstds = pickle.load(open(summ_loc+'bigstds.pkl', 'rb'))
bigmedians = pickle.load(open(summ_loc+'bigmedians.pkl', 'rb'))

plt.figure('big min, mean, max, and stddev')
plt.errorbar(np.arange(bigmeans.shape[0]), bigmeans, yerr = bigstds, errorevery=100, elinewidth=1,
	label='Mean and 1 SD')
plt.plot(bigmins, label = 'Guessed min.')
plt.plot(maxes, label='Max')
plt.plot(bigmedians, label='Median')
plt.legend(bbox_to_anchor=(1.05, 1), loc=0, borderaxespad=0.)

plt.show()
