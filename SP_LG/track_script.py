import numpy as np
import os
from dill import Pickler, Unpickler
from snow_models.run_snow_model import run_model
import shelve
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
from microwave_models.run_micro_model import run_micro_model
from make_met_forcing import track_utils
import logging
import datetime

#########################################################################################

def SP_LG(track_no,
          config):

    year = config.year  # Choose a year
    tmp_dir = config.tmp_dir  # Location of temp hard disk location - if used
    model_name = config.model_name.lower()

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

    my_track = track_utils.create_met_forcing(year=year,
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

            ###################################################################################

            # Run model


            my_track = run_model(my_track,
                                 config)

            if config.microwave_model:

                my_track = run_micro_model(my_track,
                                                config)


            my_track.output['coords'] = my_track.frame['track_coords']

            my_track.output.to_hdf(f'{config.output_dir}{config.results_f_name}{year}.hdf5',
                                    key=f't_{track_no}',
                                    mode='a')

        except Exception as e:
            print(e)
            my_track.duration = np.nan

    return my_track.duration