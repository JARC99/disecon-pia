import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns

import matplotlib.font_manager as font_manager
font_file = 'C:/Windows/Fonts/pala.ttf'
font_manager.fontManager.addfont(font_file)

sns.set_theme(style='darkgrid', font='Palatino Linotype', context='paper')

#%% 

data = pd.read_excel('bldc_motors_database.xlsx',  engine='openpyxl')

name_array = data['Name'].to_numpy()
kV_array = data['kv'].to_numpy()
kT_array = 1/(kV_array*np.pi/30)
I0_array = data['I_0'].to_numpy()
Rm_array = data['R_m'].to_numpy()
Pmax_array = data['P_max'].to_numpy()

Qm_array = np.linspace(0, 1, 100)
omega_array = np.linspace(0, 20000, 100)

Qm_mg, omega_mg = np.meshgrid(Qm_array, omega_array)

for i in range(np.size(kV_array)):
    
    I_array = Qm_array/(kT_array[i]) + I0_array[i]
    V_array = omega_array/kV_array[i] + Rm_array[i]*I0_array[i]
    
    Pshaft_array = Qm_array*(omega_array*np.pi/30)
    Pin_array = V_array*I_array
    
    eta_m_array = Pshaft_array/Pin_array

    
    I_mg, V_mg = np.meshgrid(I_array, V_array)
    
    Pshaft_mg = Qm_mg*(omega_mg*np.pi/30)
    Pin_mg = V_mg*I_mg
    
    eta_m_mg = Pshaft_mg/Pin_mg
    
    if not np.isnan(I0_array[i]):
        fig = plt.figure(dpi=1200)
        ax = fig.add_subplot(111)
        levels = np.linspace(0, 1, 50)
        ticks = np.linspace(0, 1, 11)
        cp = ax.contourf(omega_mg, Qm_mg, eta_m_mg, cmap='jet', levels=levels, extend='max', alpha=0.75, edgecolor='none')
        fig.colorbar(cp, label='$\mathdefault{\eta_{m}}$', ticks=ticks)
        ax.set_ylabel('$\mathdefault{Q_{m}, Nm}$')
        ax.set_xlabel('$\mathdefault{\omega, rpm}$')
        ax.set_ylim(Qm_array[0], Qm_array[-1])
        ax.set_xlim(omega_array[0], omega_array[-1])
        ax.set_title(name_array[i])
        
        # fig = plt.figure(dpi=1200)
        # ax = fig.add_subplot(111)
        # ax.plot(Pin_array, eta_m_array)
        # ax.set_ylabel('$\mathdefault{\eta_{m}}$')
        # ax.set_xlabel('$\mathdefault{P_{in}, W}$')
        # ax.set_ylim(bottom=eta_m_array[0])
        # ax.set_xlim(left=Pin_array[0])
        # ax.set_title(name_array[i])


