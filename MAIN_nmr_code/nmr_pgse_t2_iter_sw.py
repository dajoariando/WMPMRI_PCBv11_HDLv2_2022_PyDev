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
meas_folder = 'NMR_DATA'+'\\PGSE_'+datatime
file_name_prefix = 'data_'
absdatapath = data_parent_folder+'\\'+meas_folder
if not os.path.exists(absdatapath):
    os.makedirs(absdatapath)

# variables
client_data_folder = absdatapath
en_fig = 0  # enable figure
meas_time = 0  # measure time
process_data = 1

if ( meas_time ):
    start_time = time.time()

plen_base = 5 # the precharging length base
refill_mult = 2.2 # the refill multiplication to compensate RF loss
p180_p90_fact = 1.6 # multiplication factor between p90 to p180 length

# cpmg settings
cpmg_freq = 4.08
bstrap_pchg_us = 2000
lcs_pchg_us = 20
lcs_dump_us = 100
p90_pchg_us = plen_base
p90_pchg_refill_us = plen_base*refill_mult
p90_us = 5.6
p90_dchg_us = 100
p90_dtcl = 0.5
p180_pchg_us = plen_base *p180_p90_fact
p180_pchg_refill_us = plen_base*refill_mult*p180_p90_fact
p180_us = p90_us
p180_dchg_us = p90_dchg_us
p180_dtcl = 0.5
echoshift_us = 5
echotime_us = 1000
scanspacing_us = 2000000
samples_per_echo = 512
echoes_per_scan = 256
n_iterate = 32 # measurement iteration
ref_iterate = 32 # reference iteration
ph_cycl_en = 1 # phase cycle enable
dconv_fact = 1 # unused for current cpmg code
echoskip = 1 # unused for current cpmg code
echodrop = 0 # unused for current cpmg code
vvarac = -1.55 # more negative, more capacitance
# precharging the vpc
lcs_vpc_pchg_us = 25
lcs_recycledump_us = 1000
lcs_vpc_pchg_repeat = 210
# discharging the vpc
lcs_vpc_dchg_us = 5
lcs_wastedump_us = 200
lcs_vpc_dchg_repeat = 2000

# gradient params sweep parameter
gradlen_us = 400 # gradient pulse length
gradspac_us = echotime_us/2-gradlen_us # gradient pulse spacing
# gradient strength sweep
gradz_volt_Sta = -2.5  # this value must be lower than gradz_volt_Sto
gradz_volt_Sto = 2.5
gradz_volt_Spa = 0.5
gradz_volt_Sw = np.arange( gradz_volt_Sta, gradz_volt_Sto+gradz_volt_Spa/2, gradz_volt_Spa )

# write sweep parameters
swsettings  = open(  absdatapath+"\\sw_settings.txt", 'w' )
swsettings.write ("folder,gradz_voltage\n" %())

# processing parameters
dconv_lpf_ord = 3  # downconversion order
dconv_lpf_cutoff_kHz = 100  # downconversion lpf cutoff


# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )


# generate reference (set gradient to 0.0)
# set a higher number of iteration
nmrObj.pgse_t2_iter(
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
    ref_iterate,
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
    gradlen_us,
    gradspac_us,
    0.0
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
    en_ext_param = 0
    thetaref = 0
    echoref_avg = 0
    direct_read = 0
    datain = 0
    # compute data
    a_ref, a_integ_ref, a0_ref, snr_ref, T2_ref, noise_ref, res_ref, theta_ref, data_filt_ref, echo_avg_ref, t_echospace_ref = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, en_fig, en_ext_param, thetaref, echoref_avg, direct_read, datain, dconv_lpf_ord, dconv_lpf_cutoff_kHz )
    # transfer data
    shutil.copy(indv_datadir+"\\decay_sum.png", nmrObj.client_data_folder+"\\decay_sum_ref.png" )
    shutil.copy(indv_datadir+"\\echo_shape.png", nmrObj.client_data_folder+"\\echo_shape_ref.png" )
    shutil.copy(indv_datadir+"\\echo_spect.png", nmrObj.client_data_folder+"\\echo_spect_ref.png" )


# sweep measurements
data_parser.write_text_overwrite( nmrObj.client_data_folder, "pgse_info.txt", "a_integ, a0, snr, T2, noise, res, theta" ) # write pgse data

for i in range( len( gradz_volt_Sw ) ):
    # write settings
    swsettings.write ("%03d,%02.3f\n" %(i, gradz_volt_Sw[i]))
    
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "set parameter time: %.3f" % ( elapsed_time ) )
        start_time = time.time()
    
    # run cpmg sequence
    nmrObj.pgse_t2_iter(
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
        gradlen_us,
        gradspac_us,
        gradz_volt_Sw[i]
    )
    
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "cpmgSequence acquisition time: %.3f" % ( elapsed_time ) )
        start_time = time.time()
    
    if ( process_data ):
        
        indv_datadir = nmrObj.client_data_folder+"\\%03d" % i
        indv_measdir = meas_folder+"\\%03d" % i
        
        if not os.path.exists(indv_datadir):
            os.makedirs(indv_datadir)
        
        # compute the generated data
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
        cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
        # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, en_fig )
        
        # processing parameters
        en_ext_param = 0 # enable external parameter rotation and matched filtering
        thetaref = theta_ref
        echoref_avg = echo_avg_ref
        direct_read = 0
        datain = 0
        
        a, a_integ, a0, snr, T2, noise, res, theta, data_filt, echo_avg, t_echospace = compute_multiple( nmrObj, data_parent_folder, indv_measdir, file_name_prefix, en_fig, en_ext_param, thetaref, echoref_avg, direct_read, datain, dconv_lpf_ord, dconv_lpf_cutoff_kHz )
        
        data_parser.write_text_append( nmrObj.client_data_folder, "pgse_info.txt", "%.5f %.5f %.3f %.3f %.3f %.3f %.3f" % (a_integ, a0, snr, T2, noise, res, theta))
        
        shutil.copy(indv_datadir+"\\decay_sum.png", nmrObj.client_data_folder+"\\decay_sum_%03d__%02.3f.png" % (i, gradz_volt_Sw[i]))
        shutil.copy(indv_datadir+"\\echo_shape.png", nmrObj.client_data_folder+"\\echo_shape_%03d__%02.3f.png" % (i, gradz_volt_Sw[i]))
        shutil.copy(indv_datadir+"\\echo_spect.png", nmrObj.client_data_folder+"\\echo_spect_%03d__%02.3f.png" % (i, gradz_volt_Sw[i]))
        
    if ( meas_time ):
        elapsed_time = time.time() - start_time
        print( "data processing time: %.3f" % ( elapsed_time ) )
        start_time = time.time()

swsettings.close()