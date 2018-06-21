# -------------------------------
#| Robert Green   GFZ Potsdam    |
#| 2018-03-15                    |
# -------------------------------
"""
Module containing misc functions.
"""
import numpy as np
def load_multi_segment_txtfile(fname) :
    """Read a multisegmentline text file of the format used in
    gmt .xy files, and reads into numpy arrays. 

    :type fname: string
    :param fname: filename of textfile
    :type return: dictionary
    :param return: dictionary where each entry is a numpy 
                    array of shape (n,3) for each line
    """
    contourlines=open(fname).readlines()
    separator_ind=[i for i,s in enumerate(contourlines) if "> " in s]
    dict={}
    # Separating the segments, convert to np.array
    for i in range(0,len(separator_ind)-1) :
        seg=contourlines[separator_ind[i]+1:separator_ind[i+1]]
        #seg_ar=np.array([l.strip().split('\t') for l in seg]).astype(np.float)
        seg_ar=np.array([l.strip().split() for l in seg]).astype(np.float)
        dict[i]=seg_ar
    # Do the final segment
    seg=contourlines[separator_ind[-1]+1:]
    #seg_ar=np.array([l.strip().split('\t') for l in seg]).astype(np.float)
    seg_ar=np.array([l.strip().split() for l in seg]).astype(np.float)
    dict[i+1]=seg_ar
    return dict
