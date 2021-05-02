"""Optimize planform shape for a given area and flight condition."""

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

sns.set_theme(style='darkgrid', font='Palatino Linotype', context='paper')
FONT_FILE = 'C:/Windows/Fonts/pala.ttf'
font_manager.fontManager.addfont(FONT_FILE)


# %% Problem constants

h = 640 # m AMSL
V = 22  # m/s
g = Atmosphere(h).grav_accel  # m/s^2
rho = Atmosphere(h).density  # kg/m^3
nu = Atmosphere(h).kinematic_viscosity  # m^2/s

WL = 23.239  # kg/m^2
W0 = 10  # kg
AR = 11

n_sections = 6

c_min = 0.10  # m
c_max = 0.50 # m

S = W0/WL  # m^2
b = np.sqrt(AR*S)  # m

dy = b/n_sections  # m
y_stations = np.linspace(0, b/2, n_sections//2 + 1)  # m

y_stations_fine = np.linspace(0, b/2, n_sections*100)  # m
c_r_ideal = 4*S/(b*np.pi)  # m
ideal_planform = c_r_ideal*np.sqrt(1 - (2*y_stations_fine/b)**2)

# %% GA - Planform

population_size = 500
p_crossover = 0.9
p_mutation = 0.1
max_generations = 100


def optimize_planform(population_size, max_generations, p_crossover,
                      p_mutation):
    """Wing planform shape optimization algorithm."""
    hall_of_fame_size = 10
    crowding_factor = 15
    penalty_value = 1

    toolbox = base.Toolbox()

    # Create fitness function class
    creator.create('FitnessMin', base.Fitness, weights=(-1.0,))

    # Create individual class
    creator.create('Individual', list, fitness=creator.FitnessMin)

    def get_chords(c_min, c_max):
        return round(random.uniform(c_min, c_max), 3)

    # Random chord generator
    toolbox.register('generate_chords', get_chords, c_min, c_max)

    # Create individual generator
    toolbox.register('individual_creator', tools.initRepeat,
                     creator.Individual, toolbox.generate_chords,
                     n=len(y_stations))

    # Create population generator
    toolbox.register('population_creator', tools.initRepeat, list,
                     toolbox.individual_creator)

    # Fitness evaluation
    def evaluate_fitness(individual):
        planform = np.array([])
        for i in range(n_sections//2):
            section = np.linspace(individual[i], individual[i+1], 200)
            planform = np.concatenate((planform, section))

        planform_mse = np.mean((planform - ideal_planform)**2)

        return planform_mse,

    # Feasibility evaluation
    def evaluate_feasibility(individual):
        planform = np.array(individual)
        planform_S = sum((planform[:-1] + planform[1:])/2*dy)

        return abs(2*planform_S - S)/S <= 0.01

    def distance(individual):
        planform = np.array(individual)
        planform_S = sum((planform[:-1] + planform[1:])/2*dy)

        return (2*planform_S - S)**2

    # Define geneitc operators
    toolbox.register('evaluate', evaluate_fitness)
    toolbox.decorate('evaluate', tools.DeltaPenality(evaluate_feasibility,
                                                     penalty_value, distance))
    toolbox.register('select', tools.selTournament, tournsize=2)
    toolbox.register('mate', tools.cxSimulatedBinaryBounded, low=c_min,
                     up=c_max, eta=crowding_factor)
    toolbox.register('mutate', tools.mutPolynomialBounded, low=c_min,
                     up=c_max, eta=crowding_factor, indpb=1/len(y_stations))

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

    best_planform = list(map(lambda c: round(c, 3), hof.items[0]))
    best_planform = np.array(best_planform)
    best_planform_S = sum((best_planform[:-1] + best_planform[1:])/2*dy)

    print('\n--> Best Fitness = {0}'.format(hof.items[0].fitness.values[0]))
    print('\n--> Best Planform = {0} m'.format(best_planform))
    print('--> Planform Area = {0:.4f} m^2'.format(2*best_planform_S))

    fig = plt.figure(dpi=1200)
    ax = fig.add_subplot(111)
    ax.plot(minFitnessValues, color='red', label='Min FV')
    ax.set_xlabel('Generation')
    ax.set_ylabel(r'Mean Square Error')
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    ax2 = ax.twinx()
    ax2.plot(meanFitnessValues, color='green', label='Mean FV')
    ax2.set_ylabel('Generation Average Mean Square Error')
    ax2.set_ylim(bottom=0)

    fig = plt.figure(dpi=1200)
    ax = fig.add_subplot(111)
    ax.plot(y_stations_fine, ideal_planform)
    ax.plot(y_stations, np.array(best_planform), color='red')
    ax.set_xlabel('Span Station, m')
    ax.set_ylabel('Chord, m')
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    return best_planform


def main():
    return optimize_planform(200, 300, 0.9, 0.1)


if __name__ == "__main__":
    opt_planform = main()
