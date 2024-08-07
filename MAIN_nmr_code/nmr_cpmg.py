'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

import os
import time
from datetime import datetime
import pydevd
from scipy import signal
import matplotlib.pyplot as plt

from nmr_std_function.data_parser import parse_csv_float2col
from nmr_std_function.data_parser import parse_simple_info
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir
from nmr_std_function.nmr_functions import plot_echosum
from nmr_std_function.time_func import time_meas
from nmr_std_function.expts_functions import cpmg


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = '\\cpmg_'+datatime

# variables
expt_num = 0 # set to 0 for a single experiment
sav_fig = 1 # save figures
show_fig = 1  # show figures

# enable time measurement
tmeas = time_meas(True)

# instantiate nmr object
client_data_folder = data_parent_folder+'\\'+meas_folder
nmrObj = nmr_system_2022( client_data_folder )

# report time
tmeas.reportTimeSinceLast("### load libraries")

# import default measurement configuration
from sys_configs.phenc_conf_random import phenc_conf_random
phenc_conf = phenc_conf_random()

# modify the config
phenc_conf.en_fit = True
#phenc_conf.a_est = [20] # array of amplitude estimate for fitting
#phenc_conf.t2_est = [40e-3] # array of t2 estimate for fitting

# run the experiment
cpmg(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)

tmeas.reportTimeSinceLast("### processing")

# clean up
nmrObj.exit()