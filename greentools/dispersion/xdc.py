"""
Module containing functions used around dispersion measurements with xdc
"""
import numpy as np

def read_xdc_inst_pickfile(fname):
    '''
    Reads the textfile format recording dispersion picks from 
    xdc (instantaneous freq version).
    :param fname: The pick filename
    :type fname: string
    :return: 2D array with columns; centre_freq,inst_freq,travel_time,distance
    :return type: class:`~numpy.ndarray`
    '''
    pick_centre_freq, pick_inst_freq, pick_time, pick_dist, _, _ = np.loadtxt(fname).T
    pick_time[pick_time<0.0]=np.nan
    return np.column_stack([pick_centre_freq,pick_inst_freq,pick_time,pick_dist])
