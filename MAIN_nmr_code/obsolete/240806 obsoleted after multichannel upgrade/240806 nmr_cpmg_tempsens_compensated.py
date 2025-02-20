'''
Created on March 30, 2023

This is temperature sensing experiment by doing cpmg over a long period of time and see how the frequency changes.

230421 the temperature is compensated by taking into account the temperature shift from previous measurement.

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
from nmr_std_function.expts_functions import cpmg, phenc
from nmr_std_function.data_parser import write_text_append


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = 'cpmg_tempsens_'+datatime

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
from sys_configs.phenc_conf_halbach_v03_230420_tempsens import phenc_conf_halbach_v03_230420_tempsens
phenc_conf = phenc_conf_halbach_v03_230420_tempsens()

# set cpmg settings
phenc_conf.n_iterate = 20 # set minimum iteration (preferably 1, but 2 is fine for phase-cycling
phenc_conf.dummy_scan_num = 1 # set 1 dummy scan to get consistency for the first scan
nscans = 2000 # set the number of scans to be performed
tspac = 0 # set the spacing between scans to check temperature (seconds)

# write general measurement data
write_text_append( nmrObj.client_data_folder, "general_meas_config.txt", "tspac = %0.2f s" % tspac )
write_text_append( nmrObj.client_data_folder, "general_meas_config.txt", "dummy_scan_num = %d" % phenc_conf.dummy_scan_num )

# set settings for scan. use reference scan for rotation and match filtering
phenc_conf.en_ext_rotation = 0 # enable external reference for echo rotation
phenc_conf.thetaref = 0 # external parameter: echo rotation angle
phenc_conf.en_conj_matchfilter = 1 # enable conjugate matchfiltering but it has to be enabled along with ext_matchfilter and external rotation
phenc_conf.en_ext_matchfilter = 0 # enable external reference for matched filtering
en_self_rotation = 1 # enable self rotation with the angle estimated by its own echo (is automatically disactivated when en_ext_rotation is active
phenc_conf.echoref_avg = 0 # external parameter: matched filtering echo average
phenc_conf.en_fit = True # enable fit

# run dummy scan
sav_fig = 1 # save figures
show_fig = 1  # show figures
# _, _, _, _, _, _, _, _, _, _ = cpmg(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
_, _, _, _, _, _, _, _, _, fofst = phenc(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
fstart = phenc_conf.cpmg_freq # save the starting frequency


# set settings for loop
sav_fig = 1 # save figures
show_fig = 0  # show figures

# set data containers
asum_re = np.zeros(nscans);
asum_im = np.zeros(nscans);
a0_list = np.zeros(nscans);
snr = np.zeros(nscans);
T2_list = np.zeros(nscans);
theta = np.zeros(nscans);
fpeak = np.zeros(nscans);
f_list = np.zeros(nscans);

tmeas.reportTimeSinceLast("### start pulse sequence")

for i in range(0,nscans):
    print("scan (%d/%d)" % (i,nscans))
    
    # record the current frequency
    f_list[i] = np.around(phenc_conf.cpmg_freq + np.around(fofst*0.001, decimals=3), decimals=3) # fofst is in kHz range, and cpmg freq is in MHz. Round the frequency to 1 kHz
    
    # add the frequency offset
    phenc_conf.cpmg_freq = f_list[i]
    print("offset: %0.0f kHz. f: %0.3f MHz. f init: %0.3f MHz" % ((phenc_conf.cpmg_freq - fstart)*1000,phenc_conf.cpmg_freq, fstart))
    
    write_text_append( nmrObj.client_data_folder, "time.txt", "%0.2f" % tmeas.getTimeAbs() ) # write the timestamp of the scan
    
    expt_num = i

    # run the experiment
    # asum_re[i], asum_im[i], a0, snr[i], T2, _, _, theta[i], _, fpeak[i] = cpmg(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    asum_re[i], asum_im[i], a0, snr[i], T2, _, _, theta[i], _, fpeak[i] = phenc(nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    a0_list[i] = a0[0] # only take the first fit
    T2_list[i] = T2[0] # only take the first fit
    fofst = fpeak[i] # set the new frequency offset
    
    # plot the figure
    plt.ion()
    fig = plt.figure(77, figsize=(21,8))
    fig.clf()
    ax1 = fig.add_subplot( 3, 3, 1 )
    ax1.plot( asum_re[0:i], '-o' )
    # ax1.plot( asum_im[0:i], '-o' )
    ax1.grid()
    plt.ylabel("asum")
    # ax1.legend(["re", "im"])
    
    ax2 = fig.add_subplot( 3, 3, 2 )
    ax2.plot( a0_list[0:i], '-o' )
    ax2.grid()
    plt.ylabel("a0")
    
    ax3 = fig.add_subplot( 3, 3, 3 )
    ax3.plot( snr[0:i], '-o' )
    ax3.grid()
    plt.ylabel("snr")
    
    ax4 = fig.add_subplot( 3, 3, 4 )
    ax4.plot( T2_list[0:i]*1e3, '-o' )
    ax4.grid()
    plt.ylabel("T2 (ms)")
    
    ax5 = fig.add_subplot( 3, 3, 5 )
    ax5.plot( theta[0:i]/(2*np.pi)*360, '-o' )
    ax5.grid()
    plt.ylabel("theta (degrees)")
    
    ax6 = fig.add_subplot( 3, 3, 6 )
    ax6.plot( fpeak[0:i], '-o' )
    ax6.grid()
    plt.ylabel("fpeak (kHz)")
    
    ax7 = fig.add_subplot( 3, 3, 7 )
    ax7.plot( f_list[0:i], '-o' )
    ax7.plot( f_list[0:i]+fpeak[0:i]/1000)
    ax7.grid()
    plt.ylabel("f (MHz)")
    
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    
    # save the data
    np.savetxt(nmrObj.client_data_folder+"\\asum_re.txt",asum_re,fmt='%0.10f')
    np.savetxt(nmrObj.client_data_folder+"\\asum_im.txt",asum_im,fmt='%0.10f')
    np.savetxt(nmrObj.client_data_folder+"\\a0.txt",a0_list,fmt='%0.10f')
    np.savetxt(nmrObj.client_data_folder+"\\T2.txt",T2,fmt='%0.10f')
    np.savetxt(nmrObj.client_data_folder+"\\snr.txt",snr,fmt='%0.10f')
    np.savetxt(nmrObj.client_data_folder+"\\theta.txt",theta,fmt='%0.10f')
    np.savetxt(nmrObj.client_data_folder+"\\fpeak.txt",fpeak,fmt='%0.10f')
    np.savetxt(nmrObj.client_data_folder+"\\f.txt",f_list,fmt='%0.10f')
    
    os.remove(nmrObj.client_data_folder+"\\dsum_%06d.txt" % i)
    
    scantime = tmeas.reportTimeSinceLast("### scantime") # report the scan time
    if (tspac > 0 ):
        # calculate elapsed time and add delay if necessary
        if (tmeas.TimeSto > tspac):
            print("tspac (%0.2f s) is less than elapsed (%0.2f s)!" % (scantime, tspac))
        else:
            print("sleep for %0.2f s to get %0.2f inter-experiment delay" % (tspac-scantime, tspac))    
            time.sleep(tspac-scantime) # sleep for tspac seconds

plt.savefig(nmrObj.client_data_folder+"\\monitor_plot_compensated.png")     
    
# clean up
nmrObj.exit()