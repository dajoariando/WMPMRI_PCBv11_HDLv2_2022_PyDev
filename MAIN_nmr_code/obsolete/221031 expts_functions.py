import os

from nmr_std_function.ntwrk_functions import cp_rmt_file, exec_rmt_ssh_cmd_in_datadir, init_ntwrk
from nmr_std_function.nmr_functions import compute_multiexp

# basic phase encoding experiments
def phenc (nmrObj, phenc_conf, sav_fig, show_fig):
    # measurement parameters
    expt_num = 0 # experiment number is always 0 for a single experiment
    
    # run the measurement
    nmrObj.phenc_t2_iter(phenc_conf, expt_num)
    
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder and delete remote files
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "dsum_%06d.txt" % expt_num )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu_%06d.par" % expt_num )
    exec_rmt_ssh_cmd_in_datadir ( nmrObj.ssh, "rm dsum_%06d.txt acqu_%06d.par" % (expt_num, expt_num), nmrObj.server_data_folder )
    # post-processing
    #_, asum_re, asum_im, a0, snr, T2, noise, res, theta, _, _, _ = compute_multiple( nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    _, asum_re, asum_im, a0, snr, T2, noise, res, theta, _, echo_avg, _ = compute_multiexp( nmrObj, phenc_conf, expt_num, sav_fig, show_fig)

    return asum_re, asum_im, a0, snr, T2, noise, res, theta, echo_avg

# phase encoding experiment with both x-y p180 to get real (CPMG) and imaginary (CP) data to construct an image
def phenc_ReIm ( nmrObj, phenc_conf, expt_num ):
    
    # post-processing parameters
    phenc_conf.en_ext_rotation = 1 # enable external reference for echo rotation
    phenc_conf.thetaref = phenc_conf.thetaref # external parameter: echo rotation angle
    phenc_conf.en_conj_matchfilter = 0 # disable conjugate matchfiltering because it will auto-rotate the data
    phenc_conf.en_ext_matchfilter = 0 # enable external reference for matched filtering
    phenc_conf.echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
    sav_fig = 0 # disable figure save
    show_fig = 0 # disable figure show
    
    ### run measurement for the Real part
    phenc_conf.p180_xy_angle = 2 # set 1 for x-pulse and 2 for y-pulse for p180
    # run the experiment
    nmrObj.phenc_t2_iter(phenc_conf, expt_num)
    # create folder for this measurement
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder and delete remote files
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "dsum_%06d.txt" % expt_num  )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu_%06d.par" % expt_num )
    exec_rmt_ssh_cmd_in_datadir ( nmrObj.ssh, "rm dsum_%06d.txt acqu_%06d.par" % (expt_num, expt_num), nmrObj.server_data_folder )
    # post-processing
    _, Y_asum_re, Y_asum_im, Y_a0, Y_snr, Y_T2, Y_noise, Y_res, Y_theta, _, _, _ = compute_multiple( nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
        
    
    #### run measurement for the Imaginary part
    phenc_conf.p180_xy_angle = 1 # set 1 for x-pulse and 2 for y-pulse for p180
    # run the experiment
    nmrObj.phenc_t2_iter(phenc_conf, expt_num+1) 
    # create folder for this measurement
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder and delete the remote files
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "dsum_%06d.txt" % (expt_num+1)  )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu_%06d.par" % (expt_num+1) )
    exec_rmt_ssh_cmd_in_datadir ( nmrObj.ssh, "rm dsum_%06d.txt acqu_%06d.par" % (expt_num+1, expt_num+1), nmrObj.server_data_folder )
    # post-processing
    _, X_asum_re, X_asum_im, X_a0, X_snr, X_T2, X_noise, X_res, X_theta, _, _, _ = compute_multiple( nmrObj, phenc_conf, expt_num+1, sav_fig, show_fig)
    
    # combine the real and imaginary data
    asum_cmplx = Y_asum_re + 1j*X_asum_im
    
    return asum_cmplx

# phase encoding experiment with both x-y p180 to get real (CPMG) and imaginary (CP) data to construct an image. With multithreading
# the object being used is nmrObj for scp and ssh, with its issues when trying to do multithreading.
def compute_phenc_ReIm__mthread ( nmrObj, phenc_conf, expt_num, x, y, kspace, kspace_a0 ):
    # post-processing parameters
    sav_fig = 0 # disable figure save
    show_fig = 0 # disable figure show    
    
    # create folder for this measurement
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder and delete remote files
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "dsum_%06d.txt" % expt_num  )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu_%06d.par" % expt_num )
    exec_rmt_ssh_cmd_in_datadir ( nmrObj.ssh, "rm dsum_%06d.txt acqu_%06d.par" % (expt_num, expt_num), nmrObj.server_data_folder )
    # post-processing
    #_, Y_asum_re, Y_asum_im, Y_a0, Y_snr, Y_T2, Y_noise, Y_res, Y_theta, _, _, _ = compute_multiple( nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    _, Y_asum_re, Y_asum_im, Y_a0, Y_snr, Y_T2, Y_noise, Y_res, Y_theta, _, _, _ = compute_multiexp( nmrObj, phenc_conf, expt_num, sav_fig, show_fig)
    # delete the data to save space
    os.remove(indv_datadir+"\\dsum_%06d.txt" % expt_num)
    os.remove(indv_datadir+"\\acqu_%06d.par" % expt_num)
        
    # create folder for this measurement
    indv_datadir = nmrObj.client_data_folder + nmrObj.folder_extension
    if not os.path.exists(indv_datadir):
        os.makedirs(indv_datadir)
    # transfer the data to local folder and delete the remote files
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "dsum_%06d.txt" % (expt_num+1)  )
    cp_rmt_file( nmrObj.scp, nmrObj.server_data_folder, indv_datadir, "acqu_%06d.par" % (expt_num+1) )
    exec_rmt_ssh_cmd_in_datadir ( nmrObj.ssh, "rm dsum_%06d.txt acqu_%06d.par" % (expt_num+1, expt_num+1), nmrObj.server_data_folder )
    # post-processing
    # _, X_asum_re, X_asum_im, X_a0, X_snr, X_T2, X_noise, X_res, X_theta, _, _, _ = compute_multiple( nmrObj, phenc_conf, expt_num+1, sav_fig, show_fig)
    _, X_asum_re, X_asum_im, X_a0, X_snr, X_T2, X_noise, X_res, X_theta, _, _, _ = compute_multiexp( nmrObj, phenc_conf, expt_num+1, sav_fig, show_fig)
    # delete the data to save space
    os.remove(indv_datadir+"\\dsum_%06d.txt" % (expt_num+1))
    os.remove(indv_datadir+"\\acqu_%06d.par" % (expt_num+1))
    
    # combine the real and imaginary data
    kspace[x,y] = Y_asum_re + 1j*X_asum_im
    for i in range(0,len(Y_a0)): # process for multi-exponential at a0
        kspace_a0[x,y,i] = Y_a0[i]+1j*X_a0[i]