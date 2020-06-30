from pyproj import Proj, transform
import h5py
import numpy as np
import warnings
warnings.filterwarnings("ignore") #Performance warning from pytables
import sys
sys.setrecursionlimit(10000)
from make_met_forcing import ERA5_utils, track_class
import psutil

def create_met_forcing(year,
                       track_no,
                       stop_date,
                       tmp_dir,
                       aux_dir,
                       model_name):

    track = get(year, track_no, aux_dir)

    my_track = track_class.track(track, year, stop_date, aux_dir)

    my_track.track_no = track_no

    if my_track.valid_data:

        rean = ERA5_utils.add_reanalysis_to_track(my_track,
                                                  aux_dir=aux_dir)

        full = ERA5_utils.add_derived_vars_to_track(rean)

        my_track.met_forcing = full

        initial_coords = xy_to_lonlat(my_track.info['start_coords'][0],
                                      my_track.info['start_coords'][1])

        start_date = my_track.info['start_date']

        metadata = (np.round(initial_coords, decimals=1), start_date)

    return(my_track)

def get(year, track_no, track_dir):

    track_file_name = f'{track_dir}/{year}.h5'

    f = h5py.File(track_file_name, 'r')

    track = list(f[str(track_no)])
    f.close()

    return (track)

def xy_to_lonlat(x, y):
    EASE_Proj = Proj(init='epsg:3408')
    WGS_Proj = Proj(init='epsg:4326')
    lon, lat = transform(EASE_Proj, WGS_Proj, x, y)
    return (lon, lat)

def lonlat_to_xy(lon, lat):
    EASE_Proj = Proj(init='epsg:3408')
    WGS_Proj = Proj(init='epsg:4326')
    x, y = transform(WGS_Proj, EASE_Proj, lon, lat)
    return (x, y)

def dangerous_temp():
    temps =  psutil.sensors_temperatures()['coretemp']
    too_hot = False
    for i in temps:
        if i[1] > 70:
            too_hot = True

    return(too_hot)