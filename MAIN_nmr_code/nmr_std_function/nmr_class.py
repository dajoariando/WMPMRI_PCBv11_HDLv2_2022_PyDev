'''
Created on Nov 06, 2018

@author: David Ariando
'''

#!/usr/bin/python

from datetime import datetime
import os
import shutil

import pydevd

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
        self.server_ip = '192.168.137.2'  # '129.22.143.88'
        self.client_ip = '192.168.137.1'  # '129.22.143.39'
        self.server_path = '/root/NMR_PCBv11_HDLv2_2022_PyDev/MAIN_nmr_code'
        # client path with samba
        self.client_path = 'W:\\NMR_PCBv11_HDLv2_2022_PyDev\\MAIN_nmr_code'
        self.ssh_usr = 'root'
        self.ssh_passwd = 'dave'
        # data folder
        self.server_data_folder = "/root/NMR_DATA"
        self.client_data_folder = client_data_folder
        self.exec_folder = "c_exec"

        # configure the network
        self.ssh, self.scp = init_ntwrk ( self.server_ip, self.ssh_usr, self.ssh_passwd )

    def exit( self ):
        exit_ntwrk ( self.ssh, self.scp )

    def cpmg_t2( self, cpmg_freq,
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
    ):
        # execute cpmg sequence
        exec_name = "cpmg_t2"

        command = ( exec_name + " " +
                   str( cpmg_freq ) + " " +
                   str( bstrap_pchg_us ) + " " +
                   str( lcs_pchg_us ) + " " +
                   str( lcs_dump_us ) + " " +
                   str( p90_pchg_us ) + " " +
                   str( p90_pchg_refill_us ) + " " +
                   str( p90_us ) + " " +
                   str( p90_dchg_us ) + " " +
                   str( p90_dtcl ) + " " +
                   str( p180_pchg_us ) + " " +
                   str( p180_pchg_refill_us ) + " " +
                   str( p180_us ) + " " +
                   str( p180_dchg_us ) + " " +
                   str( p180_dtcl ) + " " +
                   str( echoshift_us ) + " " +
                   str( echotime_us ) + " " +
                   str( scanspacing_us ) + " " +
                   str( samples_per_echo ) + " " +
                   str( echoes_per_scan ) + " " +
                   str( n_iterate ) + " " +
                   str( p180_ph_sel ) + " " +
                   str( dconv_fact ) + " " +
                   str( echoskip ) + " " +
                   str( echodrop ) + " " +
                   str( vvarac ) + " " +
                   str( lcs_vpc_pchg_us ) + " " +
                   str( lcs_recycledump_us ) + " " +
                   str( lcs_vpc_pchg_repeat ) + " " +
                   str( lcs_vpc_dchg_us ) + " " +
                   str( lcs_wastedump_us ) + " " +
                   str( lcs_vpc_dchg_repeat )
                   )

        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )

    def cpmg_t2_iter( self, cpmg_freq,
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
    ):
        # execute cpmg sequence
        exec_name = "cpmg_t2_iter"

        command = ( exec_name + " " +
                   str( cpmg_freq ) + " " +
                   str( bstrap_pchg_us ) + " " +
                   str( lcs_pchg_us ) + " " +
                   str( lcs_dump_us ) + " " +
                   str( p90_pchg_us ) + " " +
                   str( p90_pchg_refill_us ) + " " +
                   str( p90_us ) + " " +
                   str( p90_dchg_us ) + " " +
                   str( p90_dtcl ) + " " +
                   str( p180_pchg_us ) + " " +
                   str( p180_pchg_refill_us ) + " " +
                   str( p180_us ) + " " +
                   str( p180_dchg_us ) + " " +
                   str( p180_dtcl ) + " " +
                   str( echoshift_us ) + " " +
                   str( echotime_us ) + " " +
                   str( scanspacing_us ) + " " +
                   str( samples_per_echo ) + " " +
                   str( echoes_per_scan ) + " " +
                   str( n_iterate ) + " " +
                   str( p180_ph_sel ) + " " +
                   str( dconv_fact ) + " " +
                   str( echoskip ) + " " +
                   str( echodrop ) + " " +
                   str( vvarac ) + " " +
                   str( lcs_vpc_pchg_us ) + " " +
                   str( lcs_recycledump_us ) + " " +
                   str( lcs_vpc_pchg_repeat ) + " " +
                   str( lcs_vpc_dchg_us ) + " " +
                   str( lcs_wastedump_us ) + " " +
                   str( lcs_vpc_dchg_repeat )
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )
    
    def phenc_t2_iter( self,
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
        lcs_vpc_dchg_repeat,
        gradz_len_us,
        gradz_volt,
        gradx_len_us,
        gradx_volt,
        grad_refocus,
        flip_grad_refocus_sign,
        enc_tao_us,
        p180_xy_angle,
        en_lcs_pchg,
        en_lcs_dchg
    ):
        # execute cpmg sequence
        exec_name = "phenc_t2_iter"

        command = ( exec_name + " " +
                   str( cpmg_freq ) + " " +
                   str( bstrap_pchg_us ) + " " +
                   str( lcs_pchg_us ) + " " +
                   str( lcs_dump_us ) + " " +
                   str( p90_pchg_us ) + " " +
                   str( p90_pchg_refill_us ) + " " +
                   str( p90_us ) + " " +
                   str( p90_dchg_us ) + " " +
                   str( p90_dtcl ) + " " +
                   str( p180_pchg_us ) + " " +
                   str( p180_pchg_refill_us ) + " " +
                   str( p180_us ) + " " +
                   str( p180_dchg_us ) + " " +
                   str( p180_dtcl ) + " " +
                   str( echoshift_us ) + " " +
                   str( echotime_us ) + " " +
                   str( scanspacing_us ) + " " +
                   str( samples_per_echo ) + " " +
                   str( echoes_per_scan ) + " " +
                   str( n_iterate ) + " " +
                   str( p180_ph_sel ) + " " +
                   str( dconv_fact ) + " " +
                   str( echoskip ) + " " +
                   str( echodrop ) + " " +
                   str( vvarac ) + " " +
                   str( lcs_vpc_pchg_us ) + " " +
                   str( lcs_recycledump_us ) + " " +
                   str( lcs_vpc_pchg_repeat ) + " " +
                   str( lcs_vpc_dchg_us ) + " " +
                   str( lcs_wastedump_us ) + " " +
                   str( lcs_vpc_dchg_repeat ) + " " +
                   
                   str( gradz_len_us ) + " " +
                   str( gradz_volt ) + " " +
                   
                   str( gradx_len_us ) + " " +
                   str( gradx_volt ) + " " +
                   
                   str(grad_refocus) + " " +
                   str(flip_grad_refocus_sign) + " " +
                   
                   str( enc_tao_us ) + " " +
                   
                   str(p180_xy_angle) + " " +
                   
                   str(en_lcs_pchg) + " " +
                   str(en_lcs_dchg)
                   
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )
     
    def noise( self, f_adc, samples, vvarac ):
        # execute cpmg sequence
        exec_name = "noise"

        command = ( exec_name + " " +
                   str( f_adc ) + " " +
                   str( samples ) + " " +
                   str (vvarac)
                   )
    
        ssh_cmd = self.server_path +'/'+ self.exec_folder +'/'+ command
        exec_rmt_ssh_cmd_in_datadir( self.ssh, ssh_cmd, self.server_data_folder )