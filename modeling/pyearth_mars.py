from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import scipy.io as spio
import pyearth
from IPython import embed

ndimx = 2
path = './vdp/sim_data/'
#mat = spio.loadmat(path+'vdp_data_1e3_t05.mat')
#mat = spio.loadmat(path+'vdp_data_1e4_t05.mat')
#mat = spio.loadmat(path+'vdp_data_1e5_t05.mat')
#mat = spio.loadmat(path+'vdp_data_1e6_t05.mat')

#mat = spio.loadmat(path+'vdp_data_1e3_t02.mat')
mat = spio.loadmat(path+'vdp_data_1e4_t02.mat')

X, Y = mat['Y_summary'][:, 0:ndimx], mat['Y_summary'][:, ndimx:ndimx+ndimx]
y0, y1 = Y[:, 0], Y[:, 1]

#X, y0, y1 = mat['X'], mat['Y'][:, 0], mat['Y'][:, 1]

#model0 = pyearth.Earth(penalty=0, max_degree=3, verbose=2, thresh=1e-3, check_every=1)
#model1 = pyearth.Earth(penalty=0,  max_degree=3, verbose=2,check_every=1, feature_importance_type='rss')
model0 = pyearth.Earth(penalty=0, max_degree=2, verbose=1, thresh=1e-4)
model1 = pyearth.Earth(penalty=0,  max_degree=4, verbose=1, thresh=1e-4)
model0.fit(X, y0)
embed()
model1.fit(X, y1)

#print(model0.trace())
print(model0.summary())
print('='*50)
#print(model1.trace())
print(model1.summary())

y0_ = model0.predict(X)
y1_ = model1.predict(X)

n = X.shape[0]
idxs = np.random.randint(0, n, int(01*n))

fig = plt.figure()
fig.suptitle('y0')
ax = fig.add_subplot(2, 1, 1, projection='3d')
#ax.plot_surface(xx1, xx2, np.reshape(yy0, (xx1.shape)))
#ax.plot(X[idxs, 0], X[idxs, 1], y0[idxs], 'y.')
ax.plot(X[idxs, 0], X[idxs, 1], y0[idxs], 'b.')
ax.plot(X[idxs, 0], X[idxs, 1], y0_[idxs], 'y.')
ax.set_title('y0 vs x')
ax.set_xlabel('x0')
ax.set_ylabel('x1')
ax.set_zlabel('y0')

ax = fig.add_subplot(2, 1, 2, projection='3d')
#ax.plot_surface(xx1, xx2, np.reshape(yy1, (xx1.shape)))
ax.plot(X[idxs, 0], X[idxs, 1], y1[idxs], 'b.')
ax.plot(X[idxs, 0], X[idxs, 1], y1_[idxs], 'y.')
ax.set_title('y1 vs x')
ax.set_xlabel('x0')
ax.set_ylabel('x1')
ax.set_zlabel('y1')

fig = plt.figure()
plt.plot(X[idxs, 0], y1[idxs], 'b.')
plt.plot(X[idxs, 0], y1_[idxs], 'y.')

# plt.plot(X[0:100, 1], y0[0:100], 'b.')
# plt.plot(X[0:100, 1], y0_[0:100], 'r.')

# plt.figure()
# plt.plot(X[0:100, 1], y1[0:100], 'b.')
# plt.plot(X[0:100, 1], y1_[0:100], 'r.')
# plt.title('y1')

plt.show()
