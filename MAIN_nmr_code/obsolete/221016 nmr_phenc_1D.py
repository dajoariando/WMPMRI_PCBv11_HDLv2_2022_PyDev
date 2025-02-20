'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

import os
import time
from datetime import datetime

import pydevd
import numpy as np
from scipy import signal
import shutil

import matplotlib.pyplot as plt
from nmr_std_function.data_parser import parse_csv_float2col
from nmr_std_function.data_parser import parse_simple_info
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir
from nmr_std_function.nmr_functions import plot_echosum
from nmr_std_function.nmr_functions import compute_multiple
from nmr_std_function import data_parser


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:'
meas_folder = 'NMR_DATA'+'\\PHENC_1D_'+datatime
file_name_prefix = 'data_'
absdatapath = data_parent_folder+'\\'+meas_folder
if not os.path.exists(absdatapath):
    os.makedirs(absdatapath)

# variables
client_data_folder = absdatapath
sav_fig = 0 # save figures
show_fig = 0  # show figures
meas_time = 0  # measure time
process_data = 1

if ( meas_time ):
    start_time = time.time()

# pulse parameters
plen_base = 5.00 # the precharging length base
refill_mult = 0.6 # the refill multiplication to compensate RF loss
p180_p90_fact = 1.6 # multiplication factor between p90 to p180 length

# cpmg settings
cpmg_freq = 4.1
bstrap_pchg_us = 2000
lcs_pchg_us = 20
lcs_dump_us = 100
p90_pchg_us = plen_base
p90_pchg_refill_us = plen_base*refill_mult
p90_us = 10
p90_dchg_us = 100
p90_dtcl = 0.5
p180_pchg_us = plen_base *p180_p90_fact
p180_pchg_refill_us = plen_base*refill_mult*p180_p90_fact
p180_us = p90_us
p180_dchg_us = p90_dchg_us
p180_dtcl = 0.5
echoshift_us = 10
echotime_us = 500
scanspacing_us = 100000
samples_per_echo = 4096
echoes_per_scan = 64
n_iterate = 4 # unused for current cpmg code
ph_cycl_en = 1 # phase cycle enable
dconv_fact = 1 # unused for current cpmg code
echoskip = 1 # unused for current cpmg code
echodrop = 0 # unused for current cpmg code
vvarac = -1.65 # set to -1.6 for Gy # more negative, more capacitance
# precharging the vpc
lcs_vpc_pchg_us = 25
lcs_recycledump_us = 1000
lcs_vpc_pchg_repeat = 210
# discharging the vpc
lcs_vpc_dchg_us = 5
lcs_wastedump_us = 200
lcs_vpc_dchg_repeat = 2000
# gradient params
gradz_len_us = 1000 # gradient pulse length
gradx_len_us = 1000 # gradient pulse length
grad_refocus = 1 # put 1 to enable refocusing of the gradient
flip_grad_refocus_sign = 1 # put 1 to flip the gradient refocusing sign
enc_tao_us = 1100 # the encoding time
# gradient strength sweep parameters
grad_volt_Sta = -2.0
grad_volt_Sto = 2.0
grad_volt_Spa = 0.05
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



# apply to z or x direction
apply_gz = False # put True of False. Either gx or gz must be true
apply_gx = True # put True of False

# post-processing parameter
dconv_lpf_ord = 2  # downconversion order
dconv_lpf_cutoff_kHz = 200  # downconversion lpf cutoff
ignore_echoes = 16 # ignore initial echoes for data processing

if apply_gz:
    gradz_volt_Sw = grad_volt_Sw
else:
    gradz_volt_Sw = np.zeros(len(grad_volt_Sw))
if apply_gx:
    gradx_volt_Sw = grad_volt_Sw
else:
    gradx_volt_Sw = np.zeros(len(grad_volt_Sw))

# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )

print("\n(Reference scan)" )
# generate reference (set gradient to 0.0)
# set a higher number of iteration
nmrObj.phenc_t2_iter(
    cpmg_freq,
    bstrap_pchg_us,
    lcs_pchg_us,
    lcs_dump_us,
    p90_pchg_us,
    p90_pchg_refill_us,
    p90_us,
    p90_dchg_us,
    p90_dtcl,
    p180_pchg_us,
    p180_pchg_refill_us,
    p180_us,
    p180_dchg_us,
    p180_dtcl,
    echoshift_us,
    echotime_us,
    scanspacing_us,
    samples_per_echo,
    echoes_per_scan,
    n_iterate,
    ph_cycl_en,
    dconv_fact,
    echoskip,
    echodrop,
    vvarac,
    lcs_vpc_pchg_us,
    lcs_recycledump_us,
    lcs_vpc_pchg_repeat, 
    lcs_vpc_dchg_us,
    lcs_wastedump_us,
    lcs_vpc_dchg_repeat,
    gradz_len_us,
    0.1, # gradz strength set to 0 for reference
    gradx_len_us,
    0.1, # gradz strength set to 0 for reference
    grad_refocus,
    flip_grad_refocus_sign,
    enc_tao_us,
    2, # 2 is for p180 y pulse
    1, # enable lcs precharging
    0, # disable lcs discharging
)
# process ref data
if ( process_data ):
    # define folder
    indv_datadir = nmrObj.client_data_folder+"\\ref"
    indv_measdir = meas_folder+"\\ref"
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # compute the generated data
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
    # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, show_fig )
    # set compute parameters
    en_ext_rotation = 0 # enable external reference for echo rotation
    thetaref = 0 # external parameter: echo rotation angle
    en_ext_matchfilter = 0 # enable external reference for matched filtering
    echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average 
    # compute data
    _, _, _, _, _, _, _, _, theta_ref, _, _, _ = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, sav_fig, show_fig, en_ext_rotation, thetaref, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
    # transfer data
    # shutil.copy(indv_datadir+"\\decay_sum.png", nmrObj.client_data_folder+"\\decay_sum_ref.png" )
    # shutil.copy(indv_datadir+"\\echo_shape.png", nmrObj.client_data_folder+"\\echo_shape_ref.png" )
    # shutil.copy(indv_datadir+"\\echo_spect.png", nmrObj.client_data_folder+"\\echo_spect_ref.png" )


# sweep measurements
folder_ext = "Y" # signifies Y pulse

# write sweep parameters
phenc_sw_result = "phenc_info_"+folder_ext+".txt"
sw_settings_filename = "sw_settings_"+folder_ext+".txt"

# open sweep settings file
swsettings  = open(  absdatapath+"\\" + sw_settings_filename, 'w' )
swsettings.write ("folder,grad_voltage\n" %())

data_parser.write_text_overwrite( nmrObj.client_data_folder, phenc_sw_result, "asum_re, asum_im, a0, snr, T2, noise, res, theta" ) # write phenc output data

for i in range( len( grad_volt_Sw ) ):
    # print sweep information
    print("\n(%d/%d) : grad = %.3f V" %(i+1,len(grad_volt_Sw),grad_volt_Sw[i]))
    
    # write settings
    swsettings.write ("%03d,%02.3f\n" %(i, grad_volt_Sw[i]))
    
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "set parameter time: %.3f" % ( elapsed_time ) )
        start_time = time.time()
    
    # run cpmg sequence
    nmrObj.phenc_t2_iter(
        cpmg_freq,
        bstrap_pchg_us,
        lcs_pchg_us,
        lcs_dump_us,
        p90_pchg_us,
        p90_pchg_refill_us,
        p90_us,
        p90_dchg_us,
        p90_dtcl,
        p180_pchg_us,
        p180_pchg_refill_us,
        p180_us,
        p180_dchg_us,
        p180_dtcl,
        echoshift_us,
        echotime_us,
        scanspacing_us,
        samples_per_echo,
        echoes_per_scan,
        n_iterate,
        ph_cycl_en,
        dconv_fact,
        echoskip,
        echodrop,
        vvarac,
        lcs_vpc_pchg_us,
        lcs_recycledump_us,
        lcs_vpc_pchg_repeat, 
        lcs_vpc_dchg_us,
        lcs_wastedump_us,
        lcs_vpc_dchg_repeat,
        gradz_len_us,
        gradz_volt_Sw[i],
        gradx_len_us,
        gradx_volt_Sw[i],
        grad_refocus,
        flip_grad_refocus_sign,
        enc_tao_us,
        2, # 2 is for p180 y-pulse. 1 is for p180 x-pulse.
        0, # disable lcs precharging
        0 # disable lcs discharging
    )
    
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "cpmgSequence acquisition time: %.3f" % ( elapsed_time ) )
        start_time = time.time()
    
    if ( process_data ):
        
        indv_datadir = nmrObj.client_data_folder+"\\"+folder_ext+"%03d" % i
        indv_measdir = meas_folder+"\\"+folder_ext+"%03d" % i
        
        if not os.path.exists(indv_datadir):
            os.makedirs(indv_datadir)
        
        # compute the generated data
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
        # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, show_fig )
        
        # processing parameters
        en_ext_rotation = 1 # enable external reference for echo rotation
        thetaref = theta_ref # external parameter: echo rotation angle
        en_ext_matchfilter = 0 # enable external reference for matched filtering
        echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
        
        _, asum_re, asum_im, a0, snr, T2, noise, res, theta, _, _, _ = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, sav_fig, show_fig, en_ext_rotation, thetaref, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
        
        data_parser.write_text_append( nmrObj.client_data_folder, phenc_sw_result, "%.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f" % (asum_re, asum_im, a0, snr, T2, noise, res, theta))
        
        # shutil.copy(indv_datadir+"\\decay_sum.png", nmrObj.client_data_folder+"\\decay_sum_%03d__%02.3f.png" % (i, grad_volt_Sw[i]))
        # shutil.copy(indv_datadir+"\\echo_shape.png", nmrObj.client_data_folder+"\\echo_shape_%03d__%02.3f.png" % (i, grad_volt_Sw[i]))
        # shutil.copy(indv_datadir+"\\echo_spect.png", nmrObj.client_data_folder+"\\echo_spect_%03d__%02.3f.png" % (i, grad_volt_Sw[i]))
        
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "data processing time: %.3f" % ( elapsed_time ) )
        start_time = time.time()

swsettings.close()



















## sweep measurements
folder_ext = "X" # signifies X pulse

# write sweep parameters
phenc_sw_result = "phenc_info_"+folder_ext+".txt"
sw_settings_filename = "sw_settings_"+folder_ext+".txt"

# open sweep settings file
swsettings  = open(  absdatapath+"\\" + sw_settings_filename, 'w' )
swsettings.write ("folder,grad_voltage\n" %())

data_parser.write_text_overwrite( nmrObj.client_data_folder, phenc_sw_result, "asum_re, asum_im, a0, snr, T2, noise, res, theta" ) # write phenc output data

for i in range( len( grad_volt_Sw ) ):
    # print sweep information
    print("\n(%d/%d) : grad = %.3f V" %(i+1,len(grad_volt_Sw),grad_volt_Sw[i]))
    
    # write settings
    swsettings.write ("%03d,%02.3f\n" %(i, grad_volt_Sw[i]))
    
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "set parameter time: %.3f" % ( elapsed_time ) )
        start_time = time.time()
    
    # run cpmg sequence
    nmrObj.phenc_t2_iter(
        cpmg_freq,
        bstrap_pchg_us,
        lcs_pchg_us,
        lcs_dump_us,
        p90_pchg_us,
        p90_pchg_refill_us,
        p90_us,
        p90_dchg_us,
        p90_dtcl,
        p180_pchg_us,
        p180_pchg_refill_us,
        p180_us,
        p180_dchg_us,
        p180_dtcl,
        echoshift_us,
        echotime_us,
        scanspacing_us,
        samples_per_echo,
        echoes_per_scan,
        n_iterate,
        ph_cycl_en,
        dconv_fact,
        echoskip,
        echodrop,
        vvarac,
        lcs_vpc_pchg_us,
        lcs_recycledump_us,
        lcs_vpc_pchg_repeat, 
        lcs_vpc_dchg_us,
        lcs_wastedump_us,
        lcs_vpc_dchg_repeat,
        gradz_len_us,
        gradz_volt_Sw[i],
        gradx_len_us,
        gradx_volt_Sw[i],
        grad_refocus,
        flip_grad_refocus_sign,
        enc_tao_us,
        2, # 2 is for p180 y-pulse. 1 is for p180 x-pulse.
        0, # disable lcs precharging
        0 # disable lcs discharging
    )
    
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "cpmgSequence acquisition time: %.3f" % ( elapsed_time ) )
        start_time = time.time()
    
    if ( process_data ):
        
        indv_datadir = nmrObj.client_data_folder+"\\"+folder_ext+"%03d" % i
        indv_measdir = meas_folder+"\\"+folder_ext+"%03d" % i
        
        if not os.path.exists(indv_datadir):
            os.makedirs(indv_datadir)
        
        # compute the generated data
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
        # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, show_fig )
        
        # processing parameters
        en_ext_rotation = 1 # enable external reference for echo rotation
        thetaref = theta_ref # external parameter: echo rotation angle
        en_ext_matchfilter = 0 # enable external reference for matched filtering
        echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
        
        _, asum_re, asum_im, a0, snr, T2, noise, res, theta, _, _, _ = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, sav_fig, show_fig, en_ext_rotation, thetaref, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
        
        data_parser.write_text_append( nmrObj.client_data_folder, phenc_sw_result, "%.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f" % (asum_re, asum_im, a0, snr, T2, noise, res, theta))
        
        # shutil.copy(indv_datadir+"\\decay_sum.png", nmrObj.client_data_folder+"\\decay_sum_%03d__%02.3f.png" % (i, grad_volt_Sw[i]))
        # shutil.copy(indv_datadir+"\\echo_shape.png", nmrObj.client_data_folder+"\\echo_shape_%03d__%02.3f.png" % (i, grad_volt_Sw[i]))
        # shutil.copy(indv_datadir+"\\echo_spect.png", nmrObj.client_data_folder+"\\echo_spect_%03d__%02.3f.png" % (i, grad_volt_Sw[i]))
        
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "data processing time: %.3f" % ( elapsed_time ) )
        start_time = time.time()

swsettings.close()

# DUMMY SCAN: discharge power from the lcs
nmrObj.phenc_t2_iter(
    cpmg_freq,
    bstrap_pchg_us,
    lcs_pchg_us,
    lcs_dump_us,
    p90_pchg_us,
    p90_pchg_refill_us,
    p90_us,
    p90_dchg_us,
    p90_dtcl,
    p180_pchg_us,
    p180_pchg_refill_us,
    p180_us,
    p180_dchg_us,
    p180_dtcl,
    echoshift_us,
    echotime_us,
    scanspacing_us,
    samples_per_echo,
    echoes_per_scan,
    1,
    ph_cycl_en,
    dconv_fact,
    echoskip,
    echodrop,
    vvarac,
    lcs_vpc_pchg_us,
    lcs_recycledump_us,
    lcs_vpc_pchg_repeat, 
    lcs_vpc_dchg_us,
    lcs_wastedump_us,
    lcs_vpc_dchg_repeat,
    gradz_len_us,
    gradz_volt_Sw[i],
    gradx_len_us,
    gradx_volt_Sw[i],
    grad_refocus,
    flip_grad_refocus_sign,
    enc_tao_us,
    2, # 2 is for p180 y-pulse. 1 is for p180 x-pulse.
    0, # disable lcs precharging
    1 # enable lcs discharging
)