"""Optimize wing section for a given planform and flight condition."""

import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib.font_manager as font_manager

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from ambiance import Atmosphere

from aerodynamics_toolbox import interpolate_airfoil_polar
from aerodynamics_toolbox import get_3D_aerodynamics
from aerodynamics_toolbox import runXfoil

from aircraft_plotter import naca_4_series
from aircraft_plotter import create_VSP_wing

sns.set_theme(style='darkgrid', font='Palatino Linotype', context='paper')
FONT_FILE = 'C:/Windows/Fonts/pala.ttf'
font_manager.fontManager.addfont(FONT_FILE)


# %% Problem constants

H = 600  # m AMSL
V = 15  # m/s
g = Atmosphere(H).grav_accel[0]  # m/s^2
rho = Atmosphere(H).density[0]  # kg/m^3
nu = Atmosphere(H).kinematic_viscosity[0]  # m^2/s

WL = 11  # kg/m^2
W0 = 5  # kg
AR = 6

# planform = [0.344, 0.329, 0.232, 0.2] # 6 sections
# planform = [0.34, 0.338, 0.303, 0.202, 0.2] # 8 sections
planform = [0.348, 0.338, 0.31, 0.272, 0.2, 0.2]  # 10 sections
n_sections = 6

max_camber_min = 0  # %
max_camber_max = 6  # %
max_camber_loc_min = 2  # 10%
max_camber_loc_max = 6  # 10%
max_tc_min = 13  # %
max_tc_max = 25  # %

S_ideal = W0/WL  # m^2
b = round(np.sqrt(AR*S_ideal), 2)  # m
dy = b/n_sections  # m
y_stations = np.linspace(0, b/2, n_sections//2 + 1)  # m
c_array = np.array(planform)
S_array = (c_array[:-1] + c_array[1:])/2*dy

S_real = 2*np.sum(S_array)
MGC = round(np.sum((c_array[:-1] + c_array[1:])/2*S_array)/(S_real/2), 3)

Lambda_midc = np.sum(np.arctan(
    (c_array[1:] - c_array[0:-1])/(4*dy))*S_array)/S_real

L = W0*g
CL = round(L/(0.5*rho*V**2*S_real), 4)

Lr = L/(np.pi/4*b)
cl_r = round(2*Lr/(rho*V**2*c_array[0]), 4)
Re = (V*MGC)/nu

# %% GA - Airfoil


def optimize_airfoil(population_size, max_generations, p_crossover,
                     p_mutation):
    """Airfoil optimization algorithm."""
    hall_of_fame_size = 1

    toolbox = base.Toolbox()

    # Create fitness function class
    creator.create('FitnessMin', base.Fitness, weights=(-1.0,))

    # Create individual class
    creator.create('Individual', list, fitness=creator.FitnessMin)

    # Random wing sections generator
    def get_airfoil(y_stations):

        max_camber = round(random.randint(max_camber_min, max_camber_max), 0)
        max_camber_loc = round(random.randint(max_camber_loc_min,
                                              max_camber_loc_max), 0)
        max_tc = round(random.randint(max_tc_min, max_tc_max), 0)

        return [max_camber, max_camber_loc, max_tc]

    toolbox.register('generate_airfoil', get_airfoil, y_stations)

    # Create individual generator
    toolbox.register('individual_creator', tools.initIterate,
                     creator.Individual, toolbox.generate_airfoil)

    # Create population generator
    toolbox.register('population_creator', tools.initRepeat, list,
                     toolbox.individual_creator)

    # Fitness evaluation
    def get_wing_CDp(individual):

        alpha_array, cl_array, cd_array = interpolate_airfoil_polar(individual,
                                                                    Re)

        CDp = get_3D_aerodynamics(AR, Lambda_midc, cl_r, alpha_array, cl_array,
                                  cd_array)[-1]

        return CDp,

    # Define geneitc operators
    toolbox.register('evaluate', get_wing_CDp)
    toolbox.register('select', tools.selTournament, tournsize=6)
    # toolbox.register('mate', tools.cxSimulatedBinaryBounded,
    #                  low=(max_camber_min, max_camber_loc_min,
    #                                       max_tc_min),
    toolbox.register('mate', tools.cxUniform, indpb=1/3)
    toolbox.register('mutate', tools.mutUniformInt,
                     low=(max_camber_min, max_camber_loc_min, max_tc_min),
                     up=(max_camber_max, max_camber_loc_max, max_tc_max),
                     indpb=1/3)

    population = toolbox.population_creator(n=population_size)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register('min', np.min)
    stats.register('avg', np.mean)

    hof = tools.HallOfFame(hall_of_fame_size)

    population, logbook = algorithms.eaSimple(population, toolbox,
                                              cxpb=p_crossover,
                                              mutpb=p_mutation,
                                              ngen=max_generations,
                                              stats=stats, halloffame=hof,
                                              verbose=True)

    minFitnessValues, meanFitnessValues = logbook.select("min", "avg")

    fig = plt.figure(dpi=1200)
    ax = fig.add_subplot(111)
    ax.plot(minFitnessValues, color='red', label='Min FV')
    ax2 = ax.twinx()
    ax2.plot(meanFitnessValues, color='green', label='Mean FV')
    ax.set_xlabel('Generation')
    ax.set_ylabel(r'$\mathdefault{Minimum C_{D_{p}}}$')
    ax2.set_ylabel(r'Average $\mathdefault{C_{D_{p}}}$')
    ax.set_xlim(left=0)

#   hof_file = open('airfoil_hof.txt', 'w')
    for i in range(hall_of_fame_size):
        max_cam = hof.items[i][0]
        max_cam_loc = hof.items[i][1]
        max_tc = hof.items[i][2]

        airfoil_name = ('NACA({0:.2f})({1:.2f})({2:.2f})'.format(
            max_cam, max_cam_loc, max_tc))

        naca_4_series(max_cam, max_cam_loc, max_tc, 100, plot_switch=True)
        alpha_array, cl_array, cd_array = runXfoil(airfoil_name, Re, -10, 10,
                                                   0.25)

#       CDp = hof.items[i].fitness.values[0]
        alpha_i = get_3D_aerodynamics(AR, Lambda_midc, cl_r, alpha_array,
                                      cl_array, cd_array)[0]

        # hof_file.write(airfoil_name + '\t\t')
        # hof_file.write('{0}\t\t'.format(CDp))
        # hof_file.write('{0}\n'.format(alpha_i))

        if i == 0:
            best_airfoil = hof.items[i]
            best_alpha_i = alpha_i
    # hof_file.close()

    return best_airfoil, best_alpha_i


def main():

    airfoil, alpha_i = optimize_airfoil(20, 20, 0.5, 0.95)
    create_VSP_wing(b, planform, airfoil, alpha_i)


if __name__ == "__main__":
    main()
