import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

import constraint_analysis_tools as cat

import matplotlib.font_manager as font_manager
font_file = 'C:/Windows/Fonts/pala.ttf'
font_manager.fontManager.addfont(font_file)

sns.set_theme(style='whitegrid', font='Palatino Linotype', context='paper')

graphics_folder_path = 'C:/Users/jaros/Documents/GitHub/DISECON_PIA/2 - Conceptual Design/3 - Initial Sizing/images'

#%% Aircraft Requirements

design_brief = {'Cruise altitude':640, # m AMSL
                'Ground run':30, # m
                'Rate of climb':7.5, # m/s
                'Rate of climb at service ceiling':0, # m/s
                'Stall speed': 14, # m/s
                'Service ceiling':5943, # m AMSL
                'T-O altitude':540} # m AMSL

concept = {'Battery specific energy':140, # Wh/kg
           'Battery specific power':850, # W/kg
           'Drag coefficient at T-O':0.03, 
           'Ground friction coefficient':0.04,
           'Lift coefficient at T-O':0.7,
           'Maximum lift coefficient':2, 
           'Minimum drag coefficient':0.03,
           'Peukert exponent':1.3,
           'Powertrain efficiency':0.85, 
           'Propulsive efficiency':0.7,
           'Wing aspect ratio':11}


#%% Constrain Analysis

WL = np.linspace(0.001, 30, 1000) 

PW_rat_TO = cat.get_TO_PW_rat(design_brief, concept, WL)
PW_rat_RoC, V_Y = cat.get_RoC_PW_rat(design_brief, concept, WL)
PW_rat_cr, V_cr = cat.get_V_cr_PW_rat(design_brief, concept, WL)
PW_rat_SC = cat.get_SC_PW_rat(design_brief, concept, WL)
WL_S, V_S = cat.get_S_WL(design_brief, concept)


fw_PW_rat_list = [PW_rat_TO, PW_rat_RoC, PW_rat_cr, PW_rat_SC]
fw_label_list = ['T-O', 'RoC', 'Cruise', 'Absolute Ceiling']

#%% Constrain Diagrams

fig = plt.figure(dpi=1200)
ax = fig.add_subplot(111)
for PW_rat, fw_label in zip(fw_PW_rat_list, fw_label_list):
    ax.fill_between(WL, 0, PW_rat, edgecolor='none', alpha=0.75, label=fw_label)
ax.fill_betweenx([0, 500], WL_S, WL[-1], edgecolor='none', alpha=0.75, label='Stall')
ax.set_xlabel('Wing Loading, $\mathdefault{kg/m^{2}}$')
ax.set_ylabel('Power-to-Weight Ratio, W/kg')
ax.set_xlim(WL[0], WL[-1])
ax.set_ylim(0, 500)

ax2 = ax.twinx()
ax2.plot(WL, V_Y, linestyle='--', color='y', label='$\mathdefault{V_{Y}, V_{L}}$')
ax2.plot(WL, V_cr, linestyle='--', color='g', label='$\mathdefault{V_{C}}$')
ax2.hlines(V_S, WL[0], WL[-1], linestyle='--', color='m', label='$\mathdefault{V_{S0}}$')
ax2.set_ylabel('$\mathdefault{True~Airspeed, m/s}$')
ax2.set_ylim(0, 30)
ax2.grid(False)

h, l = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax2.legend(h+h2, l+l2, loc=2)
fig.savefig(graphics_folder_path + '/PWrat_vs_WL.pdf', format='pdf', bbox_inches='tight')