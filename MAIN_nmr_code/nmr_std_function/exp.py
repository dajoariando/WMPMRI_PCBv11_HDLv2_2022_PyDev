def phenc_ReIm ( nmrObj, phenc_conf ):
    
    # post-processing parameters
    en_ext_rotation = 1 # enable external reference for echo rotation
    thetaref = phenc_conf.thetaref # external parameter: echo rotation angle
    en_conj_matchfilter = 0 # disable conjugate matchfiltering because it will auto-rotate the data
    en_ext_matchfilter = 0 # enable external reference for matched filtering
    echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
    
    
    # run measurement for the Real part
    phenc_conf.p180_xy_angle = 2 # set 1 for x-pulse and 2 for y-pulse for p180
    nmrObj.phenc_t2_iter(phenc_conf)
    # create folder for this measurement
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension + '_Y'
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
    # post-processing
    _, Y_asum_re, Y_asum_im, Y_a0, Y_snr, Y_T2, Y_noise, Y_res, Y_theta, _, _, _ = compute_multiple( nmrObj, sav_fig, show_fig, en_ext_rotation, thetaref, en_conj_matchfilter, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
        
    
    # run measurement for the Imaginary part
    phenc_conf.p180_xy_angle = 1 # set 1 for x-pulse and 2 for y-pulse for p180
    nmrObj.phenc_t2_iter(phenc_conf)
    # create folder for this measurement
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension + '_X'
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
    # post-processing
    _, X_asum_re, X_asum_im, X_a0, X_snr, X_T2, X_noise, X_res, X_theta, _, _, _ = compute_multiple( nmrObj, sav_fig, show_fig, en_ext_rotation, thetaref, en_conj_matchfilter, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )

    
    # combine the real and imaginary data
    asum_cmplx = Y_asum_re + 1j*X_asum_im
    
    return asum_cmplx

def phenc (nmrObj, phenc_conf):
    # run the measurement
    nmrObj.phenc_t2_iter(phenc_conf)
    
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "datasum.txt" )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu.par" )
    # post-processing
    _, asum_re, asum_im, a0, snr, T2, noise, res, theta, _, _, _ = compute_multiple( nmrObj, sav_fig, show_fig, en_ext_rotation, thetaref, en_conj_matchfilter, en_ext_matchfilter, echoref_avg, dconv_lpf_ord, dconv_lpf_cutoff_kHz, ignore_echoes )
        
    return asum_re, asum_im, a0, snr, T2, noise, res, theta