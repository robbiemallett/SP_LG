import numpy as np
import psutil
import multiprocessing
import pro_utils
import os
import time
import SP_utils
import subprocess
from tqdm import trange
from dill import Pickler, Unpickler    # Necessary to store the SMRT objects for later analysiss
import shelve
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
import smrt_utils
import track_utils
import logging
import datetime
from track_script import SP_LG
import psutil
import time

# Choose tracks to run, must be an iterator

# tracks_to_run = [1151]
tracks_to_run = [200]
# tracks_to_run = trange(1, 55_000, 3000)

def dangerous_temp(cores):
    temps =  psutil.sensors_temperatures()['coretemp']
    too_hot = False
    for i in temps:
        if i[1] > 70:
            too_hot = True

    return(too_hot)



def multi_track_run(tracks_to_run,
                    log_f_name=f'SP_LG_Output/core',  # Set file name of log file
                    log_level = logging.DEBUG,
                    core=0,
                    temp_control=True):

    log_f_name = log_f_name + f'_{core}.log'

    logging.basicConfig(level=log_level,
                        filename=log_f_name)

    logging.critical(f'Start time: {str(datetime.datetime.now())}')
    print(f'Start time: {str(datetime.datetime.now())}')

    SNOWPACK_TIMER = []  # a list recording the duration of every SNOWPACK run.

    for track_no in tracks_to_run:

        if temp_control:                    # Hold iteration if cores too hot
            while dangerous_temp(cores):
                time.sleep(0.5)

        ######################################################

        x = SP_LG(track_no,
                  results_f_name=f'Core_{core}_',
                  save_media_list=True,
                  media_f_name=f'Core_{core}_med',
                  use_RAM=True)

        ######################################################

        if not np.isnan(x):
            SNOWPACK_TIMER.append(x)

    logging.critical(f'End time: {str(datetime.datetime.now())}')
    print(f'Core {core} End time: {str(datetime.datetime.now())}')
    print(f'Core {core} Mean time = {np.nanmean(SNOWPACK_TIMER)}')
    print(f'Core {core} Successful runs = {len(SNOWPACK_TIMER)}/{len(list(tracks_to_run))}')



# multi_track_run(tracks_to_run)

cores = 5
processes = []
for core in range(cores):

    p = multiprocessing.Process(target = multi_track_run,
                                # args = [[200]],
                                args=(trange(core, 10000, cores),),
                                kwargs={'core':core})

    p.start()

    processes.append(p)

for p in processes:
    p.join()

