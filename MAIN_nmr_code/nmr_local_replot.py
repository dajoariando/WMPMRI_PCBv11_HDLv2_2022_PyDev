from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.nmr_functions import compute_multiexp

sav_fig = True
show_fig = True
expt_num = 0 # experiment number is always 0 for a single experiment

# import default measurement configuration
from sys_configs.phenc_conf_random import phenc_conf_random
phenc_conf = phenc_conf_random()

# set local folder
client_data_folder = "D:/NMR_DATA/cpmg_240806_212212"
nmrObj = nmr_system_2022( client_data_folder )


compute_multiexp( nmrObj, phenc_conf, expt_num, sav_fig, show_fig )