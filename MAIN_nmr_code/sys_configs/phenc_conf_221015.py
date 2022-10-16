class phenc_conf_221015():
# this configuration is for:
# halbach8 v02 that contains 30 turns rx solenoid coil, 1 turn gradient coils for x and z, 5 turns tx coil

    # pulse parameters
    plen_base = 5.00 # the precharging length base
    refill_mult = 0.8 # the refill multiplication to compensate RF loss
    p180_p90_fact = 1.6 # multiplication factor between p90 to p180 length
    
    # cpmg settings
    cpmg_freq = 4.1
    bstrap_pchg_us = 2000
    lcs_pchg_us = 20
    lcs_dump_us = 100
    p90_pchg_us = plen_base
    p90_pchg_refill_us = plen_base*refill_mult
    p90_us = 10.0
    p90_dchg_us = 100
    p90_dtcl = 0.5
    p180_pchg_us = plen_base *p180_p90_fact
    p180_pchg_refill_us = plen_base*refill_mult*p180_p90_fact
    p180_us = p90_us
    p180_dchg_us = p90_dchg_us
    p180_dtcl = p90_dtcl
    echoshift_us = 10
    echotime_us = 500
    scanspacing_us = 200000
    samples_per_echo = 4000
    echoes_per_scan = 80
    n_iterate = 2
    ph_cycl_en = 1 # phase cycle enable
    dconv_fact = 1 # unused for current cpmg code
    echoskip = 1 # unused for current cpmg code
    echodrop = 0 # unused for current cpmg code
    vvarac = -1.91 # set to -1.91V # more negative, more capacitance
    # precharging the vpc
    lcs_vpc_pchg_us = 25
    lcs_recycledump_us = 1000
    lcs_vpc_pchg_repeat = 210
    # discharging the vpc
    lcs_vpc_dchg_us = 5
    lcs_wastedump_us = 200
    lcs_vpc_dchg_repeat = 2000
    # gradient params
    gradz_len_us = 800 # gradient pulse length
    gradz_volt = 0.1 # the gradient can be positive or negative
    gradx_len_us = 800 # gradient pulse length
    gradx_volt = 0.1 # the gradient can be positive or negative
    grad_refocus = 1 # put 1 to refocus the gradient
    flip_grad_refocus_sign = 1 # put 1 to flip the gradient refocusing sign
    enc_tao_us = 1000 # the encoding time
    # p180 x-y pulse selection. 
    p180_xy_angle = 2 # set 1 for x-pulse and 2 for y-pulse for p180
    # lcs charging param
    en_lcs_pchg = 1 # enable lcs precharging
    en_lcs_dchg = 1 # enable lcs discharging
    
    # post-processing parameters
    dconv_lpf_ord = 2  # downconversion order
    dconv_lpf_cutoff_kHz = 200  # downconversion lpf cutoff
    en_ext_rotation = 0 # enable external reference for echo rotation
    thetaref = 0 # external parameter: echo rotation angle
    en_conj_matchfilter = 0 # compute matchfiltering with the conjugate (results in absolute value of signal with no imaginary)
    en_ext_matchfilter = 0 # enable external reference for matched filtering
    echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average 
    ignore_echoes = 0 # ignore initial echoes for data processing