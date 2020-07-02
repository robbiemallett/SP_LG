from tqdm import trange
from dill import Pickler, Unpickler
import shelve
import tqdm
shelve.Pickler = Pickler
import types
from misc.calibration_tools.pass_custom_list import OIB_intersection_tracks
shelve.Unpickler = Unpickler
import logging
import datetime
import sys
import os
from make_met_forcing.multi_track_utils import CL_parse, multi_track_run


#####################################################################

if __name__ == '__main__':
    if len(sys.argv) == 1: # Code is being run from the editor in test mode

        CL_input =        {'start':200,
                           'end':210,
                           'spacing':1,
                           'hpc':False}
    else:

        CL_input = CL_parse(sys.argv)

    # CONFIGURATION

    config = types.SimpleNamespace() #Makes an empty object

    config.hpc_run = CL_input['hpc']
    config.year = 2016
    config.log_f_name = 'log.txt'
    config.custom_input_list = True
    config.ram_dir = '/dev/shm/SP'
    config.delete=True
    config.use_RAM = False
    config.log_level=logging.DEBUG
    config.model_name = 'degree_days' # can be 'snowpack', 'degree_days' or 'nesosim'
    config.results_f_name = 'result'
    config.make_spro = False
    config.microwave_model = False
    config.micro_model_name = 'SMRT'
    config.save_micro_input = False
    config.run_micro_input = False
    config.media_f_name = 'media'
    config.frequencies = [19e9, 37e9]

    if config.hpc_run:
        config.tmp_dir = os.getcwd()
        config.aux_data_dir = '/home/ucfarm0/SP_LG/aux_data/'
        config.tracks_dir = '/home/ucfarm0/SP_LG/tracks/'
        config.output_dir = '/home/ucfarm0/Scratch/'
        config.use_RAM = False
        config.parallel_SMRT=False

    else:
        config.tmp_dir = '/home/robbie/Dropbox/SP_LG/Snowpack_files'
        config.aux_data_dir = '/home/robbie/Dropbox/Data/SP_LG_aux_data/'
        config.output_dir = "/home/robbie/Dropbox/SP_LG/SP_LG_Output/"
        config.tracks_dir = "/home/robbie/Dropbox/SP_LG/tracks/"

    ######################################################################

    logging.basicConfig(level=config.log_level,
                        filename=f'{config.output_dir}{config.log_f_name}')

    start_time = str(datetime.datetime.now())

    if config.custom_input_list:
        custom_list = OIB_intersection_tracks(config.year + 1)
        logging.warning(f'number of custom tracks: {len(custom_list)}')
        iterator = tqdm.tqdm(custom_list)

    else:
        iterator = trange(CL_input['start'],
                         CL_input['end'],
                         CL_input['spacing'])

    multi_track_run(tracks_to_run=iterator,
                    config=config,
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