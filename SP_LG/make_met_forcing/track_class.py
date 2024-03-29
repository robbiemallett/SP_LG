import numpy as np
from scipy import spatial
import pandas as pd
from make_met_forcing.ERA5_utils import get_grid
import logging
import datetime
import time


class track:
    """A virtual ice parcel track and associated reanalysis"""

    def __init__(self, input_track, year, hard_stop_date, aux_dir):

        # Trim leading and trailing nans from the track (as parcel enters and leaves the scheme)

        x_coords, y_coords = list(input_track[0]), list(input_track[1])

        input_track = list(zip(x_coords, y_coords))

        x_nans = np.isnan(x_coords) # Checks which values are nans and which aren't
        all_nans = all(x_nans) # Evaluates to True if all values are nans

        if all_nans == False:

            not_nan = np.where(x_nans == False) # Indexes of values where not nans start and stop

            startday = not_nan[0][0]
            end_day = not_nan[0][-1]+1
            duration = end_day - startday

            valid_track = input_track[startday:end_day] # Trim the list of input coordinates to valid tracks

            # MAKE A LIST OF DATETIME OBJECTS TO ACCOMPANY EACH COORDINATE PAIR

            valid_track_start_date = datetime.date(year=year, month=8, day=31) + datetime.timedelta(days=int(startday))

            date_list = [valid_track_start_date + datetime.timedelta(days=int(day)) for day in range(duration)]

            track_existance = [x for x in date_list if x < hard_stop_date]
            valid_track_trimmed = valid_track[:len(track_existance)]

            if track_existance:

                logging.info(f'Start:{track_existance[0]}. End:{track_existance[-1]}')

                if startday == datetime.date(year=year, month=8, day=31):
                    ice_type = 'firstyear'
                else:
                    ice_type = 'multiyear'

                self.info = {'start_day' : startday,
                              'end_day' : end_day,
                              'start_date' : track_existance[0],
                              'end_date' : track_existance[-1],
                              'start_coords' : valid_track_trimmed[0],
                              'end_coords': valid_track_trimmed[-1],
                              'ice_type':ice_type}

                ERA5_grid = get_grid(aux_dir=aux_dir)

                distance, index = spatial.KDTree(ERA5_grid).query(valid_track_trimmed)

                unraveled = np.unravel_index(index, (121, 1440))

                df = pd.DataFrame({ 'ERA_i_ind'   : unraveled[0],
                                    'ERA_j_ind'   : unraveled[1],
                                    'track_coords': valid_track_trimmed,
                                    'track_dates' :track_existance})

                self.frame = df

                self.valid_data = True
            else:
                logging.debug('Empty list upon trimming to stop date')
                self.valid_data = False
        else:
            logging.debug('Empty list upon trimming nans')
            self.valid_data = False
