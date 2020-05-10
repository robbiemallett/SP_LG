from pyproj import Proj, transform
import numpy as np
import pandas as pd
from math import sqrt
from netCDF4 import Dataset
import dateutil.parser
import pickle
import datetime
import xarray as xr

def lonlat_to_xy(lon, lat):
    EASE_Proj = Proj(init='epsg:3408')
    WGS_Proj = Proj(init='epsg:4326')
    x, y = transform(WGS_Proj, EASE_Proj, lon, lat)
    return (x, y)

def get_grid():

    ERA5_data = Dataset('ERA5_sample.nc')

    ERA5_lon_grid = np.array([np.array(ERA5_data['longitude']), ] * 121)

    ERA5_lat_grid = np.array([np.array(ERA5_data['latitude']), ] * 1440).T

    ERA_x_grid, ERA_y_grid = lonlat_to_xy(ERA5_lon_grid, ERA5_lat_grid)

    ERA_grid_points = list(zip(ERA_x_grid.ravel(), ERA_y_grid.ravel()))

    return(ERA_grid_points)

def get_daylist(year):

    """Takes a year and provides a list of 365 datetime objects for every day
    after starting on 31/8/year"""

    start_day = datetime.date(year=year, month=8, day=31)

    datetime_list = [start_day + timedelta(days=int(day)) for day in range(365)]

    return(datetime_list)


def add_reanalysis_to_track(my_track,era_dir,rh_dir):
    varlist = ['u10', 'v10', 't2m', 'ptype', 'asn', 'ssrd', 'strd', 'tp']

    list_of_dicts = []

    df = my_track.frame

    df['track_datetime'] = [datetime.datetime.combine(x, datetime.time()) for x in df['track_dates']]

    df.set_index(['track_datetime'], inplace=True, drop=True)

    df = df.resample('3H').ffill()

    # Make month and year columns

    df['month'] = [dt.month for dt in df['track_dates']]
    df['year'] = [dt.year for dt in df['track_dates']]

    # Find which months of reanalysis will be needed
#
    relevant_months = set(df['month'])

    for month in relevant_months:

        df_m = df[df['month'] == month]

        # Get year

        year = list(df_m['year'])[0]

        # Import data

        with xr.open_dataset(f'{era_dir}{str(year)}_{str(month).zfill(2)}.nc') as data, \
                xr.open_dataset(f'{rh_dir}{year}_{str(month).zfill(2)}rh_.nc') as rh_data:

            # data = Dataset(f'{era_dir}{str(year)}_{str(month).zfill(2)}.nc')
            # rh_data = Dataset(f'{rh_dir}{year}_{str(month).zfill(2)}rh_.nc')

            for index, row in df_m.iterrows():

                my_dt = index

                day_of_month = my_dt.day
                hour_of_day = my_dt.hour

                i_index = row['ERA_i_ind']
                j_index = row['ERA_j_ind']

                # Get the timestamp of the variable

                dat_dic = {}

                # Load the month's data

                time_index = int((8 * (day_of_month - 1)) + hour_of_day / 3)

                for var in varlist:
                    try:
                        dat_dic[var] = float(data[var][time_index,i_index,j_index])
                    except:
                        print(f'ERROR:{my_dt}')

                dat_dic['rh'] = float(rh_data['r'][time_index,i_index,j_index])

                dat_dic['dt'] = my_dt

                list_of_dicts.append(dat_dic)


    weather_df = pd.DataFrame(list_of_dicts)

    weather_df.set_index(['dt'], inplace=True, drop=True)

    df2 = pd.concat([df,weather_df],axis=1)

    df2['ISO_time'] = [x.isoformat() for x in df2.index]

    return (df2)


def add_derived_vars_to_track(df):
    cum_precip = 0
    cum_precip_list = []

    wind_speed_list = []

    wind_dir_list = []

    for i in range(len(df['tp'])):
        cum_precip += df['tp'][i]
        cum_precip_list.append(cum_precip)

        wind_speed_list.append(sqrt((df['v10'][i] ** 2) + (df['u10'][i] ** 2)))

        wind_dir_list.append(np.degrees(np.arctan(df['u10'][i] / df['v10'][i])))

    df['cum_prec'] = cum_precip_list
    df['wind_speed'] = wind_speed_list
    df['wind_dir'] = wind_dir_list

    return(df)

def reverser(s):
    d = dateutil.parser.parse(s)
    return d


def create_smet_df(df, hourly=True):

    TSG = np.full(len(df['ISO_time']), 273.05)
    null = np.full(len(df['ISO_time']), -999)

    smet_frame = pd.DataFrame({'timestamp': df['ISO_time'],
                               'TA': df['t2m'],
                               'RH': df['rh'] / 100,
                               'TSG': TSG,
                               'TSS_UNUSED': null,
                               'HS_UNUSED': null,
                               'VW': df['wind_speed'],
                               'DW': df['wind_dir'],
                               'OSWR_UNUSED': null,
                               'ISWR': df['ssrd'] / 10800,
                               'ILWR': df['strd'] / 10800,
                               'PSUM': df['tp'] * 1000,
                               'TS1': null,
                               'TS2': null,
                               'TS3': null})

    return (smet_frame)


def save_smet_file(smet_frame, meta_data, smet_file_name, track_no):

    pd.set_option('display.float_format', lambda x: '%.5f' % x)

    preamble = f"""SMET 1.1 ASCII
[HEADER]
station_id = {track_no}
latitude = {meta_data[0][1]}
longitude = {meta_data[0][0]}
altitude = 0
epsg = 21781
nodata = -999
tz = 1
source = Robbie Mallett CPOM UCL
fields = timestamp TA RH TSG TSS_UNUSED HS VW DW OSWR_UNUSED ISWR ILWR PSUM TS1 TS2 TS3
units_multiplier = 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
[DATA]"""

    smet_frame = smet_frame.round(5)

    stringblock = smet_frame.to_string(header=None, index=None)

    f = open(smet_file_name, "w+", encoding='utf8')
    f.write(preamble + '\n')
    f.write(stringblock)

    f.close()

    return({'start_date':smet_frame['timestamp'][0],
            'end_date':list(smet_frame['timestamp'])[-1]})