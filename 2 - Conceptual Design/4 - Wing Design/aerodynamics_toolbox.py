"""Contains tools for conceptual level aerodynamic analysis."""

import os
import subprocess
import numpy as np

from scipy import interpolate


def runXfoil(airfoil_name, Re, alpha_min, alpha_max, alpha_step):
    """Run XFoil for the given geometry at the given flow conditions."""
    if os.path.exists('xfoil/polar_file.txt'):
        os.remove('xfoil/polar_file.txt')

    i, polar_file_size = 0, 0
    while polar_file_size == 0:
        input_file = open('xfoil/xfoil_input.in', 'w')
        input_file.write('LOAD {0}.dat\n'.format(airfoil_name))
        input_file.write(airfoil_name + '\n')
        input_file.write("PANE\n")
        input_file.write('OPER\n')
        input_file.write('Visc {0}\n'.format(Re))
        input_file.write("TYPE 1\n")
        input_file.write('PACC\n')
        input_file.write('polar_file.txt\n\n')
        input_file.write('ITER {0}\n'.format(100 + 10*i))
        input_file.write('ASeq {0} {1} {2}\n'.format(alpha_min, alpha_max,
                                                     alpha_step))
        input_file.write('\n\n')
        input_file.write('quit\n')
        input_file.close()

        subprocess.call('xfoil.exe < xfoil_input.in', shell=True, cwd='xfoil')

        polar_file = np.loadtxt('xfoil/polar_file.txt', skiprows=12)
        polar_file_size = np.size(polar_file)

        i += 1

        os.remove('xfoil/xfoil_input.in')
        os.remove('xfoil/{0}.dat'.format(airfoil_name))

    polar_array = np.vstack((
        np.flipud(polar_file[int(alpha_max*(1//alpha_step) + 1):, :]),
        polar_file[1:int(alpha_max*(1//alpha_step)+1), :]))
    
    alpha_array = polar_array[:, 0]
    cl_array = polar_array[:, 1]
    cd_array = polar_array[:, 2]
    
    

    return alpha_array, cl_array, cd_array


def interpolate_airfoil_polar(airfoil, Re):
    """Interpolate airfoil polar using existing airfoil database."""
    Re_array = np.arange(200000, 500000, 100000)

    max_cam_array = np.arange(0.0, 6.50, 0.50)
    max_cam_loc_array = np.arange(2.0, 6.5, 0.50)
    max_tc_array = np.arange(12, 25.50, 0.50)

    max_cam = airfoil[0]
    max_cam_loc = airfoil[1]
    max_tc = airfoil[2]

    Re_low = Re_array[Re_array < Re][-1]
    Re_high = Re_array[Re_array > Re][0]
    Re_lims = [Re_low, Re_high]

    max_cam_low = max_cam_array[max_cam_array <= max_cam][-1]
    max_cam_high = max_cam_array[max_cam_array >= max_cam][0]
    max_cam_lims = [max_cam_low, max_cam_high]

    max_cam_loc_low = max_cam_loc_array[max_cam_loc_array <= max_cam_loc][-1]
    max_cam_loc_high = max_cam_loc_array[max_cam_loc_array >= max_cam_loc][0]
    max_cam_loc_lims = [max_cam_loc_low, max_cam_loc_high]

    max_tc_low = max_tc_array[max_tc_array <= max_tc][-1]
    max_tc_high = max_tc_array[max_tc_array >= max_tc][0]

    for Re in Re_lims:
        for max_cam in max_cam_lims:
            for max_cam_loc in max_cam_loc_lims:
                polar_low = np.loadtxt(
                    'airfoil_data/{0}/{1:.2f}/{2:.2f}/{3:.2f}.txt'.format(
                        Re, max_cam, max_cam_loc, max_tc_low))
                polar_high = np.loadtxt(
                    'airfoil_data/{0}/{1:.2f}/{2:.2f}/{3:.2f}.txt'.format(
                        Re, max_cam, max_cam_loc, max_tc_high))
                slope_num = polar_high-polar_low
                if not slope_num.any():
                    polar = polar_low
                else:
                    polar = polar_low + (max_cam_loc - max_cam_loc_low) * \
                        slope_num/(max_cam_loc_high-max_cam_loc_low)

                np.savetxt(
                    'airfoil_interpolation/({0})({1:.2f})({2:.2f}).txt'.format(
                        Re, max_cam, max_cam_loc), polar)

            polar_low = np.loadtxt(
                'airfoil_interpolation/({0})({1:.2f})({2:.2f}).txt'.format(
                    Re, max_cam, max_cam_loc_low))
            polar_high = np.loadtxt(
                'airfoil_interpolation/({0})({1:.2f})({2:.2f}).txt'.format(
                    Re, max_cam, max_cam_loc_high))
            slope_num = polar_high-polar_low
            if not slope_num.any():
                polar = polar_low
            else:
                polar = polar_low + (max_cam_loc - max_cam_loc_low) * \
                    slope_num/(max_cam_loc_high-max_cam_loc_low)

            np.savetxt('airfoil_interpolation/({0})({1:.2f}).txt'.format(
                Re, max_cam), polar)

        polar_low = np.loadtxt(
            'airfoil_interpolation/({0})({1:.2f}).txt'.format(Re, max_cam_low))
        polar_high = np.loadtxt(
            'airfoil_interpolation/({0})({1:.2f}).txt'.format(
                Re, max_cam_high))
        slope_num = polar_high-polar_low
        if not slope_num.any():
            polar = polar_low
        else:
            polar = polar_low + (max_cam - max_cam_low) *\
                slope_num/(max_cam_high-max_cam_low)

        np.savetxt('airfoil_interpolation/({0}).txt'.format(Re), polar)

    polar_low = np.loadtxt('airfoil_interpolation/({0}).txt'.format(Re_low))
    polar_high = np.loadtxt('airfoil_interpolation/({0}).txt'.format(Re_high))
    slope_num = polar_high-polar_low
    if not slope_num.any():
        polar = polar_low
    else:
        polar = polar_low + (Re - Re_low) * slope_num/(Re_high - Re_low)

    for file in os.listdir('airfoil_interpolation'):
        os.remove('airfoil_interpolation/' + file)

    alpha_array = np.around(polar[:, 0], 2)
    cl_array = np.around(polar[:, 1], 4)
    cd_array = np.around(polar[:, 2], 4)

    return alpha_array, cl_array, cd_array


def get_3D_aerodynamics(AR, Lambda_midc, cl_r, alpha_array, cl_array,
                        cd_array):
    """Convert 2D lift curve into 3D lift curve."""
    cl_alpha_fit = interpolate.interp1d(alpha_array, cl_array,
                                        fill_value='extrapolate')
    cd_alpha_fit = interpolate.interp1d(alpha_array, cd_array,
                                        fill_value='extrapolate')
    alpha_cl_fit = interpolate.interp1d(cl_array, alpha_array,
                                        fill_value='extrapolate')

    alpha_zl = alpha_cl_fit(0)

    alpha_array = np.linspace(alpha_zl, 10, 21)
    cl_array = cl_alpha_fit(alpha_array)
    cl_alpha = np.mean((cl_array[1:] -
                        cl_array[:-1])/(alpha_array[1:] -
                                        alpha_array[:-1]))
    CL_alpha = np.deg2rad(
        2*np.pi*AR/(2 + np.sqrt((AR/(np.rad2deg(cl_alpha) /
                                     (2*np.pi)))**2 *
                                (1 + np.tan(Lambda_midc)**2) + 4)))
    CL_array = CL_alpha/cl_alpha*(
        cl_array - cl_alpha*alpha_array) + CL_alpha*alpha_array

    alpha_CL_fit = interpolate.interp1d(CL_array, alpha_array,
                                        fill_value='extrapolate')

    alpha = float(np.around(alpha_CL_fit(cl_r), 2))

    if alpha < 15:
        CDp = float(np.around(cd_alpha_fit(alpha), 5))
    else:
        CDp = 1
    return alpha, CDp