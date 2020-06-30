from tqdm import trange
from dill import Pickler, Unpickler
import shelve
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
import logging
import datetime
import sys
import os
from multi_track_utils import CL_parse, multi_track_run


#####################################################################


if len(sys.argv) == 1: # Code is being run from the editor in test mode

    CL_input =        {'start':200,
                       'end':220,
                       'spacing':1,
                       'hpc':False}

else:

    CL_input = CL_parse(sys.argv)

# CONFIGURATION

hpc_run = CL_input['hpc']
year = 2016
log_f_name = 'log.txt'
ram_dir = '/dev/shm/SP'
block_smrt=False
delete=True
use_RAM = False
save_media_list = False
parallel_SMRT=False
log_level=logging.WARNING
snow_model = 'degree_days' # can be 'snowpack', 'degree_days' or 'nesosim'

if hpc_run:
    tmp_dir = os.getcwd()
    aux_data_dir = '/home/ucfarm0/SP_LG/aux_data/'
    output_dir = '/home/ucfarm0/Scratch/'
    use_RAM = False
    parallel_SMRT=False

else:
    tmp_dir = '/home/robbie/Dropbox/SP_LG/Snowpack_files'
    aux_data_dir = '/home/robbie/Dropbox/Data/SP_LG_aux_data/'
    output_dir = "/home/robbie/Dropbox/SP_LG/SP_LG_Output/"

######################################################################

# Configure run_dict

core = 'results'

run_dict = {
                  'year':year,
                  'ram_dir':ram_dir,  # Location of ram directory
                  'tmp_dir':tmp_dir,  # Location of temp hard disk location
                  'results_f_name':f'{CL_input["start"]}_results',
                  'save_media_list':save_media_list,
                  'log_f_name' : log_f_name,
                  'media_f_name':f'{CL_input["start"]}_media',
                  'aux_dir':aux_data_dir,
                  'block_smrt':block_smrt,
                  'delete':delete,
                  'output_dir':output_dir,
                  'use_RAM':use_RAM,
                  'parallel':parallel_SMRT,
                  'snow_model':snow_model,

                  }

############################################################

logging.basicConfig(level=log_level,
                    filename=f'{output_dir}{log_f_name}')

start_time = str(datetime.datetime.now())


multi_track_run(tracks_to_run=trange(CL_input['start'],
                                     CL_input['end'],
                                     CL_input['spacing']),
                run_dict=run_dict,

                temp_control=False)

logging.critical(f'Start time: {start_time}')
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
#         data.to_hdf(f'SP_LG_Output/Cores_combined_{year}.hdf5', key=key, mode='a')year}.hdf5', key=key, mode='a')