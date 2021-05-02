"""Provide tools for creating parametirc aircraft geometry."""

import numpy as np
import matplotlib.pyplot as plt
import openvsp as vsp


def naca_4_series(max_camber, max_camber_loc, max_tc, n_points,
                  plot_switch=False):
    """Plot NACA 4-Series airfoil with the given characteristics."""
    airfoil_name = 'NACA({0:.2f})({1:.2f})({2:.2f})'.format(
        max_camber, max_camber_loc, max_tc)
    x_coords = np.linspace(0, 1, n_points)

    def get_thickness_dist(x_coords):

        t_max = max_tc/100
        t_dist = t_max*(1.4845*np.sqrt(x_coords) - 0.63*x_coords -
                        1.758*x_coords**2 + 1.4215*x_coords**3 -
                        0.5075*x_coords**4)

        return t_dist

    def get_camber_curve(x_coords):

        x_mc = max_camber_loc/10
        z_mc = max_camber/100

        z_mcl = np.empty(len(x_coords))
        dz_mcldx = np.empty(len(x_coords))

        for i, x_coord in enumerate(x_coords):
            if x_coord < x_mc:
                z_mcl[i] = z_mc/x_mc**2*(2*x_mc*x_coord-x_coord**2)
                dz_mcldx[i] = (z_mc/x_mc**2)*(2*x_mc - 2*x_coord)
            else:
                z_mcl[i] = (z_mc/(1-x_mc)**2)*(
                    1-2*x_mc + 2*x_mc*x_coord-x_coord**2)
                dz_mcldx[i] = (z_mc/(1-x_mc)**2)*(2*x_mc - 2*x_coord)

            theta = np.arctan(dz_mcldx)

        return z_mcl, theta

    t_dist = get_thickness_dist(x_coords)
    z_mcl, theta = get_camber_curve(x_coords)

    x_u = x_coords - t_dist*np.sin(theta)
    z_u = z_mcl + t_dist*np.cos(theta)

    x_l = x_coords + t_dist*np.sin(theta)
    z_l = z_mcl - t_dist*np.cos(theta)

    scale_factor_u = 1/x_u[-1]
    x_u *= scale_factor_u
    z_u *= scale_factor_u

    scale_factor_l = 1/x_l[-1]
    x_l *= scale_factor_l
    z_l *= scale_factor_l

    if plot_switch:
        fig = plt.figure(dpi=1200)
        ax = fig.add_subplot(111)
        ax.plot(x_u, z_u, 'k')
        ax.plot(x_l, z_l, 'k')
        ax.axis('equal')
        ax.set_title(airfoil_name)

    coords_array = np.vstack((np.concatenate((x_u[::-1], x_l)),
                              np.concatenate((z_u[::-1], z_l)))).T

    np.savetxt('xfoil/' + airfoil_name + '.dat', coords_array, fmt='%.4f')

    return coords_array


def create_VSP_wing(wing_span, planform, airfoil, alpha_i):
    """Create wing in OpenVSP dexcribed by the given characteristics."""
    max_camber = airfoil[0]
    max_camber_loc = airfoil[1]
    max_tc = airfoil[2]

    vsp.VSPCheckSetup()
   
    vsp.ClearVSPModel()

    wing_id = vsp.AddGeom('WING')
    vsp.SetGeomName(wing_id, 'Wing')

    wing_sec_span = wing_span/(2*(len(planform) - 1))

    for i in range(len(planform)-1):
        if i != 0:
            vsp.InsertXSec(wing_id, i, vsp.XS_FOUR_SERIES)
        vsp.SetParmValUpdate(wing_id, 'Span', 'XSec_{0}'.format(i+1),
                             wing_sec_span)
        vsp.SetParmValUpdate(wing_id, 'Root_Chord', 'XSec_{0}'.format(i+1),
                             planform[i])
        vsp.SetParmValUpdate(wing_id, 'Tip_Chord', 'XSec_{0}'.format(i+1),
                             planform[i+1])
        vsp.SetParmValUpdate(wing_id, 'Sweep', 'XSec_{0}'.format(i+1), 0)
        vsp.SetParmValUpdate(wing_id, 'Sweep_Location', 'XSec_{0}'.format(
            i+1), 0.25)

    for i in range(len(planform)):
        vsp.SetParmValUpdate(wing_id, 'Camber', 'XSecCurve_{0}'.format(i),
                             max_camber/100)
        vsp.SetParmValUpdate(wing_id, 'CamberLoc', 'XSecCurve_{0}'.format(i),
                             max_camber_loc/10)
        vsp.SetParmValUpdate(wing_id, 'ThickChord', 'XSecCurve_{0}'.format(i),
                             max_tc/100)
    vsp.SetParmValUpdate(wing_id, 'Y_Rel_Rotation', 'XForm', alpha_i)

    vsp.WriteVSPFile(
        'C:/Users/jaros/Documents/GitHub/DISECON_PIA/2 - Conceptual Design/4 - Wing Design/wing_model.vsp3')

    print('Done!')
