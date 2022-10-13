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
from nmr_std_function.time_func import time_meas


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:'
meas_folder = 'NMR_DATA'+'\\PHENC_'+datatime
file_name_prefix = 'data_'
absdatapath = data_parent_folder+'\\'+meas_folder
if not os.path.exists(absdatapath):
    os.makedirs(absdatapath)

# variables
client_data_folder = absdatapath
en_fig = 0  # enable figure
report_time = True  # measure time
process_data = 1 # process the NMR data

tmeas = time_meas(report_time)

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
gradz_len_us = 100 # gradient pulse length
gradx_len_us = 100 # gradient pulse length
grad_refocus = 1 # put 1 to enable refocusing of the gradient
flip_grad_refocus_sign = 1 # put 1 to flip the gradient refocusing sign
enc_tao_us = 200 # the encoding time
# gradient strength sweep parameters
grad_volt_Sta = -2.5
grad_volt_Sto = 2.5
grad_volt_Spa = 0.1
grad_volt_Sw = np.arange( grad_volt_Sta, grad_volt_Sto+grad_volt_Spa/2, grad_volt_Spa )

gradz_volt_Sw = grad_volt_Sw
gradx_volt_Sw = grad_volt_Sw

# post-processing parameter
dconv_lpf_ord = 2  # downconversion order
dconv_lpf_cutoff_kHz = 200  # downconversion lpf cutoff
ignore_echoes = 16 # ignore initial echoes for data processing

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
    0.0, # gradz strength set to 0 for reference
    gradx_len_us,
    0.0, # gradz strength set to 0 for reference
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
    # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, en_fig )
    # set compute parameters
    en_ext_rotation = 0 # enable external reference for echo rotation
    thetaref = 0 # external parameter: echo rotation angle
    en_ext_matchfilter = 0 # enable external reference for matched filtering
    echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average 
    # compute data
    a_ref, a_integ_ref, a0_ref, snr_ref, T2_ref, noise_ref, res_ref, theta_ref, data_filt_ref, echo_avg_ref, t_echospace_ref = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, en_fig, en_ext_rotation, thetaref, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
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
swsettings.write ("folder,gradz_voltage\n" %())

data_parser.write_text_overwrite( nmrObj.client_data_folder, phenc_sw_result, "a_integ, a0, snr, T2, noise, res, theta, asum_real, asum_imag" ) # write phenc output data

tmeas.reportTimeSinceLast("############################################################################### load libraries and reference scan")

for i in range( len( gradz_volt_Sw ) ):
    for j in range (len(gradx_volt_Sw)):
        
        ij = i*len(gradz_volt_Sw)+j # iteration number
        
        # print sweep information
        print("\n(%d/%d)(1/2) : gradz = %.3f V -- gradx = %.3f V" %(ij+1,len(gradz_volt_Sw)*len(gradx_volt_Sw),gradz_volt_Sw[i],gradx_volt_Sw[j]))
        
        # write settings
        swsettings.write ("%03d,%02.3f,%02.3f\n" %(ij, gradz_volt_Sw[i], gradx_volt_Sw[j]))
        
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
            gradx_volt_Sw[j],
            grad_refocus,
            flip_grad_refocus_sign,
            enc_tao_us,
            2, # 2 is for p180 y-pulse. 1 is for p180 x-pulse.
            0, # disable lcs precharging
            0 # disable lcs discharging
        )
        
        tmeas.reportTimeSinceLast("############################################################################## cpmg")
        
        if ( process_data ):
            
            indv_datadir = nmrObj.client_data_folder+"\\"+folder_ext+"%03d" % ij
            indv_measdir = meas_folder+"\\"+folder_ext+"%03d" % ij
            
            if not os.path.exists(indv_datadir):
                os.makedirs(indv_datadir)
            
            # compute the generated data
            cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
            cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
            # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, en_fig )
            
            # processing parameters
            en_ext_rotation = 1 # enable external reference for echo rotation
            #thetaref =  # external parameter: echo rotation angle
            en_ext_matchfilter = 0 # enable external reference for matched filtering
            echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
            
            a, a_integ, a0, snr, T2, noise, res, theta, data_filt, echo_avg, t_echospace = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, en_fig, en_ext_rotation, thetaref, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
            
            data_parser.write_text_append( nmrObj.client_data_folder, phenc_sw_result, "%.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f" % (a_integ, a0, snr, T2, noise, res, theta, np.sum(np.real(echo_avg)), np.sum(np.imag(echo_avg)) ))
            
            # shutil.copy(indv_datadir+"\\decay_sum.png", nmrObj.client_data_folder+"\\decay_sum_%03d__%02.3f__%02.3f.png" % (ij, gradz_volt_Sw[i],gradx_volt_Sw[j]))
            # shutil.copy(indv_datadir+"\\echo_shape.png", nmrObj.client_data_folder+"\\echo_shape_%03d__%02.3f__%02.3f.png" % (ij, gradz_volt_Sw[i],gradx_volt_Sw[j]))
            # shutil.copy(indv_datadir+"\\echo_spect.png", nmrObj.client_data_folder+"\\echo_spect_%03d__%02.3f__%02.3f.png" % (ij, gradz_volt_Sw[i],gradx_volt_Sw[j]))
            
        tmeas.reportTimeSinceLast("############################################################################## data processing")

swsettings.close()



















## sweep measurements
folder_ext = "X" # signifies X pulse

# write sweep parameters
phenc_sw_result = "phenc_info_"+folder_ext+".txt"
sw_settings_filename = "sw_settings_"+folder_ext+".txt"

# open sweep settings file
swsettings  = open(  absdatapath+"\\" + sw_settings_filename, 'w' )
swsettings.write ("folder,gradz_voltage\n" %())

data_parser.write_text_overwrite( nmrObj.client_data_folder, phenc_sw_result, "a_integ, a0, snr, T2, noise, res, theta" ) # write phenc output data

for i in range( len( gradz_volt_Sw ) ):
    
    for j in range (len(gradx_volt_Sw)):
    
        ij = i*len(gradz_volt_Sw)+j # iteration number
        
        # print sweep information
        print("\n(%d/%d)(2/2) : gradz = %.3f V -- gradx = %.3f V" %(ij+1,len(gradz_volt_Sw)*len(gradx_volt_Sw),gradz_volt_Sw[i],gradx_volt_Sw[j]))
        
        # write settings
        swsettings.write ("%03d,%02.3f,%02.3f\n" %(ij, gradz_volt_Sw[i], gradx_volt_Sw[j]))
        
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
            gradx_volt_Sw[j],
            grad_refocus,
            flip_grad_refocus_sign,
            enc_tao_us,
            2, # 2 is for p180 y-pulse. 1 is for p180 x-pulse.
            0, # disable lcs precharging
            0 # disable lcs discharging
        )
        
        tmeas.reportTimeSinceLast("############################################################################## cpmg")
        
        if ( process_data ):
            
            indv_datadir = nmrObj.client_data_folder+"\\"+folder_ext+"%03d" % ij
            indv_measdir = meas_folder+"\\"+folder_ext+"%03d" % ij
            
            if not os.path.exists(indv_datadir):
                os.makedirs(indv_datadir)
            
            # compute the generated data
            cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
            cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
            # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, en_fig )
            
            # processing parameters
            en_ext_rotation = 1 # enable external reference for echo rotation
            # thetaref = 0 # external parameter: echo rotation angle
            en_ext_matchfilter = 0 # enable external reference for matched filtering
            echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
            
            a, a_integ, a0, snr, T2, noise, res, theta, data_filt, echo_avg, t_echospace = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, en_fig, en_ext_rotation, thetaref, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
            
            data_parser.write_text_append( nmrObj.client_data_folder, phenc_sw_result, "%.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f" % (a_integ, a0, snr, T2, noise, res, theta, np.sum(np.real(echo_avg)), np.sum(np.imag(echo_avg)) ))
            
            # shutil.copy(indv_datadir+"\\decay_sum.png", nmrObj.client_data_folder+"\\decay_sum_%03d__%02.3f__%02.3f.png" % (ij, gradz_volt_Sw[i],gradx_volt_Sw[j]))
            # shutil.copy(indv_datadir+"\\echo_shape.png", nmrObj.client_data_folder+"\\echo_shape_%03d__%02.3f__%02.3f.png" % (ij, gradz_volt_Sw[i],gradx_volt_Sw[j]))
            # shutil.copy(indv_datadir+"\\echo_spect.png", nmrObj.client_data_folder+"\\echo_spect_%03d__%02.3f__%02.3f.png" % (ij, gradz_volt_Sw[i],gradx_volt_Sw[j]))
            
        tmeas.reportTimeSinceLast("############################################################################## data processing")

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
        gradx_volt_Sw[j],
        grad_refocus,
        flip_grad_refocus_sign,
        enc_tao_us,
        2, # 2 is for p180 y-pulse. 1 is for p180 x-pulse.
        0, # disable lcs precharging
        1 # enable lcs discharging
    )