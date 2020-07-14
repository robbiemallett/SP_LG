from tqdm import trange
from dill import Pickler, Unpickler
import shelve
import tqdm
import pickle
shelve.Pickler = Pickler
from misc.calibration_tools.pass_custom_list import OIB_intersection_tracks
shelve.Unpickler = Unpickler
import logging
import datetime
import sys
import os
from config.config_cls import merge
from make_met_forcing.multi_track_utils import CL_parse, multi_track_run


#####################################################################

if __name__ == '__main__':

    if len(sys.argv) == 1: # Code is being run from the editor in test mode

        CL_input =        {'start':500,
                           'end':501,
                           'spacing':1,
                           'hpc':False}
    else:

        CL_input = CL_parse(sys.argv)

    # CONFIGURATION

    machine_config = pickle.load(open('config/desktop.cfg', 'rb'))
    run_config = pickle.load(open('config/run.cfg', 'rb'))
    config = merge(run_config, machine_config, ['aux_data_dir',
                                                'tmp_dir',
                                                'output_dir',
                                                'tracks_dir',
                                                'hpc_run'])



    if config.hpc_run:
        config.tmp_dir = os.getcwd()

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