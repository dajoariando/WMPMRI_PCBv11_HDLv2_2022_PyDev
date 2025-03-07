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
front_porch_us = 2000 # blanking before pulse in us
grad_len_us = 4000 # gradient length in us
grad_blanking_us = 4000 # gradient in-between blanking in us
back_tail_us = 2000 # blanking after pulse, in us
voltx_A = 2.51
voltx_B = 2.482+0.02
voltx_C = 2.5
voltx_D = 2.491+0.02

a = 0.2

volty_A = 2.51
volty_B = 2.51
volty_C = 2.503
volty_D = 2.503
grad_refocus = 0 # gradient refocus (second gradient pulse)
flip_grad_refocus_sign = 1 # flip the refocus sign
gradx_dir = 1
grady_dir = 1

# execute
nmrObj.tb_grad_voltage(SYSCLK_MHz, bstrap_pchg_us, front_porch_us, grad_len_us, grad_blanking_us, back_tail_us, voltx_A, voltx_B, voltx_C, voltx_D, volty_A, volty_B, volty_C, volty_D, grad_refocus, flip_grad_refocus_sign, gradx_dir, grady_dir)


# clean up
nmrObj.exit()