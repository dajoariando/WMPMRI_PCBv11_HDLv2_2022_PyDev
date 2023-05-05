class phenc_conf_halbach_v03_230405_biosample():
# this configuration is for:
# halbach8 v03 that contains 30 turns rx solenoid coil, 2 turn gradient coils for x and z, 4 turns tx coil

    # pulse parameters
    plen_base = 4.60 # 8.00, 4.40, 2.00, 1.00 # the precharging length base. Don't forget to set the corresponding p90_us
    refill_mult = 0.8 # the refill multiplication to compensate RF loss
    p180_p90_fact = 2.0 # multiplication factor between p90 to p180 length
    
    # cpmg settings
    cpmg_freq = 4.164 # 4.157 # in MHz
    bstrap_pchg_us = 2000
    lcs_pchg_us = 20
    lcs_dump_us = 100
    p90_pchg_us = plen_base
    p90_pchg_refill_us = plen_base*refill_mult
    p90_us = 7.0 # 6.00, 10.00, 18.00, 24.00
    p90_dchg_us = p90_pchg_us+p90_pchg_refill_us # used to be 150
    p90_dtcl = 0.5
    p180_pchg_us = plen_base *p180_p90_fact
    p180_pchg_refill_us = plen_base*refill_mult*p180_p90_fact
    p180_us = p90_us
    p180_dchg_us = p180_pchg_us+p180_pchg_refill_us # used to be p90_dchg_us
    p180_dtcl = p90_dtcl
    echoshift_us = 7
    echotime_us = 70 # 140 or 70
    scanspacing_us = 100000 # normally 100000 for doped water
    samples_per_echo = 400 # 1200 or 400
    echoes_per_scan = 900 # 400 or 900
    n_iterate =  2 # do not change it here for
    ph_cycl_en = 1 # phase cycle enable
    dconv_fact = 1 # unused for current cpmg code
    echoskip = 1 # unused for current cpmg code
    echodrop = 0 # unused for current cpmg code
    vvarac = -1.83 # -1.87 # set to -1.91V # more negative, more capacitance
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
    gradz_volt = 0.1 # the gradient can be positive or negative
    gradx_len_us = 100 # gradient pulse length
    gradx_volt = 0.1 # the gradient can be positive or negative
    grad_refocus = 1 # put 1 to refocus the gradient
    flip_grad_refocus_sign = 1 # put 1 to flip the gradient refocusing sign
    enc_tao_us = 200 # the encoding time
    # p180 x-y pulse selection. 
    p180_xy_angle = 2 # set 1 for x-pulse and 2 for y-pulse for p180
    # lcs charging param
    en_lcs_pchg = 1 # enable lcs precharging
    en_lcs_dchg = 1 # enable lcs discharging
    # add dummy scan before measurement to mitigate inconsistent signal for first scan
    dummy_scan_num = 0 # the dummy_scan_num added dummy scans at before measurement scans in order to have consistent measurement (same T1) across all scans
    
    # post-processing parameters
    dconv_f = 0 # in MHz. when set to 0, the downconversion local oscillator is set to be B1 freq. When set the other value, the downconversion losc is just the set value.
    dconv_lpf_ord = 2  # downconversion order
    dconv_lpf_cutoff_kHz = 100  # downconversion lpf cutoff
    en_ext_rotation = 0 # enable external reference for echo rotation
    thetaref = 0 # external parameter: echo rotation angle
    en_ext_matchfilter = 0 # enable external reference for matched filtering
    en_conj_matchfilter = 0 # compute matchfiltering with the conjugate (results in absolute value of signal with no imaginary)
    en_self_rotation = 1 # enable self rotation with the angle estimated by its own echo (is automatically disactivated when en_ext_rotation is active
    echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average 
    ignore_echoes = 0 # ignore initial echoes for data processing
    # dual_exp = 0 # enable dual exponential fit. Otherwise, it will be single exponential fit
    # a_est = [30,100] # amplitude estimation for fitting
    # t2_est = [10e-3,200e-3] # t2 estimate for fitting
    a_est = [20, 20] # array of amplitude estimate for fitting
    t2_est = [10e-3, 40e-3] # array of t2 estimate for fitting
    en_fit = False
    
