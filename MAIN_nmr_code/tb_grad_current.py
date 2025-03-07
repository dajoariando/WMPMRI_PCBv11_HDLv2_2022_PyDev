'''
Created on Feb 24, 2025
@author: David Ariando
This script tests the gradient by generating 2 pulses with a space in between, to verify current waveform & transition
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
SYSCLK_MHz = 20 # in MHz
bstrap_pchg_us = 20000 # gradient highside bootstrap precharging in us
front_porch_us = 500 # blanking before pulse in us
grad_len_us = 1000 # gradient length in us
grad_blanking_us = 500 # gradient in-between blanking in us
back_tail_us = 500 # blanking after pulse, in us
grady_mA = -1000 # gradient current pulse amplitude in mA
gradx_mA = -1500 # gradient current pulse amplitude in mA
ibias_x_A = 0 # bias for x left
ibias_x_C = 0 # bias for x right
ibias_y_A = 0 # bias for y left
ibias_y_C = 0 # bias for y right
grad_refocus = 1 # gradient refocus (second gradient pulse)
flip_grad_refocus_sign = 1 # flip the refocus sign


# execute
nmrObj.tb_grad_current(SYSCLK_MHz, bstrap_pchg_us,front_porch_us,grad_len_us,grad_blanking_us, back_tail_us,grady_mA,gradx_mA,ibias_x_A,ibias_x_C,ibias_y_A,ibias_y_C,grad_refocus,flip_grad_refocus_sign)


# clean up
nmrObj.exit()