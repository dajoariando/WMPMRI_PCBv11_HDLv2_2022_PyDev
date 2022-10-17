'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

import os
import time
from datetime import datetime

import numpy as np

from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function import data_parser
from nmr_std_function.time_func import time_meas
from nmr_std_function.experiments import phenc,phenc_ReIm

# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# measurements folder settings
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = 'PHENC_2D_'+datatime

# create folder for measurements
client_data_folder = data_parent_folder+'\\'+meas_folder
if not os.path.exists(client_data_folder):
    os.makedirs(client_data_folder)

# variables
sav_fig = 0 # save figures
show_fig = 0  # show figures
report_time = True  # measure time
process_data = 1 # process the NMR data

tmeas = time_meas(report_time)

# import default measurement configuration and modify
from sys_configs.phenc_conf_221015 import phenc_conf_221015
phenc_conf = phenc_conf_221015()

# modify default parameters
phenc_conf.n_iterate = 2
phenc_conf.gradz_len_us = 800 # gradient pulse length
phenc_conf.gradx_len_us = 800 # gradient pulse length
phenc_conf.enc_tao_us = 1000 # the encoding time

# gradient strength sweep parameters
grad_volt_Sta = -0.1
grad_volt_Sto = 0.1
grad_volt_Spa = 0.1
grad_volt_Sw = np.arange( grad_volt_Sta, grad_volt_Sto+grad_volt_Spa/2, grad_volt_Spa )

# modify grad_volt_Sw to account for 100mA biasing in the gradient circuit
# the current is 0 when it's set to +/- 0.1V, instead of 0V.
for idx,v in enumerate(grad_volt_Sw):
    if v > 0.0001 : # use 0.01 instead of 0.0 to avoid deal with floating point number around 0.0
        grad_volt_Sw[idx] = v+0.1
    elif v<(-0.0001) :
        grad_volt_Sw[idx] = v-0.1
    else :
        grad_volt_Sw[idx] = 0.1 # 0.1V means 0.1A to the transistor but 0.0A to the coil, because the other transistor is biased at 0.1A when it's turned off.
        
gradz_volt_Sw = grad_volt_Sw
gradx_volt_Sw = grad_volt_Sw

# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )

print("\n(Reference scan)" )
nmrObj.folder_extension = "\\ref"
phenc_conf.en_lcs_dchg = 0 # disable lcs precharging
_, _, _, _, _, _, _, theta_ref = phenc (nmrObj, phenc_conf)



# write sweep parameters
phenc_sw_result = "phenc_info.txt"
sw_settings_filename = "sw_settings.txt"

# open sweep settings file
swsettings  = open(  nmrObj.client_data_folder+"\\" + sw_settings_filename, 'w' )
swsettings.write ("folder,gradz_voltage\n" %())

# write phenc output data
data_parser.write_text_overwrite( nmrObj.client_data_folder, phenc_sw_result, "asum_re, asum_im" ) 

tmeas.reportTimeSinceLast("############################################################################### load libraries and reference scan")

for i in range( len( gradz_volt_Sw ) ):
    for j in range (len(gradx_volt_Sw)):
        
        ij = i*len(gradz_volt_Sw)+j # iteration number
        
        # print sweep information
        print("\n(%d/%d) : gradz = %.3f V -- gradx = %.3f V" %(ij+1,len(gradz_volt_Sw)*len(gradx_volt_Sw),gradz_volt_Sw[i],gradx_volt_Sw[j]))
        
        # write settings
        swsettings.write ("%03d,%02.3f,%02.3f\n" %(ij, gradz_volt_Sw[i], gradx_volt_Sw[j]))
        
        # run cpmg sequence
        phenc_conf.en_lcs_pchg = 0
        phenc_conf.en_lcs_dchg = 0
        phenc_conf.p180_xy_angle = 2 # set for Y pulse for p180
        phenc_conf.gradz_volt = gradz_volt_Sw[i]
        phenc_conf.gradx_volt = gradx_volt_Sw[j]
                 
        # processing parameters
        phenc_conf.en_ext_rotation = 1 # enable external reference for echo rotation
        phenc_conf.thetaref = theta_ref# external parameter: echo rotation angle
        phenc_conf.en_conj_matchfilter = 0 # disable conjugate matchfiltering because it will auto-rotate the data
        phenc_conf.en_ext_matchfilter = 0 # enable external reference for matched filtering
        phenc_conf.echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
        
        # folder parameter
        nmrObj.folder_extension = "\\"+"dat_"+"%03d" % ij
        
        # run measurement and process data
        asum_cmplx = phenc_ReIm(nmrObj, phenc_conf)
        
        # write data to file
        data_parser.write_text_append( nmrObj.client_data_folder, phenc_sw_result, "%.6f %.6f" % (np.real(asum_cmplx), np.imag(asum_cmplx)))
        
        tmeas.reportTimeSinceLast("############################################################################## cpmg & processing")

swsettings.close()



# DUMMY SCAN: discharge power from the lcs
phenc_conf.en_lcs_pchg = 0
phenc_conf.en_lcs_dchg = 1
phenc_conf.p180_xy_angle = 1 # set for X p180 pulse
nmrObj.phenc_t2_iter( phenc_conf )