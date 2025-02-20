class scan_config():
# this configuration is for:
# halbach8 v03 that contains 30 turns rx solenoid coil, 2 turn gradient coils for x and z, 4 turns tx coil

    # pulse parameters
    plen_base = 2.0 # 4.40 # the precharging length base. Don't forget to set the corresponding p90_us
    refill_mult = 0.2 # the refill multiplication to compensate RF loss
    p180_p90_amp_fact = 1.0 # 2.0 # multiplication factor between p90 to p180 length
    p180_p90_len_fact = 1.6 # 
    non_stdy_state_mult = 2.0 # if the current still ramps up during Tx (no steady-state), the usual 1.0 factor for p180_dchg_us won't be enough. This causes the current to leak through to rx and perturbs it. To make sure this does not happen, prolong the discharge time after Tx pulse.
    
    
    # cpmg settings
    cpmg_freq = 8.995 # 9.035 # 4.355 # 4.158 # 4.164 # in MHz
    bstrap_pchg_us = 2000
    lcs_pchg_us = 20
    lcs_dump_us = 100
    p90_pchg_us = plen_base
    p90_pchg_refill_us = plen_base*refill_mult
    p90_us = 20.00 # 8.00
    p90_dchg_us = p90_pchg_us+p90_pchg_refill_us # used to be 150
    p90_dtcl = 0.5
    p180_pchg_us = plen_base *p180_p90_amp_fact
    p180_pchg_refill_us = plen_base*refill_mult*p180_p90_amp_fact
    p180_us = p90_us*p180_p90_len_fact
    p180_dchg_us = (p180_pchg_us+p180_pchg_refill_us)*non_stdy_state_mult # used to be p90_dchg_us
    p180_dtcl = p90_dtcl
    echoshift_us = 15
    echotime_us = 500 # 400 or 70
    scanspacing_us = 400000 # normally 100000 for doped water
    samples_per_echo = 2000 # 1000, 600, 200, 100
    echoes_per_scan = 250 # 280 for water, 400 for oil
    n_iterate =  1
    ph_cycl_en = 1 # phase cycle enable
    dconv_fact = 1 # unused for current cpmg code
    echoskip = 1 # unused for current cpmg code
    echodrop = 0 # unused for current cpmg code
    vvarac = -0.37 # -1.87 # set to -1.91V # more negative, more capacitance
    # precharging the vpc (done prior to the cpmg, to bump the vpc to high-voltage, typically 75V)
    lcs_vpc_pchg_us = 25
    lcs_recycledump_us = 1000
    lcs_vpc_pchg_repeat = 300
    # discharging the vpc (done after the cpmg, to dump the high-voltage on vpc to low voltage, typically just the vdd 12V)
    lcs_vpc_dchg_us = 10 # normal: 10
    lcs_wastedump_us = 200 # normal: 200 --- terbakar dengan 2000
    lcs_vpc_dchg_repeat = 2000 # normal: 2000
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
    # lcs charging enable
    # this parameter is provided to add current-mode scheme, where the lcs is not discharged prior
    # to cpmg, thus enabling ultra-short echotime. However, the current in lcs has to be managed
    # by modifying the precharging length to a specific value such that prior to cpmg, the lcs
    # current is constant.
    en_lcs_pchg = 1 # enable lcs precharging (precharge lcs prior to cpmg)
    en_lcs_dchg = 1 # enable lcs discharging (discharge lcs post cpmg)
    # add dummy scan before measurement to mitigate inconsistent signal for first scan
    dummy_scan_num = 0 # the dummy_scan_num added dummy scans at before measurement scans in order to have consistent measurement (same T1) across all scans
    
    # post-processing parameters
    sel_adc_ch = 1 # select the adc channel # for NMR to be processed. Input 0 to 7
    dconv_f = 0 # in MHz. when set to 0, the downconversion local oscillator is set to be B1 freq. When set the other value, the downconversion losc is just the set value.
    dconv_lpf_ord = 2  # downconversion order
    dconv_lpf_cutoff_kHz = 200  # downconversion lpf cutoff
    en_ext_rotation = 0 # enable external reference for echo rotation
    thetaref = 0 # external parameter: echo rotation angle
    en_ext_matchfilter = 0 # enable external reference for matched filtering
    en_conj_matchfilter = 0 # compute matchfiltering with the conjugate (results in absolute value of signal with no imaginary)
    en_self_rotation = 1 # enable self rotation with the angle estimated by its own echo (is automatically disactivated when en_ext_rotation is active
    echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average 
    ignore_echoes = 6 # ignore initial echoes for data processing
    # dual_exp = 0 # enable dual exponential fit. Otherwise, it will be single exponential fit
    # a_est = [30,100] # amplitude estimation for fitting
    # t2_est = [10e-3,200e-3] # t2 estimate for fitting
    a_est = [100,10] # array of amplitude estimate for fitting
    t2_est = [200e-3,20e-3] # array of t2 estimate for fitting
    a_bnd = [0,200] # the bound is global for all a_est
    t2_bnd = [1e-3,500e-3] # the bound is global for all t2_est
    en_fit = True

    en_spect_ref = 0 # set spectrum reference compensation
    spect_ref = 0 # the reference for spectrum