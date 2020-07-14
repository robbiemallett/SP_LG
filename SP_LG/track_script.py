import numpy as np
import os
from dill import Pickler, Unpickler
from snow_models.run_snow_model import run_model
import shelve
from microwave_models.run_micro_model import run_mic_mod
import traceback
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
from make_met_forcing import track_utils
import logging
import datetime

#########################################################################################

def SP_LG(track_no,
          config):

    """ Manages the running of an individual track

    Args:
        track_no: track number (int)
        config: instance of config class with model run parameters

    Returns:
        float: Duration of snow model run

    #TODO set up to time microwave model run
    #TODO there's nice traceback error handling here, can this be included in the error class?

    """

    year = config.year  # Choose a year
    tmp_dir = config.tmp_dir  # Location of temp hard disk location - if used

    ###################################################################################

    # Model code below, do not modify
    if config.hemisphere == 'n':
        hard_stop_date = datetime.date(year=year + 1,
                                       month=4,
                                       day=31)
    elif config.hemisphere == 's':
        hard_stop_date = datetime.date(year=year,
                                       month=9,
                                       day=30)
    else: raise

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    logging.info(f'Track Number: {track_no}')

    # Now create a .smet file of reanalysis and return a track object


    my_track = track_utils.create_met_forcing(config=config,
                                              track_no=track_no,
                                              stop_date=hard_stop_date)

    if my_track.valid_data == False:
        # If false, it means you probably have a 'summer track'
        logging.info(f'No relevant data for track {track_no}')
        my_track.duration = np.nan

    else:

        try:

            logging.debug(f'Track dates: {my_track.info["start_date"]} : {my_track.info["end_date"]}')

            ###################################################################################

            # Run model


            my_track = run_model(my_track,
                                 config)

            if config.run_smrt:

                my_track = run_mic_mod(my_track,
                                                config)


            my_track.output['coords'] = my_track.frame['track_coords']

            my_track.output.to_hdf(f'{config.output_dir}/{year}{config.output_f_name}',
                                    key=f't_{track_no}',
                                    mode='a')

        except Exception as e:
            # print(config.log_f_name)
            traceback.print_exc(file=None)
            logging.debug(e)
            my_track.duration = np.nan

    return my_track.duration