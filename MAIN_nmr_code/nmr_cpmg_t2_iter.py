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
from nmr_std_function.nmr_functions import compute_multiple


# get the current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# create folder for measurements
data_parent_folder = 'D:'
meas_folder = 'NMR_DATA'+'\\T2_'+datatime
file_name_prefix = 'data_'
absdatapath = data_parent_folder+'\\'+meas_folder
if not os.path.exists(absdatapath):
    os.makedirs(absdatapath)

# variables
client_data_folder = absdatapath
en_fig = 1  # enable figure
meas_time = 0  # measure time
process_data = 1

if ( meas_time ):
    start_time = time.time()

plen_base = 5 # the precharging length base
refill_mult = 2.4 # the refill multiplication to compensate RF loss
p180_p90_fact = 1.6 # multiplication factor between p90 to p180 length

# cpmg settings
cpmg_freq = 4.08
bstrap_pchg_us = 2000
lcs_pchg_us = 20
lcs_dump_us = 100
p90_pchg_us = plen_base
p90_pchg_refill_us = plen_base*refill_mult
p90_us = 6.0
p90_dchg_us = 100
p90_dtcl = 0.5
p180_pchg_us = plen_base *p180_p90_fact
p180_pchg_refill_us = plen_base*refill_mult*p180_p90_fact
p180_us = p90_us
p180_dchg_us = p90_dchg_us
p180_dtcl = 0.5
echoshift_us = 5
echotime_us = 300
scanspacing_us = 300000
samples_per_echo = 512
echoes_per_scan = 256
n_iterate = 1 # unused for current cpmg code
ph_cycl_en = 1 # phase cycle enable
dconv_fact = 1 # unused for current cpmg code
echoskip = 1 # unused for current cpmg code
echodrop = 0 # unused for current cpmg code
vvarac = -1.46 # more negative, more capacitance
# precharging the vpc
lcs_vpc_pchg_us = 25
lcs_recycledump_us = 1000
lcs_vpc_pchg_repeat = 210
# discharging the vpc
lcs_vpc_dchg_us = 5
lcs_wastedump_us = 200
lcs_vpc_dchg_repeat = 2000

# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )

if ( meas_time ):
    elapsed_time = time.time() - start_time
    print( "set parameter time: %.3f" % ( elapsed_time ) )
    start_time = time.time()

# run cpmg sequence
nmrObj.cpmg_t2_iter(
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
    lcs_vpc_dchg_repeat
)

if ( meas_time ):
    elapsed_time = time.time() - start_time
    print( "cpmgSequence acquisition time: %.3f" % ( elapsed_time ) )
    start_time = time.time()

if ( process_data ):
    
    
    # compute the generated data
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "datasum.txt" )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "acqu.par" )
    # plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "datasum.txt", samples_per_echo, echoes_per_scan, en_fig )
    
    
    en_ext_param = 0
    thetaref = 0
    echoref_avg = 0
    direct_read = 0
    datain = 0
    dconv_lpf_ord = 2  # downconversion order
    dconv_lpf_cutoff_kHz = 100  # downconversion lpf cutoff
    
    compute_multiple( nmrObj, data_parent_folder, meas_folder, file_name_prefix, en_fig, en_ext_param, thetaref, echoref_avg, direct_read, datain, dconv_lpf_ord, dconv_lpf_cutoff_kHz )
    
if ( meas_time ):
    elapsed_time = time.time() - start_time
    print( "data processing time: %.3f" % ( elapsed_time ) )
    start_time = time.time()
