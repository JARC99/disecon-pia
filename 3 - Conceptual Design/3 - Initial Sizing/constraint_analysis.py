import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

import constraint_analysis_tools as cat

import matplotlib.font_manager as font_manager
font_file = 'C:/Windows/Fonts/pala.ttf'
font_manager.fontManager.addfont(font_file)

sns.set_theme(style='darkgrid', font='Palatino Linotype', context='paper')

graphics_folder_path = 'C:/Users/jaros/Google Drive/Universidad/'\
    'Trabajos Escolares/PIAE I/''Graphics/3 - Conceptual Design/3 -'\
        ' Initial Sizing'

#%% Aircraft Requirements

design_brief = {'Cruise altitude':640, # m AMSL
                'Ground run':25, # m
                'Hover service ceiling':4000, # m AMSL
                'Maximum range':60, # km
                'Rate of climb':2, # m/s
                'Rate of climb at service ceiling':0.2, # m/s
                'Stall speed': 12, # m/s
                'Service ceiling':4000, # m AMSL
                'T-O altitude':540, # m AMSL
                'Vertical rate of climb':5, # m/s
                'Vertical rate of climb at hover service ceiling':0.5} # m/s

concept = {'Battery specific energy':140, # Wh/
           'Battery specific power':850, # W/kg
           'Figure of merit':0.5,
           'Induced power correction factor':1.1,
           'Transition tilt angle':45, # °
           'Drag coefficient at T-O':0.035, 
           'Ground friction coefficient':0.04,
           'Lift coefficient at T-O':0.7,
           'Maximum lift coefficient':1.3, 
           'Minimum drag coefficient':0.035,
           'Peukert exponent':1.3,
           'Powertrain efficiency':0.85, 
           'Propulsive efficiency':0.7,
           'Wing aspect ratio':6}


#%% Constrain Analysis

WL = np.linspace(0.001, 15, 1000) 
DL = np.linspace(0.001, 150, 1000)
DL_mg, WL_mg = np.meshgrid(DL, WL)

PW_rat_hvr = cat.get_Hvr_PW_rat(design_brief, concept, DL)
PW_rat_vRoC = cat.get_vRoC_PW_rat(design_brief, concept, DL)
PW_rat_vSC = cat.get_vSC_PW_rat(design_brief, concept, DL)

PW_rat_TR = cat.get_Tr_PW_rat(design_brief, concept, DL_mg, WL_mg)

PW_rat_TO = cat.get_TO_PW_rat(design_brief, concept, WL)
PW_rat_RoC, V_Y = cat.get_RoC_PW_rat(design_brief, concept, WL)
PW_rat_cr, V_cr = cat.get_V_cr_PW_rat(design_brief, concept, WL)
PW_rat_SC = cat.get_SC_PW_rat(design_brief, concept, WL)
WL_S, V_S = cat.get_S_WL(design_brief, concept)

rc_PW_rat_list = [PW_rat_hvr, PW_rat_vRoC, PW_rat_vSC]
rc_label_list = ['Hover', 'Vertical RoC', 'Vertical Service Ceiling']

fw_PW_rat_list = [PW_rat_TO, PW_rat_RoC, PW_rat_cr, PW_rat_SC]
fw_label_list = ['T-O', 'RoC', 'Cruise', 'Service Ceiling']

#%% Constrain Diagrams

fig = plt.figure(dpi=1200)
ax = fig.add_subplot(111)
for PW_rat, rt_label in zip(rc_PW_rat_list, rc_label_list):
    ax.fill_between(DL, 0, PW_rat, edgecolor='none', alpha=0.75, label=rt_label)
ax.set_xlabel('Disk Loading, $\mathdefault{kg/m^{2}}$')
ax.set_ylabel('Power-to-Weight Ratio, W/kg')
ax.legend()
ax.set_xlim(DL[0], DL[-1])
ax.set_ylim(0, 700)
fig.savefig(graphics_folder_path + '/PWrat_vs_DL.pdf', format='pdf',
            bbox_inches='tight')

fig = plt.figure(dpi=1200)
ax = fig.add_subplot(111)
for PW_rat, fw_label in zip(fw_PW_rat_list, fw_label_list):
    ax.fill_between(WL, 0, PW_rat, edgecolor='none', alpha=0.75, label=fw_label)
ax.fill_betweenx([0, 500], WL_S, WL[-1], edgecolor='none', alpha=0.75, label='Stall')
ax.set_xlabel('Wing Loading, $\mathdefault{kg/m^{2}}$')
ax.set_ylabel('Power-to-Weight Ratio, W/kg')
ax.set_xlim(WL[0], WL[-1])
ax.set_ylim(0, 100)

ax2 = ax.twinx()
ax2.plot(WL, V_Y, linestyle='--', color='y', label='$\mathdefault{V_{Y}}$')
ax2.plot(WL, V_cr, linestyle='--', color='g', label='$\mathdefault{V_{cr}}$')
ax2.hlines(V_S, WL[0], WL[-1], linestyle='--', color='m', label='$\mathdefault{V_{S}}$')
ax2.set_ylabel('$\mathdefault{True Airspeed, m/s}$')
ax2.set_ylim(0, 20)
ax2.grid(False)

h, l = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax2.legend(h+h2, l+l2, loc=2)
fig.savefig(graphics_folder_path + '/PWrat_vs_WL.pdf', format='pdf', bbox_inches='tight')

fig = plt.figure(dpi=1200)
ax = fig.add_subplot(111)
levels = np.linspace(0, 1000, 50)
ticks = np.linspace(0, 1000, 11)
fig.colorbar(ax.contourf(DL, WL, PW_rat_TR, cmap='jet', levels=levels,
                         extend='max', alpha=0.75, edgecolor='none'),
             label='Power-to-Weight Ratio, W/kg', ticks=ticks)
ax.set_xlabel('Disk Loading, $\mathdefault{kg/m^{2}}$')
ax.set_ylabel('Wing Loading, $\mathdefault{kg/m^{2}}$')
ax.set_ylim(DL[0], DL[-1])
ax.set_ylim(WL[0], WL[-1])
fig.savefig(graphics_folder_path + '/PWrat_vs_WL_vs_DL.pdf', format='pdf', bbox_inches='tight')