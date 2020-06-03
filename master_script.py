import numpy as np
# import pandas as pd
import multiprocessing
# import pro_utils
# import os
# from SP_utils import dangerous_temp
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
import sys
import os
from multi_track_utils import CL_parse, multi_track_run


#####################################################################

x = os.getcwd()
print(x)

CL_input = CL_parse(sys.argv)

if len(CL_input) == 1: # Code is being run from the editor in test mode

    CL_input =        {'start':200,
                       'end':210,
                       'spacing':1,
                       'hpc':False}

# CONFIGURATION
hpc_run = CL_input['hpc']
year = 2016
log_f_name = 'log.txt'
ram_dir = '/dev/shm/SP'
block_smrt=True
use_RAM = True
save_media_list = True
log_level=logging.DEBUG

if hpc_run:
    # tmp_dir = '/scratch/scratch/ucfarm0'
    tmp_dir = x
    aux_data_dir = '/home/ucfarm0/SP_LG/aux_data/'
    output_dir = '/home/ucfarm0/Scratch/output/'
    use_RAM = False

else:
    tmp_dir = '/home/robbie/Dropbox/SP_LG/Snowpack_files'
    aux_data_dir = '/home/robbie/Dropbox/Data/for_grace/'
    output_dir = "/home/robbie/Dropbox/SP_LG/SP_LG_Output/"

######################################################################

# Configure run_dict

core = 'results'

run_dict = {
                  'year':year,
                  'ram_dir':ram_dir,  # Location of ram directory
                  'tmp_dir':tmp_dir,  # Location of temp hard disk location
                  'results_f_name':f'series_results',
                  'save_media_list':save_media_list,
                  'log_f_name' : log_f_name,
                  'media_f_name':f'series_media',
                  'aux_dir':aux_data_dir,
                  'block_smrt':block_smrt,
                  'delete':True,
                  'output_dir':output_dir,
                  'use_RAM':use_RAM,

                  }

############################################################

logging.basicConfig(level=log_level,
                    filename=f'{output_dir}{log_f_name}')

logging.critical(f'Start time: {str(datetime.datetime.now())}')

multi_track_run(tracks_to_run=trange(CL_input['start'],
                                     CL_input['end'],
                                     CL_input['spacing']),
                run_dict=run_dict,

                temp_control=False)

logging.critical(f'End time: {str(datetime.datetime.now())}')







#
# processes = []
#
# for core in range(cores):
#
#     p = multiprocessing.Process(target = multi_track_run,
#                                 args= (trange(core+200, 202, cores),),
#                                 kwargs={'core':core})
#
#     p.start()
#
#     processes.append(p)
#
# for p in processes:
#     p.join()
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