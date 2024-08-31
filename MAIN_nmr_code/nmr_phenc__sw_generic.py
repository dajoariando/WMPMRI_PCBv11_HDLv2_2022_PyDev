'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.time_func import time_meas
from nmr_std_function.expts_functions import cpmg


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = '\\sw_generic_'+datatime

# variables
expt_num = 0 # set to 0 for a single experiment

# enable time measurement
tmeas = time_meas(True)

# instantiate nmr object
client_data_folder = data_parent_folder+'\\'+meas_folder
nmrObj = nmr_system_2022( client_data_folder )

# report time
tmeas.reportTimeSinceLast("### load libraries")

# import default measurement configuration
from sys_configs.phenc_conf_halbach_v03_240810_oil import phenc_conf_halbach_v03_240810_oil
phenc_conf = phenc_conf_halbach_v03_240810_oil()

# sweep val_sw
val_center = 2.0
val_range = 2
val_npts = 21
val_sw = np.linspace(val_center-0.5*val_range,val_center+0.5*val_range,val_npts)

# modify the experiment parameters
phenc_conf.gradz_volt = 0.1
phenc_conf.gradx_volt = 0.1
phenc_conf.gradz_len_us = 100
phenc_conf.gradx_len_us = 100
phenc_conf.enc_tao_us = 200

# perform reference scan
print("\n(Reference scan)" )
nmrObj.folder_extension = "\\ref"
phenc_conf.en_lcs_pchg = 1 # enable lcs precharging
phenc_conf.en_lcs_dchg = 0 # enable lcs discharging
expt_num = 0 # set to 0 for a single experiment
sav_fig = 1 # save figure for reference scan
show_fig = 1 # show figure for reference scan
# _, _, _, _, _, _, _, theta_ref, _, _ = phenc (nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
_, _, _, _, _, _, _, theta_ref, _, _, _, _ = cpmg(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)

# post-processing parameters for the phase encoding imaging
nmrObj.folder_extension = ("") # remove the folder extension and use only the data directory to process the data
phenc_conf.en_ext_rotation = 0 # enable external reference for echo rotation
phenc_conf.thetaref = theta_ref # external parameter: echo rotation angle
phenc_conf.en_conj_matchfilter = 0 # disable conjugate matchfiltering because it will auto-rotate the data
phenc_conf.en_ext_matchfilter = 0 # enable external reference for matched filtering
phenc_conf.echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
sav_fig = 1 # save figures
show_fig = 0  # show figures

# settings for measurements
phenc_conf.en_lcs_pchg = 0 # disable lcs precharging because the vpc is already precharged by the reference scan
phenc_conf.en_lcs_dchg = 0 # disable lcs discharging because the vpc has to maintain its voltage for next scan

# data container
# set data containers
asum_re = np.zeros(val_npts);
asum_im = np.zeros(val_npts);
theta = np.zeros(val_npts);

# run the sweep
for i,val_curr in enumerate(val_sw):
    
    if (i==len(val_sw)-1):
        phenc_conf.en_lcs_dchg = 1 # enable discharging at the last iteration to dump vpc voltage
    
    print("\t\t\t\texpt: %d/%d ----- val = %0.3f " % (i,len(val_sw)-1,val_curr) )
    
    # val to sweep
    phenc_conf.p180_p90_fact = val_curr
    phenc_conf.p180_pchg_us = phenc_conf.plen_base *phenc_conf.p180_p90_fact
    phenc_conf.p180_pchg_refill_us = phenc_conf.plen_base*phenc_conf.refill_mult*phenc_conf.p180_p90_fact
    phenc_conf.p180_dchg_us = phenc_conf.p180_pchg_us+phenc_conf.p180_pchg_refill_us # used to be p90_dchg_us
    
    
    expt_num = i
    # asum_re[i], asum_im[i], _, _, _, _, _, theta[i], _, _= phenc(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    asum_re[i], asum_im[i], _, _, _, _, _, theta[i], _, _, _, _ = cpmg(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    
    # plot the figure
    plt.ion()
    fig = plt.figure(77, figsize=(14,8))
    fig.clf()
    ax1 = fig.add_subplot( 3, 1, 1 )
    ax1.plot( val_sw[0:i+1],asum_re[0:i+1], '-o' )
    # ax1.plot( asum_im[0:i+1], '-o' )
    ax1.grid()
    plt.ylabel("asum_re")
    # ax1.legend(["re", "im"])
    
    ax2 = fig.add_subplot( 3, 1, 2 )
    ax2.plot( val_sw[0:i+1],asum_im[0:i+1], '-o' )
    ax2.grid()
    plt.ylabel("asum_im")
    
    ax3 = fig.add_subplot( 3, 1, 3 )
    ax3.plot( val_sw[0:i+1],theta[0:i+1]/(2*np.pi)*360, '-o' )
    ax3.grid()
    plt.ylabel("theta (degrees)")

    
    fig.canvas.draw()
    fig.canvas.flush_events()
    
plt.savefig(nmrObj.client_data_folder+"\\monitor_plot.png")  
tmeas.reportTimeSinceLast("### processing")

# clean up
nmrObj.exit()