"""Generate airfoil data for later use."""

import os
import numpy as np

from aerodynamics_toolbox import runXfoil
from aircraft_plotter import naca_4_series

Re_array = np.arange(100000, 100001, 100000)

max_cam_array = np.arange(5.5, 6, 0.50)
max_cam_loc_array = np.arange(4.5, 5, 0.50)
max_tc_array = np.arange(19, 25.5, 0.5)

for Re in Re_array:
    Re_dir_name = 'airfoil_data/{0}'.format(Re)
    if not os.path.exists(Re_dir_name):
        os.mkdir(Re_dir_name)

    for max_cam in max_cam_array:
        max_cam_dir_name = Re_dir_name + '/{0:.2f}'.format(max_cam)
        if not os.path.exists(max_cam_dir_name):
            os.mkdir(max_cam_dir_name)

        for max_cam_loc in max_cam_loc_array:
            max_cam_loc_dir_name = max_cam_dir_name + '/{0:.2f}'.format(
                max_cam_loc)
            if not os.path.exists(max_cam_loc_dir_name):
                os.mkdir(max_cam_loc_dir_name)

            for max_tc in max_tc_array:
                max_tc_dir_name = max_cam_loc_dir_name + '/{0:.2f}.txt'.format(
                    max_tc)

                i = 0
                while np.size(np.loadtxt(max_tc_dir_name)) == 0 or not\
                        np.loadtxt(max_tc_dir_name)[:, 0][-1] >= 2.5:

                    np.savetxt('xfoil/{0}.dat'.format(max_tc), naca_4_series(
                        max_cam, max_cam_loc, max_tc, 50+i), fmt='%.4f')
                    np.savetxt(max_tc_dir_name, runXfoil(
                        '{0}'.format(max_tc), Re, -5, 5, 0.25), fmt='%.4f')
                    i += 1
                    print(i)
