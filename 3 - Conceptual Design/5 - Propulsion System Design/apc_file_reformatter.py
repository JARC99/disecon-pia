"""Re-formats APC Propellers' horribly formatted propeller performance data files."""
import os
import numpy as np

RAW_DATA_DIR = "C:/Users/jaros/Google Drive/Universidad/Trabajos Escolares/"\
    "PIAE I/PIAE Github Repository/3 - Conceptual Design/"\
        "5 - Powertrain Design/raw_propeller_data"
DATA_DIR = "C:/Users/jaros/Google Drive/Universidad/Trabajos Escolares/"\
    "PIAE I/PIAE Github Repository/3 - Conceptual Design/"\
        "5 - Powertrain Design/propeller_data"
        
        
#%% File re-formater

apc_file_list = os.listdir(RAW_DATA_DIR)

for apc_file in apc_file_list:
    prop_folder = os.path.join(DATA_DIR, apc_file[5:-4])
    if not os.path.exists(prop_folder):
        os.makedirs(prop_folder)

    with open(os.path.join(RAW_DATA_DIR, apc_file)) as raw_data_file:
        line_list = raw_data_file.readlines()

    index_list = []
    for i, line in enumerate(line_list):
        if line[:19] == "         PROP RPM =":
            index_list.append(i)
    index_list.append(len(line_list))
    index_array = np.array(index_list)
    data_len = index_array[1:] - index_array[:-1]

    for i, index in enumerate(index_list[:-1]):
        data_path = os.path.join(prop_folder, line_list[index][19:].strip() + ".dat")

        with open(data_path, 'w') as data_file:
            for line in line_list[index + 4: index + data_len[i]]:
                data_file.write(line)

#%% Unit converssion 

prop_list = os.listdir(DATA_DIR)

for prop in prop_list:
    omega_list = os.listdir(os.path.join(DATA_DIR, prop))
    
    for omega in omega_list:
        data_path = os.path.join(DATA_DIR, prop, omega)
        try:
            data_array = np.loadtxt(data_path)
        except ValueError:
            with open(data_path) as data_file:
                raw_line_list = data_file.readlines()
                
            line_list = []
            for line in raw_line_list:
                if not "-NaN" in line:
                    line_list.append(line)
            
            with open(data_path, 'w') as data_file:
                for line in line_list:
                    data_file.write(line)
            
            data_array = np.loadtxt(data_path)

        data_array[:, 0] = data_array[:, 0] * 0.44704
        data_array[:, 5] = data_array[:, 5] * 745.7
        data_array[:, 6] = data_array[:, 6] * 0.112985
        data_array[:, 7] = data_array[:, 7] * 4.44822
    
        np.savetxt(os.path.join(DATA_DIR, prop, omega), data_array, fmt="%.4f")