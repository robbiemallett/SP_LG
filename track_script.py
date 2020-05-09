import numpy as np
import psutil
import pro_utils
import os
import time
import SP_utils
import subprocess
from tqdm import trange
from dill import Pickler, Unpickler    # Necessary to store the SMRT objects for later analysiss
import shelve
shelve.Pickler = Pickler
shelve.Unpickler = Unpickler
import smrt_utils
import track_utils
import logging
import datetime

#########################################################################################

# Config

year            = 2016              # Choose a year
block_smrt      = True             # Block SMRT from running - fast if you don't care about microwaves
save_media_list = False             # Save a 'media' object suitable for SMRT to operate on
make_spro       = False             # Make a 'stripped .pro' file for each track. Storage intensive
single_run      = False             # Force a single run even when tracks_to_run is a list
use_RAM         = False              # Saves temporary SP files to RAM rather than hard disk to increase speed

# Choose a date cap to stop simulations running into the melt phase
hard_stop_date = datetime.date(year=year+1,
                               month=5,
                               day=1)

# Choose tracks to run, must be an iterator

# tracks_to_run = [1151]
tracks_to_run = [200]
# tracks_to_run = trange(1, 55_000, 25)

#########################################################################################

output_dir = "/home/robbie/Dropbox/Modelling/SP_LG/SP_LG_Output/"
log_f_name = 'my_run.log'        # Set file name of log file
log_level = logging.DEBUG      # Set level of detail of log. For long runs must be WARNING OR CRITICAL
results_f_name = f'1151_{year}'  # Set the filename for the resulting .hdf5 file
media_f_name = f'med_{year}'     # Set the name of the media file for SMRT (if created)
ram_dir = '/dev/shm/SP'          # Location of ram directory - if used
tmp_dir = '/home/robbie/Dropbox/SP_LG/Snowpack_files' # Location of temp hard disk location - if used
pio_dir = '/home/robbie/Dropbox/SM_Thickness/data/piomas/361x361'
w99_dir = '/home/robbie/Dropbox/SM_Thickness/data/W99/mW99_361'
era_dir = '/home/robbie/Dropbox/Modelling/ERA_forcings/ERA_'
rh_dir = '/media/robbie/Seagate Portable Drive/ERA5_3hr_reanalysis/ERA_'

###################################################################################

# Model code below, do not modify

if use_RAM:
    tmp_dir = ram_dir

if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

logging.basicConfig(level=log_level,             # Configure the log
                    filename=log_f_name)

logging.critical(f'Start time: {str(datetime.datetime.now())}')
print(f'Start time: {str(datetime.datetime.now())}')

SNOWPACK_TIMER = []                              # a list recording the duration of every SNOWPACK run.


for track_no in tracks_to_run:

    # print(f'Track number: {track_no}')
    logging.info(f'Track Number: {track_no}')

    # Now create a .smet file of reanalysis and return a track object

    my_track = track_utils.create_smet_file(year=year,
                                            track_no=track_no,
                                            stop_date=hard_stop_date,
                                            tmp_dir=tmp_dir,
                                            era_dir=era_dir,
                                            rh_dir=rh_dir)



    if my_track.valid_data == False:
        # If false, it means you probably have a 'summer track'
        logging.info(f'No relevant data for track {track_no}')

    else:

        try:

            logging.debug(f'Track dates: {my_track.info["start_date"]} : {my_track.info["end_date"]}')

            SP_utils.create_sno_file(start_date=my_track.info['start_date'],
                                    start_loc = my_track.info['start_coords'],
                                    track_no=track_no,
                                    tmp_dir=tmp_dir,
                                    pio_dir=pio_dir,
                                    w99_dir=w99_dir)

            SP_utils.create_ini_file(track_no=track_no,
                                     tmp_dir=tmp_dir)

            ###################################################################################

            # Run SNOWPACK

            duration = SP_utils.run(my_track.info['end_date'],
                         tmp_dir = tmp_dir,
                         track_no = track_no)

            SNOWPACK_TIMER.append(duration)

            pro_list = pro_utils.read(track_no, tmp_dir)                # Read the .pro file into a profile object

            # Prep media for SMRT to operate on if required

            ##########################################################################################

            if save_media_list or (not block_smrt):

                mediums_list = [smrt_utils.prep_medium(snowpro) for snowpro in pro_list]

                if save_media_list:

                    # Shelve the list of objects under the track_no
                    shelf_dir = f"{output_dir}{media_f_name}"

                    with shelve.open(shelf_dir, 'c') as d:

                        d[str(track_no)] = mediums_list

                # Run SMRT on the list of media

                if block_smrt == False:

                    start_timer = time.time() #Baseline for timing the SMRT run

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

            results.to_hdf(f'{output_dir}{results_f_name}.hdf5', key=f'{str(track_no)}', mode='a')

            if make_spro == True:
                os.system(f'mv {tmp_dir}/{track_no}_SPLG.pro SP_LG_Output/{track_no}.pro')
                pro_utils.pro_stripper(track_no)

        except Exception as e:  logging.exception("message")


        deletion_list = [f'{track_no}_SPLG.haz',
                         f'{track_no}_SPLG.ini',
                         f'{track_no}_SPLG.sno',
                         f'{track_no}_SPLG.pro',
                         f'config_{track_no}.ini',
                         f'track_{track_no}.smet']

        for file in deletion_list:
            cleaner_command = ['rm', f'{file}']
            subprocess.call(cleaner_command,
                            cwd=f'{tmp_dir}')

        if single_run: exit()

logging.critical(f'End time: {str(datetime.datetime.now())}')
print(f'End time: {str(datetime.datetime.now())}')
print(f'Mean time = {np.nanmean(SNOWPACK_TIMER)}')
print(f'Successful runs = {len(SNOWPACK_TIMER)}')