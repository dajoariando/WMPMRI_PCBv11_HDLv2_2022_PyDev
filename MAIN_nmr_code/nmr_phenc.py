'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

import os
import time
from datetime import datetime
from scipy import signal
import matplotlib.pyplot as plt

from nmr_std_function.data_parser import parse_csv_float2col
from nmr_std_function.data_parser import parse_simple_info
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir
from nmr_std_function.nmr_functions import plot_echosum
from nmr_std_function.time_func import time_meas
from nmr_std_function.expts_functions import phenc


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = '\\phenc_'+datatime

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
from sys_configs.phenc_conf_halbach_v10_241205_oil_sys1 import scan_config
phenc_conf = scan_config()

# modify the experiment parameters
phenc_conf.gradz_volt = 1
phenc_conf.gradx_volt = 1
phenc_conf.gradz_len_us = 100
phenc_conf.gradx_len_us = 100
phenc_conf.enc_tao_us = 500

# run the experiment
phenc(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)

tmeas.reportTimeSinceLast("### processing")

# clean up
nmrObj.exit()