import numpy as np
# import pandas as pd
import multiprocessing
# import pro_utils
# import os
from SP_utils import dangerous_temp
# import time
# import SP_utils
# import subprocess
# import h5py
from tqdm import trange
from dill import Pickler, Unpickler
import shelve
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
# import smrt_utils
# import track_utils
import logging
import datetime
from track_script import SP_LG
import psutil
import time


#####################################################################

# CONFIGURATION
grace_run = False
cores = 1
log_f_name = 'log.txt'
ram_dir = '/dev/shm/SP'
use_RAM = True
save_media_list = True
log_level=logging.WARNING

if grace_run:
    tmp_dir = '/home/ucfarm0/Scratch'
    aux_data_dir = '/home/ucfarm0/SP_LG/aux_data/'
    output_dir = '/home/ucfarm0/Scratch/'
else:
    tmp_dir = '/home/robbie/Dropbox/SP_LG/Snowpack_files'
    aux_data_dir = '/home/robbie/Dropbox/Data/for_grace/'
    output_dir = "/home/robbie/Dropbox/SP_LG/SP_LG_Output/"

######################################################################

def multi_track_run(tracks_to_run,
                    core=0,
                    temp_control=True):

    SNOWPACK_TIMER = []  # a list recording the duration of every SNOWPACK run.

    for track_no in tracks_to_run:

        if temp_control:                    # Hold iteration if cores too hot
            while dangerous_temp():
                time.sleep(3)

        ######################################################

        x = SP_LG(track_no,
                  ram_dir=ram_dir,  # Location of ram directory
                  tmp_dir=tmp_dir,  # Location of temp hard disk location
                  results_f_name=f'Core_{core}_',
                  save_media_list=save_media_list,
                  log_f_name = log_f_name,
                  media_f_name=f'Core_{core}_med',
                  aux_dir=aux_data_dir,
                  output_dir=output_dir,
                  use_RAM=use_RAM)

        ######################################################

        if not np.isnan(x):
            SNOWPACK_TIMER.append(x)

    mean_time = np.nanmean(SNOWPACK_TIMER)
    attempted_runs = len(list(tracks_to_run))
    achieved_runs = len(SNOWPACK_TIMER)

    return_dict = {'mean_time' : mean_time,
                    'attempted_runs' : attempted_runs,
                    'achieved_runs' : achieved_runs}

    logging.critical(f'Core {core}: {return_dict}')

    return(return_dict)

############################################################

logging.basicConfig(level=log_level,
                    filename=f'{output_dir}{log_f_name}')

logging.critical(f'Start time: {str(datetime.datetime.now())}')





processes = []

for core in range(cores):

    p = multiprocessing.Process(target = multi_track_run,
                                args= (trange(core+200, 205, cores),),
                                kwargs={'core':core})

    p.start()

    processes.append(p)

for p in processes:
    p.join()

logging.critical(f'End time: {str(datetime.datetime.now())}')


#
#
# year = 2016
# for core in trange(cores):
#
#     with h5py.File(f'SP_LG_Output/Core_{core}_{year}.hdf5', 'r') as f:
#
#         track_keys = list(f.keys())
#
#     for key in track_keys:
#         data = pd.read_hdf(f'SP_LG_Output/Core_{core}_{year}.hdf5', key=key, mode='r')
#         data.to_hdf(f'SP_LG_Output/Cores_combined_{year}.hdf5', key=key, mode='a')