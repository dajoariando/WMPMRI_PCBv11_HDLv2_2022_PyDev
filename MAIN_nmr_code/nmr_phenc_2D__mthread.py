'''
Created on Oct 16, 2022
@author: David Ariando
This phase encoding implements multithreading in ethernet data transfer from SoC to local computer in order for the cpmg to run as fast as possible.
However, care must be taken that the ethernet data transfer must be done before another ethernet data transfer from the next cpmg is performed. Otherwise,
multiple threads will try to access the scp/ssh at the same time and causes conflicts. This usually happens when the cpmg is faster than the
ethernet data transfer and the script will call scp/ssh at the same time. To avoid this, just use more iteration factor or more inter-experiment time.
'''

#!/usr/bin/python

import os
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function.data_parser import write_text_overwrite
from nmr_std_function.time_func import time_meas
from nmr_std_function.expts_functions import phenc,phenc_ReIm,compute_phenc_ReIm__mthread
from threading import Thread


# get current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# measurements folder settings
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = 'PHENC_2D_'+datatime

# instantiate nmr object
client_data_folder = data_parent_folder+'\\'+meas_folder
nmrObj = nmr_system_2022( client_data_folder )

def plot_image_and_save (fig_num, nmrObj, kspace, filename):
    
    # invert the kspace to image_asum
    image_asum = np.fft.fftshift(np.fft.fft2(kspace))
    
    # plot the data
    fig = plt.figure(fig_num)
    fig.clf()
    plt.subplot(1,2,1)
    plt.imshow(np.abs(kspace),cmap='gray')
    plt.subplot(1,2,2)
    plt.imshow(np.abs(image_asum),cmap='gray')
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    # save the data
    plt.savefig( nmrObj.client_data_folder + '\\image_%s.png'%filename )
    np.savetxt(nmrObj.client_data_folder+"\\kspace_%s.txt"%filename,kspace,fmt='%0.10f')

# variables
sav_fig = False # save figures
show_fig = False  # show figures
report_time = True  # measure time
process_data = True # process the NMR data
en_multithreads = True # enable multithread processing of the data. Otherwise, it'll be processed sequentially

tmeas = time_meas(report_time)

# import default measurement configuration and modify
from sys_configs.phenc_conf_halbach_v03_221018 import phenc_conf_halbach_v03_221018
phenc_conf = phenc_conf_halbach_v03_221018()

# modify default parameters
phenc_conf.n_iterate = 2
phenc_conf.gradz_len_us = 800 # gradient pulse length
phenc_conf.gradx_len_us = 800 # gradient pulse length
phenc_conf.enc_tao_us = 1000 # the encoding time
        
# set the maximum current and number of pixels 
imax = 3.0 # 3.0 # maximum current (both polarity will be used)
npxl = 64 # 64 # number of pixels inside the image_asum
ilist = np.linspace(-imax, imax, npxl) # create list of current being used
write_text_overwrite( nmrObj.client_data_folder, 'grad_strength.txt', str(ilist))

# modify current list to account for 100mA DC biasing in the gradient circuit
# the current is 0 when it's set to +/- 0.1V, instead of 0V.
for idx,v in enumerate(ilist):
    if v > 0.0001 : # use 0.01 instead of 0.0 to avoid deal with floating point number around 0.0
        ilist[idx] = v+0.1
    elif v<(-0.0001) :
        ilist[idx] = v-0.1
    else :
        ilist[idx] = 0.1 # 0.1V means 0.1A to the transistor but 0.0A to the coil, because the other transistor is biased at 0.1A when it's turned off.

# perform reference scan
print("\n(Reference scan)" )
nmrObj.folder_extension = "\\ref"
phenc_conf.en_lcs_pchg = 1 # enable lcs precharging
phenc_conf.en_lcs_dchg = 0 # enable lcs discharging
sav_fig = 1 # save figure for reference scan
show_fig = 1 # show figure for reference scan
_, _, _, _, _, _, _, theta_ref, echo_avg = phenc (nmrObj, phenc_conf, sav_fig, show_fig)

tmeas.reportTimeSinceLast("############################################################################### load libraries and reference scan")

# create index list with 3 width, 1 for concentric square number (layer number of the concentric square from the middle), 2 and 3 for index of the square
idx_list = np.zeros((3,npxl*npxl),dtype='int')

# create a concentric square pattern from the middle
idx_start = int(np.ceil(npxl/2)) # set the starting index, which is half of index max
if (npxl % 2) == 0: # for even npxl
    idx_tgt = idx_start+1
else: # for odd npxl
    idx_tgt = idx_start

# loop for generating concentric square from the middle
idx_list_n = 0
for i in range(0, idx_start):
    idx = idx_start-i # it should start with idx_start, but python range isn't giving idx_start from range()
    
    for idx_n in range(idx, idx_tgt+1):
        
        idx_list[0,idx_list_n] = i
        idx_list[1,idx_list_n] = idx_n
        idx_list[2,idx_list_n] = idx
        idx_list_n = idx_list_n + 1

    if idx != idx_tgt:        
        for idx_n in range(idx, idx_tgt+1):
            
            idx_list[0,idx_list_n] = i
            idx_list[1,idx_list_n] = idx_n
            idx_list[2,idx_list_n] = idx_tgt
            idx_list_n = idx_list_n + 1
        
    for idx_n in range(idx+1,idx_tgt):
        
        idx_list[0,idx_list_n] = i
        idx_list[1,idx_list_n] = idx
        idx_list[2,idx_list_n] = idx_n
        idx_list_n = idx_list_n + 1
    
    for idx_n in range(idx+1,idx_tgt):
    
        idx_list[0,idx_list_n] = i
        idx_list[1,idx_list_n] = idx_tgt
        idx_list[2,idx_list_n] = idx_n
        idx_list_n = idx_list_n + 1
        
    idx_tgt = idx_tgt + 1
    

for i in range(0,np.size(idx_list,1)):
    if False: # print the index list for viewing purpose
        print(idx_list[:,i])
    # subtract one from all xy indexing due to Python indexing starts with 0, not 1
    idx_list[1,i] -= 1 # subtract x indexing
    idx_list[2,i] -= 1 # subtract y indexing

n_exp = len(phenc_conf.a_est) # get the exponential #

# create kspace_asum vector
kspace_asum = np.zeros((npxl,npxl),dtype="complex")
image_asum = np.zeros((npxl,npxl),dtype="complex")
kspace_a0 = np.zeros((npxl,npxl,n_exp), dtype="complex")
image_a0 = np.zeros((npxl,npxl,n_exp), dtype="complex")
nacq = npxl*npxl # the number of points in kspace_asum

# create figure for kspace_asum and image_asum
plt.ion()
fig_num_asum = 10

# create figure and maximize it
fig = plt.figure(fig_num_asum,figsize=(14,7))
plot_backend = matplotlib.get_backend()
mng = plt.get_current_fig_manager()
if plot_backend == 'TkAgg':
    # mng.resize(*mng.window.maxsize())
    mng.resize( 800, 400 )
elif plot_backend == 'wxAgg':
    mng.frame.Maximize( True )
elif plot_backend == 'Qt4Agg':
    mng.window.showMaximized()


# plot image_asum from kspace_asum and save data
plot_image_and_save (fig_num_asum, nmrObj, kspace_asum, "asum")


# settings for measurements
phenc_conf.en_lcs_pchg = 0 # disable lcs precharging because the vpc is already precharged by the reference scan
phenc_conf.en_lcs_dchg = 0 # disable lcs discharging because the vpc has to maintain its voltage for next scan

# post-processing parameters for the phase encoding imaging
phenc_conf.en_ext_rotation = 1 # enable external reference for echo rotation
phenc_conf.thetaref = theta_ref # external parameter: echo rotation angle
phenc_conf.en_conj_matchfilter = 0 # disable conjugate matchfiltering because it will auto-rotate the data
phenc_conf.en_ext_matchfilter = 0 # enable external reference for matched filtering
phenc_conf.echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average
sav_fig = 0 # disable figure save
show_fig = 0 # disable figure show

# run dummy scan to remove first acquisition T1 difference with the others
print("\n(Dummy scan)" )
nmrObj.folder_extension = ("\\dummy")
_, _, _, _, _, _, _, _, _ = phenc (nmrObj, phenc_conf, sav_fig, show_fig)

tmeas.reportTimeSinceLast("############################################################################## pre-cpmg")

sq_curr = 0 # the concentric square iteration #
threads = [] # list of threads to be joined later on
for i in range(0,np.size(idx_list,1)):
    print ("################################################### iter:(%d/%d) -- square:(%d/%d)" %(i+1,nacq,sq_curr+1,int(np.ceil(npxl/2))))# print iteration number
    
    
    nmrObj.folder_extension = ("") # remove the folder extension and use only the data directory to process the data
    
    # find the index of the kspace_asum to be measured
    x = int(idx_list[1,i])
    y = int(idx_list[2,i])
    
    # set gradient strength
    phenc_conf.gradz_volt = ilist[x];
    phenc_conf.gradx_volt = ilist[y];
        
    # run experiment to get real part
    phenc_conf.p180_xy_angle = 2 # set 1 for x-pulse and 2 for y-pulse for p180
    nmrObj.phenc_t2_iter(phenc_conf, i*2)
    # run experiment to get imaginary part
    phenc_conf.p180_xy_angle = 1 # set 1 for x-pulse and 2 for y-pulse for p180
    nmrObj.phenc_t2_iter(phenc_conf, i*2+1) 
    
    # start detached processing of the data to let another cpmg run without interruption
    if en_multithreads:
        process = Thread(target=compute_phenc_ReIm__mthread, args=[nmrObj, phenc_conf, i*2, x, y, kspace_asum, kspace_a0])
        process.start()
        threads.append(process)
    else:
        compute_phenc_ReIm__mthread(nmrObj, phenc_conf, i*2, x, y, kspace_asum, kspace_a0)
                
    tmeas.reportTimeSinceLast("############################################################################## cpmg ")
    
    # draw when one concentric square is finished
    if (i==np.size(idx_list,1)-1): # find if it's the last scan on the list
        if en_multithreads:
            # collect all running processes
            for thread in threads:
                thread.join()
        
        # plot image_asum from kspace_asum and save data
        plot_image_and_save (fig_num_asum, nmrObj, kspace_asum, "asum_%05d" % (idx_list[0,i]))
        
        tmeas.reportTimeSinceLast("############################################################################## plot and save data")

    else:
        sq_next = int(idx_list[0,i+1])
        if (sq_curr < sq_next): # find if it's the last scan within one concentric square. If it is, then draw the data
            sq_curr = sq_next # increment the square layer because this is the last scan of this layer
            
            if en_multithreads:
                # collect all running processes
                for thread in threads:
                    thread.join()
            
            # plot image_asum from kspace_asum and save data
            plot_image_and_save (fig_num_asum, nmrObj, kspace_asum, "asum_%05d" % (idx_list[0,i]))
            
            tmeas.reportTimeSinceLast("############################################################################## plot and save data")
 
# DUMMY SCAN: discharge power from the lcs
phenc_conf.en_lcs_pchg = 0
phenc_conf.en_lcs_dchg = 1
phenc_conf.p180_xy_angle = 1 # set for X p180 pulse
nmrObj.phenc_t2_iter( phenc_conf, 0 )

# clean up
nmrObj.exit()