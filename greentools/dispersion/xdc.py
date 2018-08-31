"""
Module containing functions used around dispersion measurements with xdc
"""
import numpy as np
#def read_xdc_inst_pickfile(fname):
#    '''
#    Reads the textfile format recording dispersion picks from 
#    xdc (instantaneous freq version).
#    :param fname: The pick filename
#    :type fname: string
#    :return: 2D array with columns; centre_freq,inst_freq,vel
#    :return type: class:`~numpy.ndarray`
#    '''
#    pick_centre_freq, pick_inst_freq, pick_time, pick_dist, _, _ = np.loadtxt(fname).T
#    mk=pick_time>0
#    pick_centre_freq=pick_centre_freq[mk]
#    pick_inst_freq=pick_inst_freq[mk]
#    pick_time=pick_time[mk]
#    pick_dist=pick_dist[0]
#    pick_vel=pick_dist/pick_time
#    return np.column_stack([pick_centre_freq,pick_inst_freq,pick_vel])

def read_xdc_inst_pickfile(fname):
    '''
    Reads the textfile format recording dispersion picks from 
    xdc (instantaneous freq version).
    :param fname: The pick filename
    :type fname: string
    :return: 2D array with columns; centre_freq,inst_freq,vel
    :return type: class:`~numpy.ndarray`
    '''
    pick_centre_freq, pick_inst_freq, pick_time, pick_dist, _, _ = np.loadtxt(fname).T
    #mk=pick_time>0
    #pick_centre_freq=pick_centre_freq[mk]
    #pick_inst_freq=pick_inst_freq[mk]
    #pick_time=pick_time[mk]
    pick_time[pick_time<0.0]=np.nan
    #pick_dist=pick_dist[0]
    #pick_vel=pick_dist/pick_time
    return np.column_stack([pick_centre_freq,pick_inst_freq,pick_time,pick_dist])
