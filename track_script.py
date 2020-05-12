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

def SP_LG(track_no,
            year            = 2016,              # Choose a year
            block_smrt      = True,             # Block SMRT from running - fast if you don't care about microwaves
            save_media_list = False,             # Save a 'media' object suitable for SMRT to operate on
            make_spro       = False,             # Make a 'stripped .pro' file for each track. Storage intensive
            use_RAM         = False,              # Saves temporary SP files to RAM rather than hard disk to increase speed
            delete          = True,
            log_f_name      = 'log.txt',
            output_dir = "/home/robbie/Dropbox/SP_LG/SP_LG_Output/",
            results_f_name = f'1151',  # Set the filename for the resulting .hdf5 file
            media_f_name = f'med',     # Set the name of the media file for SMRT (if created)
            ram_dir = '/dev/shm/SP',          # Location of ram directory - if used
            tmp_dir = '/home/robbie/Dropbox/SP_LG/Snowpack_files', # Location of temp hard disk location - if used
            aux_dir = '/home/robbie/Dropbox/Data/for_grace/'):

###################################################################################

    # Model code below, do not modify

    hard_stop_date = datetime.date(year=year + 1,
                                   month=5,
                                   day=1)

    if use_RAM:
        tmp_dir = ram_dir

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    # print(f'Track number: {track_no}')
    logging.info(f'Track Number: {track_no}')

    # Now create a .smet file of reanalysis and return a track object

    my_track = track_utils.create_smet_file(year=year,
                                            track_no=track_no,
                                            stop_date=hard_stop_date,
                                            tmp_dir=tmp_dir,
                                            aux_dir=aux_dir)



    if my_track.valid_data == False:
        # If false, it means you probably have a 'summer track'
        logging.info(f'No relevant data for track {track_no}')
        duration = np.nan

    else:

        try:

            logging.debug(f'Track dates: {my_track.info["start_date"]} : {my_track.info["end_date"]}')

            SP_utils.create_sno_file(start_date=my_track.info['start_date'],
                                    start_loc = my_track.info['start_coords'],
                                    track_no=track_no,
                                    tmp_dir=tmp_dir,
                                    aux_dir=aux_dir)

            SP_utils.create_ini_file(track_no=track_no,
                                     tmp_dir=tmp_dir,
                                     aux_dir=aux_dir)

            ###################################################################################

            # Run SNOWPACK

            duration = SP_utils.run(my_track.info['end_date'],
                         tmp_dir = tmp_dir,
                         track_no = track_no)

            pro_list = pro_utils.read(track_no, tmp_dir)                # Read the .pro file into a profile object

            # Prep media for SMRT to operate on if required

            ##########################################################################################

            if save_media_list or (not block_smrt):

                mediums_list = [smrt_utils.prep_medium(snowpro) for snowpro in pro_list]

                if save_media_list:

                    # Shelve the list of objects under the track_no
                    shelf_dir = f"{output_dir}{media_f_name}_{year}"

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

            results.to_hdf(f'{output_dir}{results_f_name}{year}.hdf5', key=f'{str(track_no)}', mode='a')

            if make_spro == True:
                os.system(f'mv {tmp_dir}/{track_no}_SPLG.pro SP_LG_Output/{track_no}.pro')
                pro_utils.pro_stripper(track_no)

        except Exception as e:
            logging.exception(f'{track_no}')
            duration = np.nan

        if delete:
            deletion_list = [f'{track_no}_SPLG.haz',
                             f'{track_no}_SPLG.ini',
                             f'{track_no}_SPLG.sno',
                             f'{track_no}_SPLG.pro',
                             f'config_{track_no}.ini',
                             f'track_{track_no}.smet']

            with open(f'{output_dir}{log_f_name}','ab') as log:
                for file in deletion_list:
                    cleaner_command = ['rm', f'{file}']
                    subprocess.call(cleaner_command,
                                    cwd=f'{tmp_dir}',
                                    stderr=log)

    return(duration)
