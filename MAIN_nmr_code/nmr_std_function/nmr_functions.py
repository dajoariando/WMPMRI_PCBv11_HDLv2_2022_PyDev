import csv
import math
import os

import matplotlib
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
from nmr_std_function import data_parser
from nmr_std_function.data_parser import convert_to_prospa_data_t1
from nmr_std_function.signal_proc import down_conv, nmr_fft, butter_lowpass_filter
import numpy as np


def plot_echosum( nmrObj, filepath, samples_per_echo, echoes_per_scan, en_fig ):

    dat1 = np.array( data_parser.read_data( filepath ) )  # use ascii representation
    dat2 = np.reshape(dat1, ( echoes_per_scan, samples_per_echo))
    dat3 = np.mean(dat2,0)
    
    # plot the individual echoes
    plt.figure(0)
    for i in range(echoes_per_scan):
        plt.plot(dat2[i,:], color='y')
    
    # plot the echo sum
    # plt.figure(1)    
    plt.plot(dat3, color='blue')
    
    plt.show()
    

def calcP90( Vpp, rs, L, f, numTurns, coilLength, coilFactor ):

    # estimates the 90 degree pulse length based on voltage output at the coil
    # Vpp: measured voltage at the coil
    # rs: series resitance of coil
    # L: inductance of coil
    # f: Larmor frequency in Hz
    # numTurns: Number of turns in coil
    # coilLength: Length of coil in m
    # coilFactor: obtained by measurement compensation with KeA, will be coil geometry
    # dependant

    import math
    import numpy as np

    gamma = 42.58e6  # MHz/Tesla
    u = 4 * np.pi * 10 ** -7
    Q = 2 * np.pi * f * L / rs
    Vrms = Vpp / ( 2 * math.sqrt( 2 ) )
    Irms = Vrms / ( math.sqrt( Q ** 2 + 1 ** 2 ) * rs )

    # extra factor due to finite coil length (geometry)
    B1 = u * ( numTurns / ( 2 * coilLength ) ) * Irms / coilFactor
    P90 = ( 1 / ( gamma * B1 ) ) * ( 90 / 360 )
    Pwatt = ( Irms ** 2 ) * rs

    return P90, Pwatt

