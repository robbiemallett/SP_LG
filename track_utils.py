from pyproj import Proj, transform
import matplotlib.pyplot as plt
import h5py
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import sys
sys.setrecursionlimit(10000)
import ERA5_utils
import classes

def create_smet_file(year,
                     track_no,
                     stop_date):

    smet_file_name= f'Snowpack_files/track_{track_no}.smet'

    track = get(year, track_no)

    my_track = classes.track(track, year, stop_date)

    if my_track.error_flag == True:
        return(None)

    elif my_track.error_flag == False:

        rean = ERA5_utils.add_reanalysis_to_track(my_track)

        full = ERA5_utils.add_derived_vars_to_track(rean)

        smet = ERA5_utils.create_smet_df(full)

        initial_coords = xy_to_lonlat(my_track.info['start_coords'][0],
                                      my_track.info['start_coords'][1])

        start_date = my_track.info['start_date']

        metadata = (np.round(initial_coords, decimals=1), start_date)

        ERA5_utils.save_smet_file(smet, metadata, smet_file_name, track_no)

        # return(start_end)
        return(my_track)

def get(year,track_no):
    track_file_name = f'tracks/{year}.h5'

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

def plot_track(array1=0,array2=0,tuplelist=0,xy=True):

    if xy == True:
        lonlist, latlist = xy_to_lonlat(array1,array2)
    else:
        lonlist, latlist = array1, array2

    plt.figure(figsize=(10, 8))

    m = Basemap(projection='npstere', boundinglat=65, lon_0=360, resolution='l')
    m.drawcoastlines(linewidth=0.5)
    m.scatter(180, 90, latlon=True, marker='x', s=5)
    m.scatter(lonlist, latlist, latlon=True, marker='x', s=15)

    plt.show()
#
# if __name__ == "__main__":
#     create_smet_file(year=2016, track_no=11021)