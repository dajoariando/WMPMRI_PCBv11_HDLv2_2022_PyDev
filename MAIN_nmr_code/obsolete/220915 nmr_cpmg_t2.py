'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

import os
import time

import pydevd
from scipy import signal

import matplotlib.pyplot as plt
from nmr_std_function.data_parser import parse_csv_float2col
from nmr_std_function.data_parser import parse_simple_info
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir
from nmr_std_function.nmr_functions import plot_echosum

# variables
client_data_folder = "D:\\NMR_DATA"
en_fig = 1  # enable figure
meas_time = 0  # measure time
process_data = 1

if ( meas_time ):
    start_time = time.time()

plen_base = 5

# cpmg settings
cpmg_freq = 4.0
bstrap_pchg_us = 2000
lcs_pchg_us = 50
lcs_dump_us = 100
p90_pchg_us = plen_base
p90_pchg_refill_us = plen_base*5
p90_us = 5
p90_dchg_us = 20
p90_dtcl = 0.5
p180_pchg_us = plen_base*1.6
p180_pchg_refill_us = plen_base*1.6*5
p180_us = 5
p180_dchg_us = p90_dchg_us
p180_dtcl = 0.5
echoshift_us = 6
echotime_us = 200
scanspacing_us = 10000
samples_per_echo = 1024
echoes_per_scan = 128
n_iterate = 1 # unused for current cpmg code
p90_ph_sel = 1 # set this to 0 for phase 0, 1 for phase 90, 2 for phase 180, 3 for phase 270.
dconv_fact = 1 # unused for current cpmg code
echoskip = 1 # unused for current cpmg code
echodrop = 0 # unused for current cpmg code
vvarac = -2.7
# precharging the vpc
lcs_vpc_pchg_us = 50
lcs_recycledump_us = 1000
lcs_vpc_pchg_repeat = 70
# discharging the vpc
lcs_vpc_dchg_us = 10
lcs_wastedump_us = 200
lcs_vpc_dchg_repeat = 250

# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )

if ( meas_time ):
    elapsed_time = time.time() - start_time
    print( "set parameter time: %.3f" % ( elapsed_time ) )
    start_time = time.time()

# run cpmg sequence
nmrObj.cpmg_t2(
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
    p180_ph_sel,
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
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, nmrObj.client_data_folder, "data.txt" )
    plot_echosum( nmrObj, nmrObj.client_data_folder + "\\" + "data.txt", samples_per_echo, echoes_per_scan, en_fig )
    
    

if ( meas_time ):
    elapsed_time = time.time() - start_time
    print( "data processing time: %.3f" % ( elapsed_time ) )
    start_time = time.time()
