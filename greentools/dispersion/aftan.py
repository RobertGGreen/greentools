"""
Module containing functions used around dispersion calculations
"""
from glob import glob
import os,sys
import numpy as np
from obspy.core import read


def read_aftan_resultfile(infile,disptype="centre_period") :

    if disptype=='obs_period' or disptype=='centre_period' :
        pass
    else :
        print "Input for function getdispersion must be <infile> <disptype>"
        print "<disptype> : centre_period or obs_period"

    # Read the AFTAN file and create lists
    lines=open(infile,'r').readlines()
    periods,dispvels=[],[]
    for line in lines :
        line=line.rstrip().split()
        centre_period,obs_period,grp_vel=float(line[1]),float(line[2]),float(line[3])
        phse_vel,ampl,snr=float(line[4]),float(line[5]),float(line[6])
        # Chose whether to take centre or observed period
        if disptype == 'obs_period' :
            periods.append(obs_period)
        elif disptype == 'centre_period' :
            periods.append(centre_period)
        dispvels.append(grp_vel)
    # Change lists to numpy arrays
    periods,dispvels=np.array(periods),np.array(dispvels)

    # Define periods you want to interpolate AFTAN results onto
    interp_periods=np.array([4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0,
                            11.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0,21.0,
                            22.0,23.0,24.0,25.0,26.0,27.0,28.0,29.0,30.0,31.0,32.0,
                            33.0,34.0,35.0,36.0,37.0,38.0,39.0])

    # Check if any interp_periods are outside data range and remove
    delindices=[]
    for i in range(0,len(interp_periods)) :
        if interp_periods[i] < periods[0] or interp_periods[i] > periods[-1] :
            delindices.append(i)
    interp_periods=np.delete(interp_periods,delindices)

    # Interpolate groupvel on required periods (interp_periods)
    interp_grp_vel=np.interp(interp_periods,periods,dispvels)

    return(interp_periods,interp_grp_vel)
