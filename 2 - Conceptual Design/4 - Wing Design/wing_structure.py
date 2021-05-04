"""Main wing-spar Euler-Bernoulli beam analysis."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as font_manager

from ambiance import Atmosphere

sns.set_theme(style='darkgrid', font='Palatino Linotype', context='paper')
FONT_FILE = 'C:/Windows/Fonts/pala.ttf'
font_manager.fontManager.addfont(FONT_FILE)


# %% Problem constants

H = 640  # m AMSL
g = Atmosphere(H).grav_accel[0]  # m/s^2

W0 = 10  # kg
AR = 11
WL = 23.239  # kg/m^2
S = W0/WL  # m^2
b = round(np.sqrt(S*AR), 3)  # m
dy = 0.01  # m
y_array = np.arange(0, b/2, dy)

FOS = 1.5
n_p = 3.5
n_m = -1

L = W0*g
Lv = L/2*FOS
Lr = L/(np.pi/4*b)
L_array = n_p*Lr*np.sqrt(1 - (2*y_array/b)**2)

E = 70E9  # Pa
r_o_array = np.array([0.7, 0.825, 0.997, 1.12, 1.245])/2 * 0.0254 # m
r_i_array = (np.array([0.7, 0.825, 0.997, 1.12, 1.245])/2 - 0.037) * 0.0254 # m

# %% Beam analysis

V_array = np.empty(np.size(y_array))
M_array = np.empty(np.size(y_array))
V_array[0] = 0
M_array[0] = 0
for i in range(len(y_array) - 1):
    V_array[i+1] = V_array[i] - dy*L_array[::-1][i]
    M_array[i+1] = M_array[i] - dy*V_array[i]
V_array = V_array[::-1]
M_array = M_array[::-1]

Mv_array = Lv*(b/2 - y_array)
Vv_array = -Lv*np.ones(np.size(y_array))

fig = plt.figure(dpi=1200)
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

ax1.plot(y_array, L_array)
#ax1.plot([y_array[-1], y_array[-1]], [0, Lv])
ax1.set_xlim(left=0)
ax1.set_xticklabels([])
ax1.set_ylabel('L, N')
ax1.legend([r'$\mathdefault{n_{max}}$', 'Hover'])

ax2.plot(y_array, V_array)
#ax2.plot(y_array, Vv_array)
ax2.set_xlim(left=0)
ax2.set_xticklabels([])
ax2.set_ylabel('V, N')

ax3.plot(y_array, M_array)
#ax3.plot(y_array, Mv_array)
ax3.set_xlim(left=0)
ax3.set_ylabel(r'$\mathdefault{M,~N~m}$')
ax3.set_xlim(left=0)
ax3.set_xlabel('y, m')

v_max_array = np.empty(np.size(r_o_array))
sigma_max_array = np.empty(np.size(r_o_array))
sigma_max_v_array = np.empty(np.size(r_o_array))
v_max_v_array = np.empty(np.size(r_o_array))

for k, r in enumerate(r_o_array):
    theta_array = np.empty(np.size(y_array))
    v_array = np.empty(np.size(y_array))
    theta_array[0] = 0
    v_array[0] = 0

    theta_v_array = np.empty(np.size(y_array))
    v_v_array = np.empty(np.size(y_array))
    theta_v_array[0] = 0
    v_v_array[0] = 0

    I_xx = np.pi/4*(r_o_array[k]**4 - r_i_array[k]**4)  # m^4

    for i in range(len(y_array) - 1):
        theta_array[i+1] = theta_array[i] + dy*M_array[i]/(E*I_xx)
        theta_v_array[i+1] = theta_v_array[i] + dy*Mv_array[i]/(E*I_xx)
        v_array[i+1] = v_array[i] + dy*theta_array[i]
        v_v_array[i+1] = v_v_array[i] + dy*theta_v_array[i]

    v_max_array[k] = np.max(v_array)
    sigma_max_array[k] = np.max(M_array)*r_o_array[k]/I_xx

    v_max_v_array[k] = np.max(v_v_array)
    sigma_max_v_array[k] = np.max(Mv_array)*r_o_array[k]/I_xx


fig = plt.figure(dpi=1200)
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

ax1.plot(r_o_array*2E3, sigma_max_array*1E-6)
#ax1.plot(r_o_array*2E3, sigma_max_v_array*1E-6)
ax1.set_ylabel(r'$\mathdefault{\sigma_{b_{max}},~MPa}$')
ax1.set_xlim(left=r_o_array[0]*2E3)
ax1.set_ylim(bottom=0)
ax1.set_xticklabels([])
ax1.legend([r'$\mathdefault{n_{max}}$', 'Hover'])

ax2.plot(r_o_array*2E3, v_max_array)
#ax2.plot(r_o_array*2E3, v_max_v_array)
ax2.set_xlabel('D, mm')
ax2.set_ylabel(r'$\mathdefault{\delta_{max},~m}$')
ax2.set_xlim(left=r_o_array[0]*2E3)
#ax2.set_ylim(0, 0.)
