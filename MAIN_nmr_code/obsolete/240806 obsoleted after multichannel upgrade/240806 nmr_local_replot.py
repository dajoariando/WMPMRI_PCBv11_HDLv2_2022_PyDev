from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.nmr_functions import compute_multiexp

sav_fig = True
show_fig = True
expt_num = 0 # experiment number is always 0 for a single experiment

# import default measurement configuration
from sys_configs.phenc_conf_halbach_v03_221018 import phenc_conf_halbach_v03_221018
phenc_conf = phenc_conf_halbach_v03_221018()

# set local folder
client_data_folder = "D:/Dropbox (UFL)/school/dissertation/Experimental/NMR Data/A04 HALBACH V03 2-TURNS GRADIENT 4-TURNS TX/01 BASIC/DISSERTATION_T2_221028_170354__AFTER_ADDED_GRAD_FERRITE"
nmrObj = nmr_system_2022( client_data_folder )


compute_multiexp( nmrObj, phenc_conf, expt_num, sav_fig, show_fig )