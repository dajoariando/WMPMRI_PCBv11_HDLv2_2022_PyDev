'''
Created on Jan 25, 2025
@author: David Ariando
This script tests the transmitter for:
1. charging coil via left halfbridge and discharge the current into the vpc
2. charging coil via right halfbridge and discharge the current into the vpc
3. discharge vpc to charge the coil and dump
Probe the voltage at the vpc and also current at lcs.
'''

#!/usr/bin/python

# import pydevd
import matplotlib.pyplot as plt
from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.ntwrk_functions import cp_rmt_file, cp_rmt_folder, exec_rmt_ssh_cmd_in_datadir

# instantiate nmr object
client_data_folder = "D:\\NMR_DATA"
nmrObj = nmr_system_2022( client_data_folder )

# parameters
f_larmor = 5.0 # in MHz
bstrap_pchg_us = 2000 # bootstrap precharging (turning on both of the low-side halfbridge, the bootstrap FET for vpc charging, and the bootstrap for the vpc discharging.
# charging
lcs_vpc_pchg_us = 20 # lcs charging via 12V source
lcs_recycledump_us = 100 # lcs dump to vpc
lcs_vpc_pchg_repeat = 100 # repetition for the 12V charging and dump to vpc
# discharging
lcs_vpc_dchg_us = 10 # lcs charging via vpc
lcs_wastedump_us = 100 # lcs dump to waste (via zener power diode)
lcs_vpc_dchg_repeat = 40 # repetition for the VPC charging and dump to waste
# enable or disable
en_lcs_pchg = 0 # enable lcs charging via 12V source
en_lcs_dchg = 1 # enable vpc discharging


# execute
nmrObj.testbench( f_larmor, bstrap_pchg_us, lcs_vpc_pchg_us, lcs_recycledump_us, lcs_vpc_pchg_repeat, lcs_vpc_dchg_us, lcs_wastedump_us, lcs_vpc_dchg_repeat, en_lcs_pchg, en_lcs_dchg)

# clean up
nmrObj.exit()