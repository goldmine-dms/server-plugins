import numpy

from goldmine.controller import *
from goldmine.utils import nantonone



@apimethod
def spans_to_time(depth, time):
    """
        Put discrete data on timescale

        depth:              sequence of depth values
        time:               sequence of time values
        nan_threshold:      the fraction of samples needed to return a non-nan 
                            value from the interval
        nan_ignore:         ignore nans

        Based on Sune Olander Rasmussen 23 March 2006 data_on_timescale.m
        which in turn is based on resampling code from Bo M. Vinther

    """
    
    ## Check consistency

    if depth["columns"] != 2:
        raise TypeError("depth must be specified with two columns of data")

    if time["columns"] != 2:
        raise TypeError("time must be specified with two columns of data")

    if depth["sequence"]["index_marker_type"] != "span":
        raise TypeError("depth must be a spanning sequence")

    if time["sequence"]["index_marker_type"] != "point":
        raise TypeError("time must be a point sequence")


    depthdata = numpy.asarray(depth["data"])
    timedata = numpy.asarray(time["data"])

    M = depth["rows"]
    N = time["rows"]-1

    output = numpy.zeros((N, 3))
    output[:,0] = timedata[1:, 0]     
    output[:,1] = timedata[1:, 1]  

    minj = 0
    maxj = 0

    for i in range(N):

        # find first data sample in time interval
        for j in range(minj, M):
            if timedata[i, 0] < depthdata[j, 0]:
                minj = j
                break

        for j in range(minj, M):
            if timedata[i+1, 0] <= depthdata[j, 0]:
                maxj = j
                break

        mm = maxj-minj+1 #number of samples in the time interval

       # FIXME, if time starts before data or the reverse
       # if minj == maxj and minj == 0:
       #     output[i, 2] = numpy.nan
       #     continue

        dz = numpy.zeros((mm, 1))

        # FIXME: ignore nan stuff

        dz[0] = depthdata[minj, 0] - timedata[i, 0]
        for j in range(1, mm-1):
            dz[j] = depthdata[minj+j, 0] - depthdata[minj+j-1, 0]

        dz[mm-1] = timedata[i+1, 0] - depthdata[maxj-1, 0]

        DZ = numpy.sum(dz) #FIXME nan stuff

        for j in range(mm):
            val = (dz[j] * depthdata[minj+j, 1]) / DZ;
            output[i, 2] += val

    lst = nantonone(output.tolist())
    time["data"] = lst
    time["current_parameters"].append(depth["current_parameters"][0])
    print depth.keys()
    return time