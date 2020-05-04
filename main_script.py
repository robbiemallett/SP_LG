import numpy as np
import psutil
import time
import pro_utils
import os
import time
from pandas.plotting import register_matplotlib_converters
import SP_utils
import pandas as pd
import dill
from dill import Pickler, Unpickler
from tqdm import trange
import shelve
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
import smrt_utils
import track_utils
from netCDF4 import Dataset
import logging
import datetime

# register_matplotlib_converters()
logging.basicConfig(level=logging.WARNING,
                    filename='overnight.log')
#########################################################################################

# Config

year            = 2016
block_smrt      = False
save_media_list = False
make_spro       = False
single_run      = False

# Choose a date cap to stop simulations running into the melt phase
hard_stop_date = datetime.date(year=year+1, month=5, day=1)

# Choose tracks to run

tracks_to_run = [1151]
# tracks_to_run = trange(1, 55_000, 25)

#########################################################################################

output_dir = "/home/robbie/Dropbox/Modelling/SP_LG/SP_LG_Output/"
results_f_name = '1151'

###################################################################################

# Model code below, do not modify

logging.critical(f'Start time: {str(datetime.datetime.now())}')
print(f'Start time: {str(datetime.datetime.now())}')
SNOWPACK_TIMER = []


for track_no in tracks_to_run:

    # print(f'Track number: {track_no}')
    logging.info(f'Track Number: {track_no}')

    cleaner_string = 'rm -r Snowpack_files/* >nul 2>&1'
    os.system(cleaner_string)

    # Now create a .smet file for the track and a python object for that track

    my_track = track_utils.create_smet_file(year=year,
                                            track_no=track_no,
                                            stop_date=hard_stop_date)



    if my_track.valid_data == False:
        logging.info(f'No relevant data for track {track_no}')
        pass
    else:

        try:

            logging.debug(f'Track dates: {my_track.info["start_date"]} : {my_track.info["end_date"]}')

            SP_utils.create_sno_file(start_date=my_track.info['start_date'],
                                    start_loc = my_track.info['start_coords'],
                                    track_no=track_no)

            logging.debug('Creating configuration .INI file...')

            SP_utils.create_ini_file(track_no=track_no)

            # Run SNOWPACK

            start_timer = time.time()

            SP_utils.run(my_track.info['end_date'],
                         track_no)

            while 'snowpack' in (p.name() for p in psutil.process_iter()):
                time.sleep(0.5)

            end_timer = time.time()

            # print(f'time to run SNOWPACK: {int(end_timer-start_timer)} s')
            SNOWPACK_TIMER.append(int(end_timer-start_timer))

            # Read the .pro file into a profile object

            pro_list = pro_utils.read(track_no)

            # Prep media for SMRT to operate on if required

            if save_media_list or (not block_smrt):

                mediums_list = [smrt_utils.prep_medium(snowpro) for snowpro in pro_list]

                if save_media_list:

                    # Shelve the list of objects under the track_no
                    shelf_dir = f"{output_dir}media_{year}"

                    with shelve.open(shelf_dir, 'c') as d:

                        d[str(track_no)] = mediums_list

                # Run SMRT on the list of media

                if block_smrt == False:

                    print('Running SMRT')

                    start_timer = time.time()

                    smrt_res = smrt_utils.run_media_series(mediums_list,
                                                            [19e9, 37e9])
                    end_timer = time.time()

                    print(f'time to run SMRT: {int(end_timer - start_timer)} s')

                else: smrt_res = None

            else: smrt_res = None

            # Process results

            results = smrt_utils.process_results(pro_list, smrt_res, [19e9, 37e9])

            results['coords'] = my_track.frame['track_coords']

            # Save the results

            results.to_hdf(f'{output_dir}{results_f_name}{year}.hdf5', key=f'{str(track_no)}', mode='a')

            if make_spro == True:
                os.system(f'mv Snowpack_files/{track_no}_SPLG.pro SP_LG_Output/{track_no}.pro')
                pro_utils.pro_stripper(track_no)

        except Exception as e: logging.warning(f'Track no: {track_no} {e}')

        if single_run == True: exit()

logging.critical(f'End time: {str(datetime.datetime.now())}')
print(f'End time: {str(datetime.datetime.now())}')
print(f'Mean time = {np.nanmean(SNOWPACK_TIMER)}')
print(f'Successful runs = {len(SNOWPACK_TIMER)}')