"""
Module containing functions for manipulating dispersion datasets
"""
import numpy as np
from greentools.core import create_path
import os
import matplotlib.pyplot as plt

def qc_disp_curves(disp_dict,df,instrument_min_freq_func,no_lambda=2,min_travel_time=0):
    """ Quality control of dispersion dictionary of dispersion curves


    :param disp_dict: All dispersion curves in dictionary where keys are
                    the count index. Each entry is a dictionary 
                    containing the dispersion data. The vital fields 
                    contained within this are:
                    ['freq'],['time'],['dist']['name'] and all others 
                    are for reference. 
                    ['name'] is a string in format STA1_STA2_CHN1_CHN2
                    ['freq'] must be an array of increasing value for 
                    correct interpolation. 
                    ['interp_freqs'],['interp_times'] are added to 
                    disp_dict by function sort_by_period()
    :type disp_dict: Dictionary
    :param df: Dataframe of measurement run, needed for pair info
    :type df: pandas.core.frame.DataFrame
    :param instrument_min_freq_func: Custom function which takes (NET,STA) 
                    as input and returns a float FREQ.
    :type instrument_min_freq_func: ~function
    :param no_lambda: Number of wavelengths for longest period limit
    :type no_lambda: float or int
    :param min_travel_time: Minimum travel time of picks to limit
    :type min_travel_time: float or int
    :param return:  All dispersion curves limited by instrument qc, min 
                    wavelength criteria, and min travel time limit
    :type return: dictionary
    """
    if not 'df' in locals() :
        raise Exception("Requires measured pairs dataframe as variable df")
    try :
        if not callable(instrument_min_freq_func):
            raise Exception("The function instrument_min_freq is not callable")
    except:
        raise Exception("Requires a loaded function named instrument_min_freq")

    for count in disp_dict.keys():

        ddict=disp_dict[count]
        nstr=ddict['name']

        pair_info=df[df['name']==nstr]
        pair_info=pair_info.loc[pair_info.index[0]]
        dist=float(pair_info['dist'])

        # Find the lowest min frequency for sensor type
        net1,net2=pair_info['network'].split('-')
        sta1,sta2=pair_info['station'].split('-')
        f1=instrument_min_freq_func(net1,sta1)
        f2=instrument_min_freq_func(net2,sta2)
        sensor_min_freq=np.amax([f1,f2])
        mask1=ddict['freq']<sensor_min_freq
        if mask1.any():
            print("sensor type limits applied to "+pair_info['station'])

        # Calculate limits from pair separation
        dist=pair_info['dist']
        # if x wavelengths are greater than the dist, then obs is removed
        mask2=float(no_lambda)*((ddict['dist']/ddict['time'])/ddict['freq']) > dist
        if mask2.any():
            print("Pair separation limits applied to "+pair_info['station'])

        # Calculate a min travel time for the pick
        mask3=ddict['time']<float(min_travel_time)

        # Check vital fields of disp curve have the same length
        vital=[ddict[x] for x in ['time','freq','dist']]
        if not len(set(map(len,vital))) == 1 :
            print("Dispersion data has different lengths")
            print("for the fields time,freq,dist")
            raise Exception()

        # Apply limit mask to all disp curve fields
        removemask=mask1+mask2+mask3
        if removemask.any() :
            for ke in ddict.keys():
                if ke=='name' :
                    continue
                ddict[ke]=ddict[ke][np.invert(removemask)]

        # Re-apply dispersion curve to overall dictionary
        disp_dict[count]=ddict
        if len(disp_dict[count]['freq'])<2 :
            del disp_dict[count]

    return disp_dict


def sort_by_period(disp_dict,df):
    """ Takes dispersion dictionary and produces a dictionary
    of all the observations interpolated onto desired periods
    :param disp_dict: All dispersion curves in dictionary where keys are
                    the count index. Each entry is a dictionary 
                    containing the dispersion data. The vital fields 
                    contained within this are:
                    ['freq'],['time'],['dist']['name'] and all others 
                    are for reference. 
                    ['name'] is a string in format STA1_STA2_CHN1_CHN2
                    ['freq'] must be an array of increasing value for 
                    correct interpolation. 
    :type disp_dict: dictionary
    :param df: Dataframe of measurement run, needed for pair info
    :type df: pandas.core.frame.DataFrame
    :return periods_dict: dictionary of travel times sorted by period
    :rtype : dictionary

    The ONLY fields used are 'time','dist','freq' from disp_dict
    Any other fields are for reference or book-keeping.
    Entrys in periods_dict are:
        travel-time,distance,lat1,lon1,el1,lat2,lon2,el2
    """

    # Loop through dispersion curves and interpolate onto desired periods
    wanted_periods=np.hstack([np.arange(1,10,0.5),np.arange(10,31,1)])[::-1]
    print "Interpolating onto periods: \n %s" % wanted_periods
    for k in disp_dict.keys():
        # Set the full range of periods to try and find
        interp_periods=wanted_periods.copy()
        interp_freqs=1./interp_periods
        # N.B. Order must be increasing for interp. Maybe use [::-1]
        # Arrival time of each picked point
        f,t=disp_dict[k]['freq'],disp_dict[k]['time']
        # Remove interp_freqs outside datarange
        delindices=[]
        for i in range(0,len(interp_freqs)) :
            if (interp_freqs[i] < np.min(f)) or (interp_freqs[i] > np.max(f)) :
                delindices.append(i)
        interp_freqs=np.delete(interp_freqs,delindices)
        # If dispersion curve contains no desired freqs, delete it.
        if len(interp_freqs)<1:
            del disp_dict[k]
            continue

        # Find interpolated time values for given frequencies
        interp_times=np.interp(interp_freqs,f,t)
        interp_vels=disp_dict[k]['dist'][0]/interp_times

        # Check the dispersion curves were prepared correctly
        if disp_dict[k]['freq'][0]>disp_dict[k]['freq'][-1] :
            raise Exception("Frequency should be increasing array in disp dict")

        # Checks if the freq-array is always increasing (not always with inst freq).
        # Print figures for inspection on disp curves that are not.
        if np.any(f!=sorted(f)) :
            plt.plot(f,t,'-b',label='raw picks')
            plt.plot(interp_freqs,interp_times,'r.',label='interpolated')
            plt.xlabel('freq (Hz)')
            plt.ylabel('time (s)')
            create_path('ALERT_FIGS')
            plt.title(disp_dict[k]['name'])
            plt.savefig('ALERT_FIGS/'+disp_dict[k]['name']+'.png')
            plt.close()

        # Add information to dispersion dictionary
        disp_dict[k]['interp_freqs']=interp_freqs
        disp_dict[k]['interp_periods']=1./interp_freqs
        disp_dict[k]['interp_vels']=interp_vels
        disp_dict[k]['interp_times']=interp_times

    try :
        alert_no=len(os.listdir('ALERT_FIGS'))
        print("**********")
        print(" Warning: %s dispersion curves had a decrease in freq at some point" % alert_no)
        print(" check the interpolation with figures in ALERT_FIGS")
        print("**********")
    except :
        pass

    # Sort into dictionary of observations at desired period
    periods_dict={}
    for per in wanted_periods :
        periods_dict[per]=[]
        for k in disp_dict.keys():
            df_row=df[df['name']==disp_dict[k]['name']]
            # Get the vel for that period from each disp curve
            time=disp_dict[k]['interp_times'][disp_dict[k]['interp_periods']==per]
            if len(time)==1 :
                periods_dict[per].append(list(time)+list(df_row[['dist','lat_1','lon_1','el_1','lat_2','lon_2','el_2']].values[0]))

    # Look at the min max vels for each periods
    for per in sorted(periods_dict.keys()) :
        if len(periods_dict[per])<1 :
            continue
        vels=np.array(periods_dict[per])[:,1]/np.array(periods_dict[per])[:,0]
        print "Period: %f s, min %f max %f stddev %f" % (per,np.min(vels),np.max(vels),np.std(vels))

    return periods_dict


def ivan_tomo_input(periods_dict,outdir,output_periods,df):
    """ 
    Write out files for Ivan Koulakov's linear inversion code from the
    periods dictionary
    
    :param periods_dict: dictionary of travel times sorted by period
    :type periods_dict : dictionary
    :param outdir: Output directory for the data text files
    :type outdir: string
    :param output_periods: The desired periods to output results for
    :type output_periods: list or array of floats
    :param df: Dataframe of measurement run, needed for station info
    :type df: pandas.core.frame.DataFrame
    """
    # Ray files
    raydir=os.path.join(outdir,'rays')
    create_path(raydir)
    p_fid=open(os.path.join(outdir,'periods.dat'),'wa')
    n=01
    for per in sorted(output_periods) :
        print "Period %f no of measurements  %i " % (per,len(periods_dict[per]))
        if len(periods_dict[per])<1 :
            continue
        fid=open(os.path.join(raydir,"rays"+str("%02.f" % n)+'.dat'),'wa')
        for l in periods_dict[per] :
            outline=" ".join(np.array([l[2],l[1],l[3],l[5],l[4],l[6],l[0]],dtype=np.str))+"\n"
            out=[l[2],l[1],l[3],l[5],l[4],l[6],l[0]]
            outline="%8.4f %8.4f %6.1f %8.4f %8.4f %6.1f %8f\n" % tuple(out)
            fid.write(outline)
        fid.close()
        n+=1
        p_fid.write(str(per)+"\n")
    p_fid.close()
    # period/station files
    stadict={}
    for l in df[['station','lat_1','lon_1','el_1']].values :
        stadict[l[0].split("-")[0]]=l[1:]
    for l in df[['station','lat_2','lon_2','el_2']].values :
        stadict[l[0].split("-")[1]]=l[1:]
    sta_fid=open(os.path.join(outdir,"stations.dat"),'wa')
    arr=np.array(stadict.values())
    for ol in arr[:,(1,0,2)]:
        sta_fid.write("%8.4f %8.4f %6.1f" % tuple(ol)+"\n")
    sta_fid.close()
    return


def tilmann_tomo_input(disp_dict,periods,outdir,df):
    """
    Write files for Frederik's  mcmc matlab code from disp dictionary
    Produces:
    data_array of dimensions num-disp_curves (cont), by num periods (data.txt)
    periods array (periods.txt)
    distance_array 
    station index array (si.txt)
    receiver index array (ri.txt)
    write stations.txt file and use gmt project and awk to convert
    stalat array --> stay array
    stalon array --> stax array
    stael array --> staz array

    :param disp_dict: All dispersion curves in dictionary where keys are
                    the count index. Each entry is a dictionary 
                    containing the dispersion data. The vital fields 
                    contained within this are:
                    ['freq'],['time'],['dist']['name'] and all others 
                    are for reference. 
                    ['name'] is a string in format STA1_STA2_CHN1_CHN2
                    ['freq'] must be an array of increasing value for 
                    correct interpolation. 
    :type disp_dict: dictionary
    :param periods: The desired periods to output results for
    :type periods: list or array of floats
    :param outdir: Output directory for the data text files
    :type outdir: string
    :param df: Dataframe of measurement run, needed for station info
    :type df: pandas.core.frame.DataFrame
    """
    print("Writing text files to %s" % outdir)
    create_path(outdir)
    # clean disp_dict of entrys with no interp_i_periods
    for i in disp_dict.keys() :
        if len(disp_dict[i]['interp_periods']) == 0 :
            del disp_dict[i]

    # Sta dictionary
    stadict={}
    for l in df[['station','lat_1','lon_1','el_1']].values :
        stadict[l[0].split("-")[0]]=l[1:]
    for l in df[['station','lat_2','lon_2','el_2']].values :
        stadict[l[0].split("-")[1]]=l[1:]
    stalist=sorted(stadict.keys())

    # Print a station file:
    ofid=open(os.path.join(outdir,"stations.lonlat"),'wa')
    for s in stalist :
        lat,lon,el=stadict[s]
        ofid.write("%s %s %s %s\n" % (s,lon,lat,el))
    ofid.close()

    # Convert that station file to cartesian using the
    # gmt script, and awk out each column separately to a txt file
    data_array=np.zeros([len(disp_dict.keys()),len(periods)])
    station_ind=np.zeros([len(disp_dict.keys())],)
    receiver_ind=np.zeros([len(disp_dict.keys())],)
    distances=np.zeros([len(disp_dict.keys())],)

    for k,d in enumerate(sorted(disp_dict.keys())):
        pair_info=df[df['name']==disp_dict[d]['name']]
        disp_pers=disp_dict[d]['interp_periods']
        disp_times=disp_dict[d]['interp_times']
        # Add vel for each period to data array
        for j,p in enumerate(periods) :
            time=disp_times[disp_pers==p]
            if len(time)>0 :
                data_array[k,j]=time
            else :
                data_array[k,j]=np.nan

        # Add the station and receiver index (for sta x,y,names list)
        sta1,sta2=pair_info['station'].values[0].split('-')
        station_ind[k]=stalist.index(sta1)+1 # Matlab indices start at 1
        receiver_ind[k]=stalist.index(sta2)+1 # Matlab indices start at 1
        # Add the separation distance
        distances[k]=disp_dict[d]['dist'][0]
    # Write ascii files to later be read to matlab format by prepare_data.m
    np.savetxt(os.path.join(outdir,"periods.txt"),periods)
    np.savetxt(os.path.join(outdir,"data.txt"),data_array)
    np.savetxt(os.path.join(outdir,"ri.txt"),receiver_ind)
    np.savetxt(os.path.join(outdir,"si.txt"),station_ind)
    return
