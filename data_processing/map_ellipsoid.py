from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pickle

path = 'potato_data/surface_map_1/summary/slices/'
f = pickle.load(open(path+'f120.p','rb'))
r = pickle.load(open(path+'f150.p','rb'))
d = pickle.load(open(path+'f200.p','rb'))
l = pickle.load(open(path+'f240.p','rb'))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Make data
lx, ly = f.shape
u = np.linspace(0, 2*np.pi/3, lx)
v = np.linspace(0, np.pi, ly)
x = 2 * np.outer(np.cos(u), np.sin(v))
y = 2 * np.outer(np.sin(u), np.sin(v))

z = 3 * np.outer(np.ones(np.size(u)), np.cos(v))

ax.plot_surface(x, y, z, facecolors=cm.viridis(f/np.max(f)))
ax.set_xlim3d(-3,3)
ax.set_ylim3d(-3,3)
ax.set_zlim3d(-3,3)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')


plt.show()
