import numpy as np
import pro_utils
import os
import time
import SP_utils
import subprocess
from dill import Pickler, Unpickler
import shelve
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
import smrt_utils
import track_utils
import logging
import datetime


#########################################################################################

def SP_LG(track_no,
          config):
    year = config.year  # Choose a year
    tmp_dir = config.tmp_dir  # Location of temp hard disk location - if used
    model_name = config.snow_model.lower()

    ###################################################################################

    # Model code below, do not modify

    hard_stop_date = datetime.date(year=year + 1,
                                   month=5,
                                   day=1)

    if config.use_RAM:
        tmp_dir = config.ram_dir

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    logging.info(f'Track Number: {track_no}')

    # Now create a .smet file of reanalysis and return a track object

    my_track = track_utils.create_met_file(year=year,
                                           track_no=track_no,
                                           stop_date=hard_stop_date,
                                           tmp_dir=tmp_dir,
                                           aux_dir=config.aux_data_dir,
                                           model_name=model_name)

    if my_track.valid_data == False:
        # If false, it means you probably have a 'summer track'
        logging.info(f'No relevant data for track {track_no}')
        my_track.duration = np.nan

    else:

        try:

            logging.debug(f'Track dates: {my_track.info["start_date"]} : {my_track.info["end_date"]}')

            if model_name == 'snowpack':

                SP_utils.create_sno_file(start_date=my_track.info['start_date'],
                                         start_loc=my_track.info['start_coords'],
                                         track_no=track_no,
                                         tmp_dir=tmp_dir,
                                         aux_dir=config.aux_data_dir)

                SP_utils.create_ini_file(track_no=track_no,
                                         tmp_dir=tmp_dir,
                                         aux_dir=config.aux_data_dir)

            ###################################################################################

            # Run SNOWPACK

            my_track = SP_utils.run_model(model_name,
                                          my_track,
                                          tmp_dir=tmp_dir,
                                          track_no=track_no)

            if model_name == 'snowpack':

                snowpro_list = pro_utils.read(track_no, tmp_dir)  # Read the .pro file into a profile object

                # Prep media for SMRT to operate on if required

                ##########################################################################################

                if config.save_media_list or (not config.block_smrt):

                    mediums_list = [smrt_utils.prep_medium(snowpro, my_track.info['ice_type']) for snowpro in snowpro_list]

                    if config.save_media_list:
                        # Shelve the list of objects under the track_no
                        shelf_dir = f"{config.output_dir}{config.media_f_name}_{year}"

                        with shelve.open(shelf_dir, 'c') as d:
                            d[str(track_no)] = mediums_list

                # Run SMRT on the list of media

                if not config.block_smrt:

                    try:

                        start_timer = time.time()  # Baseline for timing the SMRT run

                        smrt_res = smrt_utils.run_media_series(mediums_list,
                                                               [19e9, 37e9],
                                                               pol=['V', 'H'],
                                                               parallel=config.parallel_SMRT)
                        end_timer = time.time()

                        logging.debug(f'time to run SMRT: {int(end_timer - start_timer)} s')

                    except Exception as e:
                        print(e)
                        smrt_res = None

                else:
                    smrt_res = None

            else:
                smrt_res = None

            # Process results
            if model_name == 'snowpack':

                results = smrt_utils.process_results(snowpro_list, smrt_res, [19e9, 37e9])
                results['coords'] = my_track.frame['track_coords']

            else:
                results = my_track.output

            # Save the results

            results.to_hdf(f'{config.output_dir}{config.results_f_name}{year}.hdf5', key=f't_{track_no}', mode='a')

            if config.make_spro == True:
                os.system(f'mv {tmp_dir}/{track_no}_SPLG.pro SP_LG_Output/{track_no}.pro')
                pro_utils.pro_stripper(track_no)

        except Exception as e:
            logging.exception(f'{track_no}')
            my_track.duration = np.nan

        if config.delete and (model_name == 'snowpack'):
            deletion_list = [f'{track_no}_SPLG.haz',
                             f'{track_no}_SPLG.ini',
                             f'{track_no}_SPLG.sno',
                             f'{track_no}_SPLG.pro',
                             f'config_{track_no}.ini',
                             f'track_{track_no}.smet']

            with open(f'{config.output_dir}{config.log_f_name}', 'ab') as log:
                for file in deletion_list:
                    cleaner_command = ['rm', f'{file}']
                    subprocess.call(cleaner_command,
                                    cwd=f'{tmp_dir}',
                                    stderr=log)

    return my_track.duration