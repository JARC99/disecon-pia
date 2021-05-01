import numpy as np
import matplotlib.pyplot as plt

from aircraft_plotter import naca_4_series 

af_coords = naca_4_series(0, 0, 15, 101)

af_ords = af_coords[:, 1]

fuse_rads = ((np.abs(af_ords)))**(3/2)*10
fuse_rads = np.hstack((fuse_rads[:100], -fuse_rads[100:]))

fuse_len = 0.6


fig = plt.figure(dpi=1200)
ax = fig.add_subplot(111)
ax.plot(af_coords[:, 0]*fuse_len, af_ords*fuse_len)
ax.plot(af_coords[:, 0]*fuse_len, fuse_rads*fuse_len)
ax.axis('equal')
