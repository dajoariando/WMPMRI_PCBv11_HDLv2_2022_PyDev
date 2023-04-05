'''
Created on March 30, 2023

DIffusion measurement using the phase encoding experiment, with pulse gradient set to 0.1V or equivalent to 0.1A.
The default gradient of 0.1A at the other FET of the gradient will null this.

@author: David Ariando

'''

#!/usr/bin/python

import os
import time
from datetime import datetime
import pydevd
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

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
meas_folder = '\\phenc_diffusion_'+datatime

# variables
expt_num = 0 # set to 0 for a single experiment
sav_fig = 1 # save figures
show_fig = 0  # show figures

# enable time measurement
tmeas = time_meas(True)

# instantiate nmr object
client_data_folder = data_parent_folder+'\\'+meas_folder
nmrObj = nmr_system_2022( client_data_folder )

# report time
tmeas.reportTimeSinceLast("### load libraries")

# import default measurement configuration
from sys_configs.phenc_conf_halbach_v03_230323 import phenc_conf_halbach_v03_230323
phenc_conf = phenc_conf_halbach_v03_230323()

# modify the experiment parameters
phenc_conf.gradz_volt = 0.10
phenc_conf.gradx_volt = 0.10
phenc_conf.gradz_len_us = 1
phenc_conf.gradx_len_us = 1

# set list of the the enc_tao_us
enc_tao_us_sw = np.linspace(100, 10000, 100)

asum_re = np.zeros(np.size(enc_tao_us_sw));
asum_im = np.zeros(np.size(enc_tao_us_sw));
a0_list = np.zeros(np.size(enc_tao_us_sw));
T2 = np.zeros(np.size(enc_tao_us_sw));



for i in range(0,np.size(enc_tao_us_sw,0)):

    phenc_conf.enc_tao_us = enc_tao_us_sw[i]
    expt_num = i

    # run the experiment
    asum_re[i], asum_im[i], a0, _, T2[i], _, _, _, _ = phenc(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    a0_list[i] = a0[0];
    
    tmeas.reportTimeSinceLast("### processing")

np.savetxt(nmrObj.client_data_folder+"\\enc_tao_us_sw.txt",enc_tao_us_sw,fmt='%0.2f')
np.savetxt(nmrObj.client_data_folder+"\\asum_re.txt",asum_re,fmt='%0.10f')
np.savetxt(nmrObj.client_data_folder+"\\asum_im.txt",asum_im,fmt='%0.10f')
np.savetxt(nmrObj.client_data_folder+"\\a0.txt",a0_list,fmt='%0.10f')
np.savetxt(nmrObj.client_data_folder+"\\T2.txt",T2,fmt='%0.10f')


# clean up
nmrObj.exit()