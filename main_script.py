import numpy as np
import psutil
import time
import pro_utils
import os
import time
from pandas.plotting import register_matplotlib_converters
import SP_utils
import pandas as pd
import smrt_utils
import track_utils
from netCDF4 import Dataset
import logging
import datetime
register_matplotlib_converters()
logging.basicConfig(level=logging.DEBUG,
                    filename='test.log')

year = 2016
block_smrt = True
save_media_list = False
single_run = True

# Choose a date cap to stop simulations running into the melt phase
hard_stop_date = datetime.date(year=year+1, month=5, day=1)  # May first

# tracks_to_run = [49]
tracks_to_run = list(range(10_600,60_000,3_000))

# Now choose a track number to analyse (initially)
# for track_no in range(sample_track, sample_track+1):
for track_no in tracks_to_run:

    print(f'Track number: {track_no}')
    logging.info(f'Track Number: {track_no}')

    cleaner_string = 'rm -r Snowpack_files/* >nul 2>&1'
    os.system(cleaner_string)

    # Now create a .smet file for the track and a python object for that track

    my_track = track_utils.create_smet_file(year=year,
                                            track_no=track_no,
                                            stop_date=hard_stop_date)



    if my_track == None:
        logging.info(f'Passing Track Number {track_no}')
        print('error')
        pass
    else:

        print(f'Track dates: {my_track.info["start_date"]} : {my_track.info["end_date"]}')

        logging.debug('Creating initial .SNO file...')

        SP_utils.create_sno_file(start_date=my_track.info['start_date'],
                                start_loc = my_track.info['start_coords'],
                                track_no=track_no)

        logging.debug('Creating configuration .INI file...')

        SP_utils.create_ini_file(track_no=track_no)

        # Run SNOWPACK

        logging.debug('Running SNOWPACK...')

        start_timer = time.time()

        SP_utils.run(my_track.info['end_date'],
                     track_no)

        while 'snowpack' in (p.name() for p in psutil.process_iter()):
            time.sleep(0.3)

        end_timer = time.time()

        print(f'time to run SNOWPACK: {int(end_timer-start_timer)} s')


        # Read the .pro file into a profile object

        pro_list = pro_utils.read(track_no)

        # Prep media for SMRT to operate on

        mediums_list = [smrt_utils.prep_medium(snowpro) for snowpro in pro_list]

        # Run SMRT on the list of media

        if block_smrt == False:

            print('Running SMRT')

            start_timer = time.time()

            smrt_res = smrt_utils.run_media_series(mediums_list,
                                                    [19e9, 37e9])
            end_timer = time.time()

            print(f'time to run SMRT: {int(end_timer - start_timer)} s')

        else:
            smrt_res = None

        # Process results

        results = smrt_utils.process_results(pro_list, smrt_res, [19e9, 37e9])

        results['coords'] = my_track.frame['track_coords']

        # Save the results

        results.to_hdf(f'SP_LG_Output/track_df.hdf5', key=f'{track_no}', mode='a')

        # Clean the directory

        os.system(f'mv Snowpack_files/{track_no}_SPLG.pro SP_LG_Output/{track_no}.pro')

        pro_utils.pro_stripper(track_no)


        if single_run == True:
            exit()