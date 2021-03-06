"""
Module containing core convenience functions for working with seismic data in obspy
"""

import os,sys
import numpy as np
import cPickle as pickle

def create_path(directory):
    """Create a given path with all parent directories

    Provided there is write access the function will creates
    all levels of the given path.

    :type directory: string
    :param directory: path of the directory to be created

    :rtype: int
    :return: 0
    """
    if not os.path.exists(directory) :
        # Use try in case another parallel process has made it in that time
        try :
            os.makedirs(directory)
        except OSError as e :
            if e[0]==17 :
                pass
            else :
                raise OSError(e)
    else:
        assert os.path.isdir(directory), "%s exists but is not a directory" % subpath
    return 0

def save_to_pickle(fname,obj):
    """
    Save python object as a pickle
    file using cPickle.
    """
    pickle_out = open(fname,"wb")
    pickle.dump(obj, pickle_out)
    pickle_out.close()
    return

def load_from_pickle(fname):
    """
    Load a python object from a pickle
    file using cPickle
    """
    pickle_in = open(fname,"rb")
    obj = pickle.load(pickle_in)
    return obj


def write_st_to_mseed(st,fpath) :
    '''
    Write stream object to a miniseed file
    If dtype is float the encoding is set to float32 to save on disk space
    SAC files also save 32 bit floats.
    '''
    for tr in st:
        if tr.data.dtype=="float64" :
            tr.data = tr.data.astype(np.float32)
            tr.stats.mseed.encoding="FLOAT32"
    create_path(os.path.dirname(fpath))
    st.write(fpath,format="MSEED")
    return 0


def downsample(st,goal_sampling_rate) :
    '''
    Downsample stream to goal_sampling_rate
    (1) Apply antialias filter of 0.4 * goal_sampling_rate
    (2) Decimate, or else resample with lanczos method
    '''
    goal_sampling_rate=float(goal_sampling_rate)
    for tr in st :
        tr.filter("lowpass", freq=float(0.4*goal_sampling_rate), zerophase=True)
        dec_factor=tr.stats.sampling_rate/goal_sampling_rate
        if dec_factor.is_integer() :
            tr.decimate(int(dec_factor),no_filter=True)
        else :
            tr.data = np.array(tr.data)
            tr.interpolate(method="lanczos", sampling_rate=goal_sampling_rate, a=1.0)
    return st
