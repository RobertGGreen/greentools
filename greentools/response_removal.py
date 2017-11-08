# -------------------------------
#| Robert Green   GFZ Potsdam    |
#| 2017-11-03                    |
# -------------------------------
"""
Module containing functions for use in instrument response removal.
"""

def deconvolve_with_pz(st,response_prefilt,pz) :
    '''
    Deconvolves stream using the supplied polezero dictionary
    -Demeans and detrends each trace of stream
    -Applies 1% taper to prevent ringing at the end of traces
    -Prefilters data prior to deconvolution to prevent amplication of noise

    response_prefilt=(f1,f2,f3,f4) - tuple, where f1<f2<f3<f4
    Frequencies should be conditioned to your intended time series
    Both f3 and f4 should be less than the Nyquist. To avoid ringing in 
    the output time series, a suggested rule-of-thumb is:
    f1 = f2/2 and f4 >= 2*f3

    Taper fraction 0.01 means you lose 7 mins both at start and end of a 24 hour file

    Obspy pole-zero dictionaries
    (1) "poles" should be a list of tuples, e.g. [(x+yj),(r+sj)]
    (2) "zeros" should be a list of complexes, e.g. [0j,0j]
    (3) "sensitivity" is the total sensitivity and is used if remove_sensitivity=true 
        "digitizer gain" and "seismometer gain" are floats but are passive and there for reference. 
         Multiplied together they give the "sensitivity"
    (4) "gain" is actually the A0 normalisation factor, the factor that defines the amplitude of pole-zero
         curve at 1 Hz.

    N.B. In most case using the poles and zeros is sufficient for instrument response
    removal, unless you are working close to the NYQUIST frequency, in which case the
    effects of the FIR filters can become more important. The FIR filter can cause:
    -Slight rippling (in amplitude) near Nyquist frequency
    -Acausal ringing for sharp onsets (ringing is at frequencies near Nyquist)

    '''
    for tr in st :
        tr.detrend('demean')
        tr.detrend('linear')
    st.simulate(paz_remove=pz,remove_sensitivity=True,
                    pre_filt=response_prefilt,paz_simulate=None,
                    taper=True, taper_fraction=0.01)
    return st


def get_pazdictfrominventory(inventory,tr):
    ''' Reads an obspy station inventory object and
    for a given trace returns the obspy paz dictionary   

    Obspy pole-zero dictionaries
    (1) "poles" should be a list of tuples, e.g. [(x+yj),(r+sj)]
    (2) "zeros" should be a list of complexes, e.g. [0j,0j],
    (3) "sensitivity" is the total sensitivity and is used if remove_sensitivity=true 
        "digitizer gain" and "seismometer gain" are floats but are passive and there for reference. 
         Multiplied together they give the "sensitivity"
    (4) "gain" is actually the A0 normalisation factor, the factor that defines the amplitude of pole-zero
         curve at 1 Hz.
     '''
    inv=inventory.get_response(tr.id,tr.stats.starttime)
    polezerostage=inv.get_paz()
    totalsensitivity=inv.instrument_sensitivity
    pzdict={}
    pzdict['poles']=polezerostage.poles
    pzdict['zeros']=polezerostage.zeros
    pzdict['gain']=polezerostage.normalization_factor
    pzdict['sensitivity']=totalsensitivity.value
    return pzdict


def read_sacpzfile(file):
    ''' Reads a sac format poles-zero file
    Expects ZEROS, POLES and CONSTANT as keywords
    Returns a paz dictionary  
    Gain is set to 1. 
    Sensitivity is set to CONSTANT 

    Obspy pole-zero dictionaries
    (1) "poles" should be a list of tuples, e.g. [(x+yj),(r+sj)]
    (2) "zeros" should be a list of complexes, e.g. [0j,0j]
    (3) "sensitivity" is the total sensitivity and is used if remove_sensitivity=true 
        "digitizer gain" and "seismometer gain" are floats but are passive and there for reference. 
         Multiplied together they give the "sensitivity"
    (4) "gain" is actually the A0 normalisation factor, the factor that defines the amplitude of pole-zero
         curve at 1 Hz.

     '''
    from obspy.core import UTCDateTime
    fid=open(file)
    instpaz={'gain':1.}
    Z=False
    P=False
    zeros=[];poles=[]
    for line in fid:
        line=line.rstrip()
        line=line.split()
        if line[0] == 'CONSTANT':
            instpaz['sensitivity']=float(line[1])
            continue
        if line[0] == 'ZEROS':
            numofZ=int(line[1])
            Z=True
            zcount=0
            continue
        if Z:
            zeros.append(complex(float(line[0]),float(line[1])))
            zcount+=1
            if zcount == numofZ:
                Z=False
                instpaz['zeros']=zeros
        if line[0] == 'POLES':
            numofP=int(line[1])
            P=True
            pcount=0
            continue
        if P:
            poles.append(complex(float(line[0]),float(line[1])))
            pcount+=1
            if pcount == numofP:
                P=False
                instpaz['poles']=poles
    fid.close()
    return instpaz
