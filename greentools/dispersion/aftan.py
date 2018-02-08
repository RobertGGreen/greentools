"""
Module containing functions used around dispersion calculations
"""
from glob import glob
import os,sys
import numpy as np
from obspy.core import read

def read_disp_file(infile,disptype=None) :
    """ Reads the text file format containing dispersion
    results from aFTAN. 
    :type infile: string
    :param infile: Dispersion textfile name
    :type disptype: string
    :param disptype: centre_period = central period of FTAN filters,
                     inst_period =  instantaneous period of FTAN filters
                                defined as time derivative of phase 
                                of the analytic signal
    :rtype periods dispvels: :class:`~numpy.ndarray`
    :return: Numpy arrays of the periods and the picked velocities
    """
    if disptype=='inst_period' or disptype=='centre_period' :
        pass
    else :
        raise NameError("Input for function getdispersion must be <infile> <disptype>\n \
        <disptype> : centre_period or inst_period")

    # Read the AFTAN file and create lists
    lines=open(infile,'r').readlines()
    periods,dispvels=[],[]
    for line in lines :
        line=line.rstrip().split()
        centre_period,inst_period,grp_vel=float(line[1]),float(line[2]),float(line[3])
        phse_vel,ampl,snr=float(line[4]),float(line[5]),float(line[6])
        # Chose whether to take centre or observed period
        if disptype == 'inst_period' :
            periods.append(inst_period)
        elif disptype == 'centre_period' :
            periods.append(centre_period)
        dispvels.append(grp_vel)
    # Change lists to numpy arrays
    periods,dispvels=np.array(periods),np.array(dispvels)
    return periods,dispvels

def read_amp_file(infile,disptype,normalise=True):
    """ Reads the text file format containing the ftan 
    dispersion image from aFTAN
    Assumes name of disperion text file from infile
    :type infile: string
    :param infile: ftan image textfile name
    """
    dispfname=infile[:-4]+"_DISP.0"
    cleandispfname=infile[:-4]+"_DISP.1"
    periods,dispvels= read_disp_file(dispfname,disptype=disptype)
    try :
        periods_clean,dispvels_clean= read_disp_file(cleandispfname,disptype=disptype)
    except :
        periods_clean,dispvels_clean=None,None
    amplines=open(infile).readlines()
    nrow,ncol,dt,dist = amplines[0].strip().split()
    if ncol == "-15432" :
        print("No AMP map "+infile.split('/')[-1])
        return None,None,None,None,None,None
    amp = np.zeros([int(ncol),int(nrow)])
    tcnt=0
    vels=set()
    for l in amplines[1:] :
        if tcnt >= int(ncol) :
            tcnt=1
        else :
            tcnt+=1
        n,t,a=l.strip().split()
        vels.add(float(dist)/float(t))
        amp[int(ncol)-(tcnt),int(n)-1]=float(a)
    vels=sorted(vels)

    if normalise :
        # normalise amplitude at each freq
        ampn = np.zeros(amp.shape)
        for i in np.arange(0,ampn.shape[-1]) :
            ampn[:,i]=amp[:,i]/np.max(amp[:,i])
    else :
        ampn=amp
    return periods,vels,ampn,dispvels,periods_clean,dispvels_clean


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
