import numpy as np
from track_script import SP_LG
import psutil
import time
import logging

def CL_parse(arguments):

    if '-hpc' in arguments: hpc = True
    else: hpc = False

    start_track = arguments[0]
    end_track = arguments[1]
    spacing = arguments[2]

    return_dict = {'start':start_track,
                   'end':end_track,
                   'spacing':spacing,
                   'hpc':hpc}

    return(return_dict)


def multi_track_run(tracks_to_run,
                    run_dict,
                    temp_control=True):

    SNOWPACK_TIMER = []  # a list recording the duration of every SNOWPACK run.

    for track_no in tracks_to_run:

        if temp_control:                    # Hold iteration if cores too hot
            while dangerous_temp():
                time.sleep(3)

        x = SP_LG(track_no,
                  run_dict)

        if not np.isnan(x):
            SNOWPACK_TIMER.append(x)

    mean_time = np.nanmean(SNOWPACK_TIMER)
    attempted_runs = len(list(tracks_to_run))
    achieved_runs = len(SNOWPACK_TIMER)

    return_dict = {'mean_time' : mean_time,
                    'attempted_runs' : attempted_runs,
                    'achieved_runs' : achieved_runs}

    logging.critical(f'Run stats: {return_dict}')

    return(return_dict)

def dangerous_temp():
    temps =  psutil.sensors_temperatures()['coretemp']
    too_hot = False
    for i in temps:
        if i[1] > 70:
            too_hot = True

    return(too_hot)