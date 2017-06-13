import numpy as np
import pickle

dt = np.dtype( [('w', np.intc),
				('h', np.intc),
				('low',np.intc),
				('high',np.intc),
				('int_temp',np.intc),
				('time','d'),
				('pad',np.intc),
				('img', np.uint16, (160*120,))
				])

a = np.fromfile('Test.dat', dtype=dt)

imgarr = a['img']

print(imgarr[...,12345])

pickle.dump(imgarr, open('images.p', 'wb'))
print('written')
