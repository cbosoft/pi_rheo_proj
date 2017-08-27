
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 11:13:37 2014

@author: calum
modified by: chris boyle (christopher.boyle.101@strath.ac.uk)
"""

# Code to import volt/time data from novel method, remove noise from the data
# and to perform some statistical analysis, primarily power law fits.
# Requires plfit module obtainable via https://pypi.python.org/pypi/plfit
# Or entering "pip install powerlaw" in the terminal

import plfit
import numpy as np
from pylab import *
import peakdetect as pk
import random
from sys import argv
from glob import glob
import pandas as pd

##############################################
################# Read data ##################
##############################################

def read_file( filename ):

    infile = open( filename )
    lines = infile.readlines()
    infile.close()
    j = 0
    time_data = [] # initialise time column
    volt_data = [] # initialise voltage column

    for line in lines:

        data        = line.split()
        timedat     = float( j )
        volt        = float( data[0] )
        
        print timedat, volt
        
        time_data.append( timedat )
        volt_data.append( volt )
        
        j += 1
        
    time_data = [ x * 0.000001 * 100000 for x in time_data ]  # = 0.09999999999999999? ~= 0.1

    return time_data, volt_data

#############################################
########### Clean the data ##################
#############################################

def remove_noise( time_data, volt_data, sma_max, sma_min ):

    volt_clean = []
    time_clean = []

    for q in range( 0, len( volt_data ) ):

        if ( volt_data[q] >= sma_max ) or ( volt_data[q] <= sma_min ):
            time_clean.append( time_data[q] )
            volt_clean.append( volt_data[q] )

    return volt_clean, time_clean

###########################################################
############## Random Numbers between times ###############
###########################################################

def cluster_survival( time_clean, k ):

        survival_times = []
        for x in range( 1, len( time_clean ) ):
            survival = time_clean[x] - random.uniform( time_clean[x - k], time_clean[x] )
            survival_times.append( survival )

        return survival_times

###########################################################
############## Time difference between peaks ##############
###########################################################

def differences( time_clean ):

        delta_t = []
        for x in range( 1, len( time_clean ) ):
            diff = time_clean[x] - time_clean[x - 1]
            delta_t.append( diff )

        return delta_t

###########################################################
################## Simple Moving Average ##################
###########################################################

def movingaverage( values, window ):

        weights = np.repeat( 1.0, window ) / window
        sma = np.convolve( values, weights, 'same' )
        return sma

################################################################################
######################## Autocorrelation Function ##############################
################################################################################

def get_autocorr( volt_data ):
    phi = correlate( volt_data, volt_data, mode='full' )
    phi = phi[ (phi.size / 2): ]
    phi = phi / phi[0]
    return phi
    
def parse_args( args ):
    '''
    [cbo]
    
    parse_args( args )
    
    parameters:
        args                list of arguments passed to the interpreter
    
    valid arguments:
        '--file <FILE>'     dictates the file to be analysed, otherwise searches the current dir
        '-f <FILE>          for a '.csv' file
        
        '--x_title <COL>'   name of column to read in as x
        '-x <COL>'
        
        '--y_title <COL>'   name of column to read in as y
        '-y <COL>'
        
        '--start <INDEX>'   sets starting row to use from data file
        '-st'
        
        '--skip <JUMPS>'    how much of the data to skip
        '-st'
        
        '--length <LENGTH>  how far into the data file to read
        '-l'
    
    returns:
        file                '.csv' file to read
        x_col               title of x column to read
        y_col               title of y column to read
        start               index of data to begin reading
        skip                frequency of data skipping
        length              number of entries to read
    '''
    
    # Set default values:
    file = sorted(glob("./*.csv"))[0]
    x_col = "t"
    y_col = "Pzv1"
    start = 0
    skip = 1
    length = -1
    
    index = 1
    while (index < len(args)):
        if args[index] == "--file" or args[index] == "-f":
            file = args[index + 1]
            index += 1
        elif args[index] == "--x_title" or args[index] == "-x":
            x_col = args[index + 1]
            index += 1
        elif args[index] == "--y_title" or args[index] == "-y":
            y_col = args[index + 1]
            index += 1
        elif args[index] == "--start" or args[index] == "-st":
            start = int(args[index + 1])
            index += 1
        elif args[index] == "--skip" or args[index] == "-sk":
            skip = int(args[index + 1])
            index += 1
        elif args[index] == "--length" or args[index] == "-l":
            length = int(args[index + 1])
            index += 1
        else:
            raise Exception("Unknown argument \"{}\"".format(args[index]))
        index += 1
    return file, x_col, y_col, start, skip, length

def read_csv(file, x_col, y_col, start, skip, length):
    '''
    [cbo]
    
    read_csv(file, x_col, y_col, start, skip, length)
    
    parameters:
        file                '.csv' file to read
        x_col               title of x column to read
        y_col               title of y column to read
        start               index of data to begin reading
        skip                frequency of data skipping
        length              number of entries to read
    
    returns:
        x_data              numpy array (float64) of read data
        y_data              numpy array (float64) of read data
    '''
    
    datf = pd.read_csv(file)
    
    x_data = np.array(datf[x_col], np.float64)
    y_data = np.array(datf[y_col], np.float64)
    
    if (start + length > len(x_data)): length = -1 * (start + 1) #--> start + length = -1
    
    x_data = x_data[start:skip:(start + length)]
    y_data = y_data[start:skip:(start + length)]
    
    return x_data, y_data
    
#####################################################################
#################### Choose Data to Analyse #########################
#####################################################################
#file_list = ['561.txt']
file_list = ['FouriercompsX1_62.txt']
#file_list = ['611.txt', '612.txt', '613.txt']

x_data, y_data = read_csv(parse_args(sys.argv))

#file, x_col, y_col, start, skip, length = parse_args(sys.argv)
#x_data, y_data = read_csv(file, x_col, y_col, start, skip, length)

for filename in file_list:

    time_raw, signal_raw = read_file(filename)
    time_data = time_raw[:2400]
    volt_data = signal_raw[:2400]
    sma5 = movingaverage(volt_data,5) #moving average, pass data and window
    sma31 = movingaverage(volt_data,31)
    sma65 = movingaverage(volt_data,65)
    sma90 = movingaverage(volt_data,200)
    volt_clean, time_clean = remove_noise(time_data, volt_data,0,0) #simple remove noise, pass upper and lower bounds for noise
    crude_delta_t = differences(time_clean)

    peaks = pk.peakdetect(volt_clean , time_clean ,2)   # external peakdetect
    peaksX,peaksY = zip(*peaks[0])
    peaks_dt = differences(peaksX)
    #print(time_data)


    #    print k
    #survival_times_crude = cluster_survival(time_clean, 1) #cluster survivals simple cut data
    survival_times_crude = cluster_survival(peaks_dt, 1) #cluster survivals simple cut data
    #print min(survival_times_crude)

    ########################################################################
    ####################### Power Law  fits ################################
    ########################################################################
    # choose val in plfit.plfit(val) to fit power law to preferred dataset
    # details of fit should be outputted in console (xmin, \alpha etc.)
    #
    crudelaw = plfit.plfit(survival_times_crude) #fit power law

    figure(1)

    title('CDF (Simple Cut-off)')
    xlabel('Jamming Duration (s)')
    ylabel('P (Jamming Duration)')
    crudelaw.plotcdf(pointcolor='g', pointmarker='o') #cumulative
    savefig('cdf68XZ.png')

    #figure(2)

    #title('PDF (Simple Cut-off)')
    #xlabel('Jamming Duration (s)')
    #ylabel('P (Jamming Duration)')
    #crudelaw.plotpdf() #cumulative


    figure(3)
    plt.plot(time_data,volt_data,'r')
    plt.plot(peaksX,peaksY, 'o')
    plt.title('Fourier component fluctuations (6.8)')
    plt.ylabel('Fourier component magnitude')
    plt.xlim(min(time_data),max(time_data))
    plt.xlabel('Simulation Time')
    plt.savefig('WCA68XZtrajectory.png')
    #plt.plot(sma90)
    #plt.plot(sma31)
    #plt.plot(sma65)



    #figure(4)
    #title('Colloidal Suspension Jamming Data Phi=0.56')
    #xlabel('Time (s)')
    #ylabel('-Voltage (V)')
    #plot(time_data,volt_data,'b-', peaksX,peaksY,'ro') # peaks on raw data found w/peakdetect

    plt.show()
