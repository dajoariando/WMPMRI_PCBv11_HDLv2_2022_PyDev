'''
Created on Nov 06, 2018

@author: David Ariando
'''

#!/usr/bin/python

from datetime import datetime
import os
import shutil

# import pydevd

from nmr_std_function.ntwrk_functions import exec_rmt_ssh_cmd_in_datadir, init_ntwrk, exit_ntwrk
import numpy as np


# from email.errors import ObsoleteHeaderDefect
class nmr_system_2022:

    def __init__( self, client_data_folder ):

        # Numeric conversion of the hardware
        self.pamp_gain_dB = 60  # preamp gain
        self.rx_gain_dB = 20  # rx amp gain
        self.totGain = 10 ** ( ( self.pamp_gain_dB + self.rx_gain_dB ) / 20 )
        self.uvoltPerDigit = 2.0 * ( 10 ** 6 ) / 4096  # ADC conversion, in microvolt
        self.fir_gain = 21513  # downconversion FIR filter gain (sum of all coefficients)
        self.dconv_gain = 0.707106781  # downconversion gain factor due to sine(45,135,225,315) multiplication

        # ip addresses settings for the system
        self.server_ip = '192.168.14.204'  # '129.22.143.88'
        self.client_ip = '192.168.14.105'  # '129.22.143.39'
        self.server_path = '/root'
        # client path with samba
        self.client_path = 'W:\\'
        self.ssh_usr = 'root'
        self.ssh_passwd = 'dave'
        # data folder
        self.server_data_folder = "/root/NMR_DATA"
        self.client_data_folder = client_data_folder
        self.folder_extension = "" # folder extension for the measurement
        self.exec_folder = "c_exec"

        # configure the network
        self.ssh, self.scp = init_ntwrk ( self.server_ip, self.ssh_usr, self.ssh_passwd )
        
        # create folder for measurements
        if not os.path.exists(self.client_data_folder):
            os.makedirs(self.client_data_folder)

    def exit( self ):
        exit_ntwrk ( self.ssh, self.scp )

    def cpmg_t2_iter( self, cpmg_conf, expt_num ):
        # execute cpmg sequence
        exec_name = "cpmg"

        command = ( exec_name + " " +
                   str( cpmg_conf.cpmg_freq ) + " " +
                   str( cpmg_conf.bstrap_pchg_us ) + " " +
                   str( cpmg_conf.lcs_pchg_us ) + " " +
                   str( cpmg_conf.lcs_dump_us ) + " " +
                   str( cpmg_conf.p90_pchg_us ) + " " +
                   str( cpmg_conf.p90_pchg_refill_us ) + " " +
                   str( cpmg_conf.p90_us ) + " " +
                   str( cpmg_conf.p90_dchg_us ) + " " +
                   str( cpmg_conf.p90_dtcl ) + " " +
                   str( cpmg_conf.p180_pchg_us ) + " " +
                   str( cpmg_conf.p180_pchg_refill_us ) + " " +
                   str( cpmg_conf.p180_us ) + " " +
                   str( cpmg_conf.p180_dchg_us ) + " " +
                   str( cpmg_conf.p180_dtcl ) + " " +
                   str( cpmg_conf.echoshift_us ) + " " +
                   str( cpmg_conf.echotime_us ) + " " +
                   str( cpmg_conf.scanspacing_us ) + " " +
                   str( cpmg_conf.samples_per_echo ) + " " +
                   str( cpmg_conf.echoes_per_scan ) + " " +
                   str( cpmg_conf.n_iterate ) + " " +
                   str( cpmg_conf.ph_cycl_en ) + " " +
                   str( cpmg_conf.dconv_fact ) + " " +
                   str( cpmg_conf.echoskip ) + " " +
                   str( cpmg_conf.echodrop ) + " " +
                   str( cpmg_conf.vvarac ) + " " +
                   str( cpmg_conf.lcs_vpc_pchg_us ) + " " +
                   str( cpmg_conf.lcs_recycledump_us ) + " " +
                   str( cpmg_conf.lcs_vpc_pchg_repeat ) + " " +
                   str( cpmg_conf.lcs_vpc_dchg_us ) + " " +
                   str( cpmg_conf.lcs_wastedump_us ) + " " +
                   str( cpmg_conf.lcs_vpc_dchg_repeat ) + " " +
                   str( cpmg_conf.gradz_volt ) + " " +
                   str( cpmg_conf.gradx_volt ) + " " +
                   str( cpmg_conf.en_lcs_pchg ) + " " +
                   str( cpmg_conf.en_lcs_dchg ) + " " +
                   str( expt_num ) + " " +
                   str( cpmg_conf.dummy_scan_num )
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )
        
    def cpmg_cmode_t2_iter( self, cpmg_conf, expt_num ):
        # execute cpmg sequence
        exec_name = "cpmg_cmode"

        command = ( exec_name + " " +
                   str( cpmg_conf.cpmg_freq ) + " " +
                   str( cpmg_conf.bstrap_pchg_us ) + " " +
                   str( cpmg_conf.lcs_pchg_us ) + " " +
                   str( cpmg_conf.lcs_dump_us ) + " " +
                   str( cpmg_conf.p90_pchg_us ) + " " +
                   str( cpmg_conf.p90_us ) + " " +
                   str( cpmg_conf.p90_dchg_us ) + " " +
                   str( cpmg_conf.p90_dtcl ) + " " +
                   str( cpmg_conf.p180_1st_pchg_us ) + " " +
                   str( cpmg_conf.p180_pchg_us ) + " " +
                   str( cpmg_conf.p180_us ) + " " +
                   str( cpmg_conf.p180_dchg_us ) + " " +
                   str( cpmg_conf.p180_dtcl ) + " " +
                   str( cpmg_conf.echoshift_us ) + " " +
                   str( cpmg_conf.echotime_us ) + " " +
                   str( cpmg_conf.scanspacing_us ) + " " +
                   str( cpmg_conf.samples_per_echo ) + " " +
                   str( cpmg_conf.echoes_per_scan ) + " " +
                   str( cpmg_conf.n_iterate ) + " " +
                   str( cpmg_conf.ph_cycl_en ) + " " +
                   str( cpmg_conf.dconv_fact ) + " " +
                   str( cpmg_conf.echoskip ) + " " +
                   str( cpmg_conf.echodrop ) + " " +
                   str( cpmg_conf.vvarac ) + " " +
                   str( cpmg_conf.lcs_vpc_pchg_us ) + " " +
                   str( cpmg_conf.lcs_recycledump_us ) + " " +
                   str( cpmg_conf.lcs_vpc_pchg_repeat ) + " " +
                   str( cpmg_conf.lcs_vpc_dchg_us ) + " " +
                   str( cpmg_conf.lcs_wastedump_us ) + " " +
                   str( cpmg_conf.lcs_vpc_dchg_repeat ) + " " +
                   str( cpmg_conf.gradz_volt ) + " " +
                   str( cpmg_conf.gradx_volt ) + " " +
                   str( cpmg_conf.en_lcs_pchg ) + " " +
                   str( cpmg_conf.en_lcs_dchg ) + " " +
                   str( expt_num )
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )
    
    def phenc_t2_iter( self, phenc_conf, expt_num ):
        # execute cpmg sequence
        exec_name = "phenc"

        command = ( exec_name + " " +
                   str( phenc_conf.cpmg_freq ) + " " +
                   str( phenc_conf.bstrap_pchg_us ) + " " +
                   str( phenc_conf.lcs_pchg_us ) + " " +
                   str( phenc_conf.lcs_dump_us ) + " " +
                   str( phenc_conf.p90_pchg_us ) + " " +
                   str( phenc_conf.p90_pchg_refill_us ) + " " +
                   str( phenc_conf.p90_us ) + " " +
                   str( phenc_conf.p90_dchg_us ) + " " +
                   str( phenc_conf.p90_dtcl ) + " " +
                   str( phenc_conf.p180_pchg_us ) + " " +
                   str( phenc_conf.p180_pchg_refill_us ) + " " +
                   str( phenc_conf.p180_us ) + " " +
                   str( phenc_conf.p180_dchg_us ) + " " +
                   str( phenc_conf.p180_dtcl ) + " " +
                   str( phenc_conf.echoshift_us ) + " " +
                   str( phenc_conf.echotime_us ) + " " +
                   str( phenc_conf.scanspacing_us ) + " " +
                   str( phenc_conf.samples_per_echo ) + " " +
                   str( phenc_conf.echoes_per_scan ) + " " +
                   str( phenc_conf.n_iterate ) + " " +
                   str( phenc_conf.ph_cycl_en ) + " " +
                   str( phenc_conf.dconv_fact ) + " " +
                   str( phenc_conf.echoskip ) + " " +
                   str( phenc_conf.echodrop ) + " " +
                   str( phenc_conf.vvarac ) + " " +
                   str( phenc_conf.lcs_vpc_pchg_us ) + " " +
                   str( phenc_conf.lcs_recycledump_us ) + " " +
                   str( phenc_conf.lcs_vpc_pchg_repeat ) + " " +
                   str( phenc_conf.lcs_vpc_dchg_us ) + " " +
                   str( phenc_conf.lcs_wastedump_us ) + " " +
                   str( phenc_conf.lcs_vpc_dchg_repeat ) + " " +
                   
                   str( phenc_conf.gradz_len_us ) + " " +
                   str( phenc_conf.gradz_volt ) + " " +
                   
                   str( phenc_conf.gradx_len_us ) + " " +
                   str( phenc_conf.gradx_volt ) + " " +
                   
                   str( phenc_conf.grad_refocus) + " " +
                   str( phenc_conf.flip_grad_refocus_sign) + " " +
                   
                   str( phenc_conf.enc_tao_us ) + " " +
                   
                   str( phenc_conf.p180_xy_angle ) + " " +
                   
                   str( phenc_conf.en_lcs_pchg ) + " " +
                   str( phenc_conf.en_lcs_dchg ) + " " +
                   str( expt_num ) + " " +
                   str( phenc_conf.dummy_scan_num )
                   
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )
     
    def noise_timeavg( self, f_adc, samples, avg_fact, vvarac ):
        # execute cpmg sequence
        exec_name = "noise_timeavg"

        command = ( exec_name + " " +
                   str( f_adc ) + " " +
                   str( samples ) + " " +
                   str( avg_fact ) + " " +
                   str ( vvarac ) + " " +
                   "0 0 0" # data input mode
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )
        
    def noise( self, f_adc, samples, vvarac ):
        # execute cpmg sequence
        exec_name = "noise"

        command = ( exec_name + " " +
                   str( f_adc ) + " " +
                   str( samples ) + " " +
                   str ( vvarac ) + " " +
                   "0 0 0" # data input mode
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )