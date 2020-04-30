from netCDF4 import Dataset
from scipy import interpolate
from scipy.stats import linregress
import numpy as np
from pyproj import Proj, transform
import pickle
import pandas as pd
import h5py

EASE_Proj = Proj(init='epsg:3408')
WGS_Proj = Proj(init='epsg:4326')


def xy_to_lonlat(x, y):
    lon, lat = transform(EASE_Proj, WGS_Proj, x, y)
    return (lon, lat)


directory = '/media/robbie/Seagate Portable Drive/im_parcels_v4/'


def upsample_week_to_day(EASE_x_weekly):
    dayno = np.array(range(len(EASE_x_weekly))) * 7
    xnew = np.arange(0, 365, 1)

    f = interpolate.interp1d(dayno, EASE_x_weekly, kind='linear')

    EASE_x_daily = f(xnew)

    return (EASE_x_daily)


file = Dataset('/home/robbie/test_vectors.nc')

index = list(range(0, 361))
x = file['x'][index]
y = file['y'][index]

x_slope, x_intercept, r_value, p_value, std_err = linregress(index, x)
y_slope, y_intercept, r_value, p_value, std_err = linregress(index, y)


def process_raw_tracks(year):

    year = int(year)

    file = f'parcels_xyc_{str(year)}w31_{str(year + 1)}w31.csv'

    data = pd.read_csv(directory + file, index_col=None, header=None)

    data.replace([-999.0, 999.0], np.nan, inplace=True)

    data_T = data.transpose()

    lonlat_frame = pd.DataFrame({})
    xy_frame = pd.DataFrame({})

    hf = h5py.File(str(year)+'.h5','w')

    for track_no in range(0, data.shape[0], 1):

        track = data.transpose()[track_no]

        x_coords = track[::3]
        y_coords = track[1::3]

        EASE_x = [x * x_slope + x_intercept for x in x_coords]
        EASE_y = [(-y) * y_slope - y_intercept for y in y_coords]

        EASE_x_daily = upsample_week_to_day(EASE_x)
        EASE_y_daily = upsample_week_to_day(EASE_y)


        dat_to_save = list(zip(EASE_x_daily, EASE_y_daily))

        hf.create_dataset(str(track_no), data=dat_to_save)
        # lon, lat = xy_to_lonlat(EASE_x_daily, EASE_y_daily)
        #
        # lonlat_frame[track_no] = list(zip(lon, lat))
        # xy_frame[track_no] = list(zip(EASE_x_daily, EASE_y_daily))

    #     lonlat_frame.to_csv(f"{year}_tracks_lonlat.csv")
    #     xy_frame.to_csv(f"{year}_tracks_xy.csv")
    #     pickle.dump(result_frame,open(f"/media/robbie/Seagate Portable Drive/im_parcels_v4/{year}_track_daily_lonlat.p","wb"))
    # pickle.dump(xy_frame, open(f"{str(year)}_track_daily_xy.p",
    #                            "wb")
    # print('\a')
    # print('Calculations Complete - Writing...')
    hf.close()
    # for i in range(xy_frame.shape[1]):
    #     xy_frame[i].to_hdf(f'{year}.h5',
    #                     key = i,
    #                     mode = 'a')

    # print('Input Year:')
    # year_input = input()
for year in np.arange(2010,2019):
    print(year)
    process_raw_tracks(year)
    print('Success!')
