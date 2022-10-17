'''
Created on May 24, 2022

@author: David Ariando

'''

#!/usr/bin/python

import os
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from nmr_std_function.nmr_class import nmr_system_2022
from nmr_std_function import data_parser
from nmr_std_function.time_func import time_meas
from nmr_std_function.experiments import phenc,phenc_ReIm


# get current time
now = datetime.now()
datatime = now.strftime("%y%m%d_%H%M%S")

# measurements folder settings
data_parent_folder = 'D:\\NMR_DATA'
meas_folder = 'PHENC_2D_'+datatime

# create folder for measurements
client_data_folder = data_parent_folder+'\\'+meas_folder
if not os.path.exists(client_data_folder):
    os.makedirs(client_data_folder)

# variables
sav_fig = 0 # save figures
show_fig = 0  # show figures
report_time = True  # measure time
process_data = 1 # process the NMR data

tmeas = time_meas(report_time)

# import default measurement configuration and modify
from sys_configs.phenc_conf_221015 import phenc_conf_221015
phenc_conf = phenc_conf_221015()

# modify default parameters
phenc_conf.n_iterate = 2
phenc_conf.gradz_len_us = 800 # gradient pulse length
phenc_conf.gradx_len_us = 800 # gradient pulse length
phenc_conf.enc_tao_us = 1000 # the encoding time
        
# set the maximum current and number of pixels 
imax = 3.0 # maximum current (both polarity will be used)
npxl = 61 # number of pixels inside the image
ilist = np.linspace(-imax, imax, npxl) # create list of current being used

# modify current list to account for 100mA DC biasing in the gradient circuit
# the current is 0 when it's set to +/- 0.1V, instead of 0V.
for idx,v in enumerate(ilist):
    if v > 0.0001 : # use 0.01 instead of 0.0 to avoid deal with floating point number around 0.0
        ilist[idx] = v+0.1
    elif v<(-0.0001) :
        ilist[idx] = v-0.1
    else :
        ilist[idx] = 0.1 # 0.1V means 0.1A to the transistor but 0.0A to the coil, because the other transistor is biased at 0.1A when it's turned off.

# instantiate nmr object
nmrObj = nmr_system_2022( client_data_folder )

# perform reference scan
print("\n(Reference scan)" )
nmrObj.folder_extension = "\\ref"
phenc_conf.en_lcs_dchg = 0 # disable lcs precharging
_, _, _, _, _, _, _, theta_ref = phenc (nmrObj, phenc_conf)

tmeas.reportTimeSinceLast("############################################################################### load libraries and reference scan")

# create index list with 3 width, 1 for concentric square #, 2 and 3 for index of the square
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
    
# create kspace vector
kspace = np.zeros((npxl,npxl),dtype="complex")
image = np.zeros((npxl,npxl),dtype="complex")

# settings for measurements
phenc_conf.en_lcs_pchg = 0 # disable lcs precharging because the vpc is already precharged by the reference scan
phenc_conf.en_lcs_dchg = 0 # disable lcs discharging because the vpc has to maintain its voltage for next scan

# processing parameters    
phenc_conf.en_ext_rotation = 1 # enable external reference for echo rotation
phenc_conf.thetaref = theta_ref # external parameter: echo rotation angle
phenc_conf.en_conj_matchfilter = 0 # disable conjugate matchfiltering because it will auto-rotate the data
phenc_conf.en_ext_matchfilter = 0 # enable external reference for matched filtering
phenc_conf.echoref_avg = 0 # echo_avg_ref # external parameter: matched filtering echo average

# create figure for kspace and image
fig = plt.figure(25,figsize=(14,7))
plt.subplot(1,2,1)
plt.imshow(np.abs(kspace),cmap='gray')
plt.subplot(1,2,2)
plt.imshow(np.abs(image),cmap='gray')
fig.canvas.draw()
plt.pause(0.01)
np.savetxt(nmrObj.client_data_folder+"\\kspace.txt",kspace,fmt='%0.6f')

sq_curr = 0 # the concentric square iteration #
for i in range(0,np.size(idx_list,1)):
    
    nmrObj.folder_extension = ("") # remove the folder extension and use only the data directory to process the data
    
    x = int(idx_list[1,i])
    y = int(idx_list[2,i])
    
    # set gradient strength
    phenc_conf.gradz_volt = ilist[x];
    phenc_conf.gradx_volt = ilist[y];
        
    # run measurement and process data
    asum_cmplx = phenc_ReIm(nmrObj, phenc_conf)
    kspace[x,y] = asum_cmplx
    
     # draw when one concentric square is finished
    if (i==np.size(idx_list,1)-1): # find if it's the last scan on the list list
        image = np.fft.fftshift(np.fft.fft2(kspace))
        
        fig = plt.figure(25)
        plt.subplot(1,2,1)
        plt.imshow(np.abs(kspace),cmap='gray')
        plt.subplot(1,2,2)
        plt.imshow(np.abs(image),cmap='gray')
        fig.canvas.draw()
        plt.pause(0.01)
        
        plt.savefig( nmrObj.client_data_folder + '\\image.png' )
        np.savetxt(nmrObj.client_data_folder+"\\kspace.txt",kspace,fmt='%0.6f')
            
    else:
        sq_next = int(idx_list[0,i+1])
        if (sq_curr < sq_next): # find if it's the last scan within one concentric square
            sq_curr = sq_next
            
            image = np.fft.fftshift(np.fft.fft2(kspace))
        
            fig = plt.figure(25)
            plt.subplot(1,2,1)
            plt.imshow(np.abs(kspace),cmap='gray')
            plt.subplot(1,2,2)
            plt.imshow(np.abs(image),cmap='gray')
            fig.canvas.draw()
            plt.pause(0.01)
            
            plt.savefig( nmrObj.client_data_folder + '\\image.png' )
            np.savetxt(nmrObj.client_data_folder+"\\kspace.txt",kspace,fmt='%0.6f')
                
    tmeas.reportTimeSinceLast("############################################################################## cpmg & processing")

plt.show()
 
# DUMMY SCAN: discharge power from the lcs
phenc_conf.en_lcs_pchg = 0
phenc_conf.en_lcs_dchg = 1
phenc_conf.p180_xy_angle = 1 # set for X p180 pulse
nmrObj.phenc_t2_iter( phenc_conf )