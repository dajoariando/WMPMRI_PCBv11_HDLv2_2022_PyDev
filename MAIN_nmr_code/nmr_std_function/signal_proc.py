'''
Created on Apr 4, 2018

@author: David Ariando
'''

import numpy as np
import math
from scipy.signal import butter, lfilter, freqz, filtfilt
import matplotlib.pyplot as plt


def butter_lowpass( cutoff, fs, order ):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter( order, normal_cutoff, btype='low', analog=False )
    return b, a


def butter_lowpass_filter( data, cutoff, fs, order, en_figure ):
    b, a = butter_lowpass( cutoff, fs, order )

    if en_figure:
        w, h = freqz( b, a, worN=8000 )
        plt.figure( 10 )
        plt.plot( 0.5 * fs * w / np.pi, np.abs( h ), 'b' )
        plt.plot( cutoff, 0.5 * np.sqrt( 2 ), 'ko' )
        plt.axvline( cutoff, color='k' )
        plt.xlim( 0, 0.5 * fs )
        plt.title( "Lowpass Filter Frequency Response" )
        plt.xlabel( 'Frequency [Hz]' )
        plt.grid()
        pass

    # y = lfilter( b, a, data ) # normal digital filter
    y = filtfilt(b, a, data) # digital filter with backward and forward

    if en_figure:
        plt.figure( 11 )
        plt.plot( data, label='raw data' )
        plt.plot( y, label='filt data' )
        plt.legend()
        plt.show()

    return y


def down_conv( s, k, tE, Df, Sf, dconv_lpf_ord, dconv_lpf_cutoff_Hz ):

    # settings
    simp_dconv = False  # perform simplified downconversion for 4 phases signal
    padding_fact = 1 # added padding with dc averaged value to remove transient in filter. Padding factor 1 means adding 1*amount of data up front and at the back of the data, i.e. resulting 3x amount of data length.

    # filter parameter
    # dconv_lpf_ord = 2
    # lpf_cutoff_Hz = 10e3  # in Hz
    
    # data vectors
    datlen = len(s)
    T = 1 / Sf
    t = np.linspace( k * tE, k * tE + T * ( datlen - 1 ), datlen )

    # downconversion below Nyquist rate
    # Ds = abs(Df - Sf)
    # sReal = s * np.cos(2 * math.pi * Ds * t)
    # sImag = s * np.sin(2 * math.pi * Ds * t)
    
    # downconversion
    if not simp_dconv:  # normal downconversion
        # downconversion at Nyquist rate or higher
        sReal = s * np.cos( 2 * math.pi * Df * t )
        sImag = s * np.sin( 2 * math.pi * Df * t ) * (-1)
    else:  # simulated downconversion happened in FPGA
         # echo is assumed to always start at phase 0. It is true if the pulse
         # length and delay length for pi and 2pi pulse is multiplication of 4
        sReal = np.zeros( datlen, dtype=float )
        sImag = np.zeros( datlen, dtype=float )
        for i in range( 0, datlen >> 2 ):
            sReal[i * 4 + 0] = s[i * 4 + 0] * 0
            sReal[i * 4 + 1] = s[i * 4 + 1] * 1
            sReal[i * 4 + 2] = s[i * 4 + 2] * 0
            sReal[i * 4 + 3] = s[i * 4 + 3] * -1
            sImag[i * 4 + 0] = s[i * 4 + 0] * 1
            sImag[i * 4 + 1] = s[i * 4 + 1] * 0
            sImag[i * 4 + 2] = s[i * 4 + 2] * -1
            sImag[i * 4 + 3] = s[i * 4 + 3] * 0
            
    # compute mean or average of the first cycles of data frequency
    nDf = 5 # select the number of RF cycles to be averaged
    ncyc = int(np.round(Sf/Df*nDf)) # find the number of points to be averaged
    
    # find the average from the start of the data
    sRealAvgInit = np.mean(sReal[:ncyc])
    sImagAvgInit = np.mean(sImag[:ncyc])
    
    # find the average from the end of the data
    sRealAvgEnd = np.mean(sReal[-ncyc:])
    sImagAvgEnd = np.mean(sImag[-ncyc:])
    
    # create vectors: padded start and end of the data with its averaged value
    sRealPadded = np.full((1+2*padding_fact)*datlen, sRealAvgInit, dtype=float) # initialize the start of the real data
    sImagPadded = np.full((1+2*padding_fact)*datlen, sImagAvgInit,  dtype=float) # initialize the start of the imag data
    sRealPadded[(padding_fact+1)*datlen:] =  sRealAvgEnd # initialize the end of the real data
    sImagPadded[(padding_fact+1)*datlen:] =  sImagAvgEnd # initialize the end of the imag data
    
    # insert the original value into the middle of the data
    sRealPadded[padding_fact*datlen:(padding_fact+1)*datlen] = sReal
    sImagPadded[padding_fact*datlen:(padding_fact+1)*datlen] = sImag
            
    # lowpass filter
    rPadded = butter_lowpass_filter( sRealPadded + 1j * sImagPadded, dconv_lpf_cutoff_Hz, Sf, dconv_lpf_ord, False )
    
    # recover the data without padding
    r = rPadded[padding_fact*len(sReal):(padding_fact+1)*len(sReal)]

    return r


def nmr_fft( data, fs, en_fig ):
    spectx = np.linspace( -fs / 2, fs / 2, len( data ) )
    specty = np.fft.fftshift( np.fft.fft( data - np.mean( data ) ) )
    specty = np.divide( specty, len( data ) )  # normalize fft
    specty = np.abs(specty)
    if en_fig:
        plt.figure
        plt.plot( spectx, specty, 'b' )
        plt.title( "FFT_data" )
        plt.xlabel( 'Frequency [MHz]' )
        plt.grid()
        plt.show()
    return spectx, specty
