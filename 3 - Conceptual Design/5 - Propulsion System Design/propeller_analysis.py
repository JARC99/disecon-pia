"""Aide in propeller selection."""
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib.font_manager as font_manager

from ambiance import Atmosphere
from scipy import interpolate

sns.set_theme(style='whitegrid', font='Palatino Linotype', context='paper')
FONT_FILE = 'C:/Windows/Fonts/pala.ttf'
font_manager.fontManager.addfont(FONT_FILE)

DATA_DIR = "C:/Users/jaros/Google Drive/Universidad/Trabajos Escolares/"\
    "PIAE I/PIAE Github Repository/3 - Conceptual Design/"\
        "5 - Propulsion System Design/propeller_data"

vel = 0 # m/s

diam_min = 13 # in
diam_max = 13 # in

prop_list =  os.listdir(DATA_DIR)


#%% Static Thrust Analysis



for prop in prop_list:
    diam_raw = float(prop[:prop.index('x')])
    
    if diam_raw <= 28:
        diam = diam_raw
    elif diam_raw > 28 and diam_raw <= 280:
        diam = diam_raw/10
    elif diam_raw > 280 and diam_raw <= 2800:
        diam = diam_raw/100
    else:
        diam = diam_raw/1000
        
    if diam >= diam_min and diam <= diam_max:
        prop_dir = os.path.join(DATA_DIR, prop)
        
        fig = plt.figure(dpi=1200)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("axes", 1.15))
        fig.suptitle(prop)
        ax1.set_xlabel('Angular Velocity, rpm')
        ax1.set_ylabel('Thrust, N')
        ax2.set_ylabel('Power, W')
                
        data_len = len(os.listdir(prop_dir))
        
        ang_vel_array = np.empty(data_len)
        prop_eff_array = np.empty(data_len)
        power_array = np.empty(data_len)
        thrust_array = np.empty(data_len)

        for i, data_file in enumerate(sorted(os.listdir(prop_dir), key=len)):
            ang_vel_array[i] = float(data_file[:-4])
            
            data_array = np.loadtxt(os.path.join(prop_dir, data_file))
            
            vel_data = data_array[:, 0]
            prop_eff_data = data_array[:, 2]
            power_data = data_array[:, 5]
            thrust_data = data_array[:, 7]
            
            prop_eff_vel_fit = interpolate.interp1d(vel_data, prop_eff_data,
                                        fill_value='extrapolate')
            power_vel_fit = interpolate.interp1d(vel_data, power_data,
                                        fill_value='extrapolate')
            thrust_vel_fit = interpolate.interp1d(vel_data, thrust_data,
                                        fill_value='extrapolate')
            
            prop_eff_array[i] = prop_eff_vel_fit(vel)
            power_array[i] = power_vel_fit(vel)
            thrust_array[i] = thrust_vel_fit(vel)
        
        ax1.plot(ang_vel_array, thrust_array)
        ax2.plot(ang_vel_array, power_array, 'tab:orange')
        
        if vel == 0:
            ax3.plot(ang_vel_array, thrust_array/power_array, 'tab:green')
            ax3.set_ylabel('Thrust-to-Power Ratio, N/W')
            ax3.set_ylim(bottom=0)
        else:
            ax3.plot(ang_vel_array, prop_eff_array, 'tab:green')
            ax3.set_ylabel('Propulsive Efficiency')
            ax3.set_ylim(0, 1)

        ax1.set_xlim(left=0)
        ax1.set_ylim(0, 5)
        ax1.yaxis.label.set_color('tab:blue')
        ax1.tick_params(axis='y', colors='tab:blue')

        ax2.set_xlim(left=0)
        ax2.set_ylim(0, 1000)
        ax2.yaxis.label.set_color('tab:orange')
        ax2.tick_params(axis='y', colors='tab:orange')
        
        ax3.set_xlim(left=0)
        ax3.yaxis.label.set_color('tab:green')
        ax3.tick_params(axis='y', colors='tab:green')
            
            
            
            
            
    
            