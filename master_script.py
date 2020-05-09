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
from track_script import SP_LG

# Choose tracks to run, must be an iterator

# tracks_to_run = [1151]
tracks_to_run = [200]
# tracks_to_run = trange(1, 55_000, 25)

log_f_name = 'my_run.log',  # Set file name of log file
log_level = logging.DEBUG,  # Set level of detail of log. For long runs must be WARNING OR CRITICAL
logging.basicConfig(level=log_level,
                    filename=log_f_name)


logging.critical(f'Start time: {str(datetime.datetime.now())}')
print(f'Start time: {str(datetime.datetime.now())}')

SNOWPACK_TIMER = []  # a list recording the duration of every SNOWPACK run.

for track_no in tracks_to_run:
    x = SP_LG(track_no)

logging.critical(f'End time: {str(datetime.datetime.now())}')
print(f'End time: {str(datetime.datetime.now())}')
print(f'Mean time = {np.nanmean(SNOWPACK_TIMER)}')
print(f'Successful runs = {len(SNOWPACK_TIMER)}')