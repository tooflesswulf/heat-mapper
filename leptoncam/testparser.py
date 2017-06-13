import numpy as np

#with open('Test.dat', 'rb') as f:
#  print(f.read())

dt = [('w', np.intc),('h', np.intc),('low',np.intc),('high',np.intc),('int_temp',np.intc),('time','d'),('??',np.intc)]

# dtimg = [('img',np.uint16)]*80*60
dtimg = []
for i in range(80*60):
	dtimg.append(('im{}'.format(i), np.uint16))

print(len(dt + dtimg))

dtype = dt+dtimg

a = np.fromfile('Test.dat', dtype=dtype)
a = np.array(a)

def first6(tup):
	return tup[0], tup[1], tup[2], tup[3], tup[4], tup[5]

magicnum = 4800
for entry in a:
	print(first6(entry))