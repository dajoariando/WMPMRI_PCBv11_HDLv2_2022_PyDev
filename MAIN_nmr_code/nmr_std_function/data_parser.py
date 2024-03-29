'''
Created on Mar 30, 2018

@author: David Ariando
'''

import os
import csv
import numpy as np
from numpy import float64
import shutil
import math

from nmr_std_function.signal_proc import down_conv


def parse_simple_info( data_folder, file_name ):
    file_path = data_folder + "/" + file_name
    f = open( file_path )
    csv_f = csv.reader( f, delimiter=' ' )
    data = []
    for a in csv_f:
        try:
            data.append( float( a[0] ) )
        except:
            data.append( ( a[0] ) )
    f.close()
    return data


def parse_csv_float2col( data_folder, file_name ):
    file_path = data_folder + "/" + file_name
    f = open( file_path )
    csv_f = csv.reader( f, delimiter=',' )
    data1 = []
    data2 = []
    for a in csv_f:
        data1.append( float( a[0] ) )
        data2.append( float( a[1] ) )
    f.close()
    return data1, data2


def parse_csv_float3col( data_folder, file_name ):
    file_path = data_folder + "/" + file_name
    f = open( file_path )
    csv_f = csv.reader( f, delimiter='\t' )
    data1 = []
    data2 = []
    data3 = []
    for a in csv_f:
        data1.append( float( a[0] ) )
        data2.append( float( a[1] ) )
        data3.append( float( a[2] ) )
    f.close()
    return data1, data2, data3


def parse_csv_float4col( data_folder, file_name, skip_lines ):
    file_path = data_folder + "/" + file_name
    f = open( file_path )
    csv_f = csv.reader( f, delimiter=',' )

    for a in range( skip_lines ):
        next( csv_f )

    data1 = []
    data2 = []
    data3 = []
    data4 = []
    for a in csv_f:
        data1.append( float( a[0] ) )
        data2.append( float( a[1] ) )
        data3.append( float( a[2] ) )
        data4.append( float( a[3] ) )
    f.close()
    return data1, data2, data3, data4


def parse_info( data_folder, file_name ):
    # filename = "CPMG_iterate_settings.txt"
    file_path = data_folder + '\\' + file_name
    f = open( file_path )
    csv_f = csv.reader( f, delimiter=' ' )
    param = []
    value = []

    for a in csv_f:
        param.append( ( a[0] ) )
        try:
            value.append( float( a[2] ) )
        except:
            value.append( a[2] )
    f.close()
    return ( param, value )


def find_value( param_name, param_list, value_list ):
    return value_list[[i for i, elem in enumerate( param_list ) if param_name in elem][0]]


def read_data( file_path ):
    f = open( file_path )
    csv_f = csv.reader( f )
    data = []
    for a in csv_f:
        data.append( ( int( a[0] ) ) )
    f.close()
    return data


def read_hex_float( file_path ):
    import struct

    f = open( file_path, 'rb' )  # read as binary
    rddata = f.read()  # read data in bytes
    f.close()

    rddata = bytearray( rddata )  # convert to bytearray
    rddata = np.array( rddata )  # convert to numpy integer array
    # restructure to have 4 bytes per float number
    rddata = np.array( rddata ).reshape( len( rddata ) >> 2, 4 )

    # convert data to float
    data = np.zeros( len( rddata ), dtype='float' )
    for i in range( len( rddata ) ):
        data[i] = struct.unpack( 'f', rddata[i] )[0]  # 'f' is float datatype

    return data


def read_hex_int16( file_path ):
    import struct

    f = open( file_path, 'rb' )  # read as binary
    rddata = f.read()  # read data in bytes
    f.close()

    rddata = bytearray( rddata )  # convert to bytearray
    rddata = np.array( rddata )  # convert to numpy integer array
    # restructure to have 2 bytes per int16 number
    rddata = np.array( rddata ).reshape( len( rddata ) >> 1, 2 )

    # convert data to integer 16-bit
    data = np.zeros( len( rddata ), dtype='int16' )
    for i in range( len( rddata ) ):
        # 'H' is unsigned short integer datatype
        data[i] = struct.unpack( 'H', rddata[i] )[0]

    return data


def read_hex_int32( file_path ):
    import struct

    f = open( file_path, 'rb' )  # read as binary
    rddata = f.read()  # read data in bytes
    f.close()

    rddata = bytearray( rddata )  # convert to bytearray
    rddata = np.array( rddata )  # convert to numpy integer array
    # restructure to have 4 bytes per integer number
    rddata = np.array( rddata ).reshape( len( rddata ) >> 2, 4 )

    # convert data to integer
    data = np.zeros( len( rddata ), dtype='int32' )
    for i in range( len( rddata ) ):
        # 'L' is unsigned long integer datatype. and 'l' is long integer datatype
        data[i] = struct.unpack( 'l', rddata[i] )[0]

    return data


def ensure_dir( file_path ):
    directory = os.path.dirname( file_path )
    if not os.path.exists( directory ):
        os.makedirs( directory )


def write_text_overwrite( data_folder, filename, data ):
    with open( data_folder + '/' + filename, 'w', newline='' ) as csvfile:
        csvfile.write( data )
        csvfile.write( '\n' )


def write_text_append( data_folder, filename, data ):
    with open( data_folder + '/' + filename, 'a', newline='' ) as csvfile:
        csvfile.write( data )
        csvfile.write( '\n' )


def write_text_append_row( data_folder, filename, rowvect_num ):
    with open( data_folder + '/' + filename, 'a', newline='' ) as csvfile:
        for line in rowvect_num:
            csvfile.write( "%0.5f" % line )
            csvfile.write( ',' )
        csvfile.write( '\n' )


def convert_to_prospa_data_t1( datain, path, write_csv ):
    # datain     : input data in tauSteps*NoE matrix format
    # write_csv  : write output to csv file

    # SETTINGS AND DATA PARSING
    # find nmr settings from the folder
    file_info_name = "acqu.par"
    ( param_list, value_list ) = data_parser.parse_info( 
        path, file_info_name )  # read file
    tE = data_parser.find_value( 'echoTimeRun', param_list, value_list )
    SpE = int( data_parser.find_value( 'nrPnts', param_list, value_list ) )
    NoE = int( data_parser.find_value( 'nrEchoes', param_list, value_list ) )
    en_ph_cycle_proc = int( data_parser.find_value( 
        'usePhaseCycle', param_list, value_list ) )
    nrIterations = int( data_parser.find_value( 
        'nrIterations', param_list, value_list ) )
    Sf = data_parser.find_value( 
        'adcFreq', param_list, value_list ) * 1e6
    Df = data_parser.find_value( 
        'b1Freq', param_list, value_list ) * 1e6
    start_param = data_parser.find_value( 'minTau', param_list, value_list )
    stop_param = data_parser.find_value( 'maxTau', param_list, value_list )
    nsteps = int( data_parser.find_value( 'tauSteps', param_list, value_list ) )
    logspaceyesno = int( data_parser.find_value( 
        'logSpace', param_list, value_list ) )

    # CONVERSION
    if logspaceyesno:
        sweep_param = np.logspace( 
            np.log10( start_param ), np.log10( stop_param ), nsteps )
    else:
        sweep_param = np.linspace( start_param, stop_param, nsteps )

    data = np.zeros( ( len( sweep_param ), NoE * 2 ), dtype=float )
    for i in range( 0, len( sweep_param ) ):
        data[i, 0:NoE * 2:2] = np.real( datain[i,:] )
        data[i, 1:NoE * 2:2] = np.imag( datain[i,:] )

    if write_csv:
        kea_dir = path + '1/'
        ensure_dir( kea_dir )  # create dir for kea data
        shutil.copyfile( path + file_info_name, kea_dir +
                        file_info_name )  # copy kea acqu.par

        with open( kea_dir + 'data2.csv', 'w', newline='' ) as csvfile:
            filewriter = csv.writer( csvfile, delimiter=',' )
            for i in range( 0, len( sweep_param ) ):
                filewriter.writerow( data[i,:] )
