import pandas as pd
import numpy as np
from pyproj import Proj, transform
from scipy import spatial
import tqdm
import datetime

def OIB_get(day, month, year):

    """Gets an individual OIB flight from file and returns as dataframe.

    Args:
        day (int): Day of month
        month (int): Month of year
        year (int): Year

    Returns:
        pandas dataframe

    """

    data_dir = '/home/robbie/Dropbox/Data/OIB_Quicklook/OIB_'

    cols_list = ['lat', 'lon', 'snow_depth']

    df = pd.read_csv(data_dir + year + month + day + ".txt",
                     sep=",", index_col=False,
                     low_memory=False,
                     usecols=cols_list)

    data = df.loc[df['snow_depth'] != -99999.0000]

    return (data)


def lonlat_to_xy(lon, lat, hemisphere, inverse=False):

    """Converts between longitude/latitude and EASE xy coordinates.

    Args:
        lon (float): WGS84 longitude
        lat (float): WGS84 latitude
        hemisphere (string): 'n' or 's'
        inverse (bool): if true, converts xy to lon/lat

    Returns:
        tuple: pair of xy or lon/lat values
    """

    EASE_Proj_n = Proj(init='epsg:3408')
    EASE_Proj_s = Proj(init='epsg:3409')
    WGS_Proj = Proj(init='epsg:4326')

    EASE_Proj = {'n': EASE_Proj_n,
                 's': EASE_Proj_s}

    if inverse == False:
        x, y = transform(WGS_Proj, EASE_Proj[hemisphere], lon, lat)
        return (x, y)

    else:
        x, y = transform(EASE_Proj, WGS_Proj[hemisphere], lon, lat)
        return (x, y)


def plot(df):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy

    """ Plots an OIB track.
    Args:
        df: dataframe of coordinates

    Returns:
        no return
    """

    fig = plt.figure(figsize=(8, 8))
    ax = plt.axes(projection=ccrs.NorthPolarStereo())

    ax.add_feature(cartopy.feature.LAND, edgecolor='black', zorder=1)

    ax.set_extent([-180, 180, 90, 60], ccrs.PlateCarree())

    plt.scatter(np.array(df['lon']), np.array(df['lat']),
                transform=ccrs.PlateCarree(), marker='.', s=0.1)

    plt.show()

if __name__ == '__main__':

    daysdict = {"201203": ["14", "15", "16", "17", "19", "21", "22", "23", "26", "27", "28", "29"],
                "201204": ["02"],
                "201303": ["21", "22", "23", "24", "26", "27"],
                "201304": ["22", "24", "25"],
                "201403": ["12", "13", "14", "15", "17", "18", "19", "21", "24", "25", "26", "28", "31"],
                "201404": ["03", "28"],
                "201503": ["19", "24", "25", "26", "27", "29", "30"],
                "201504": ["01", "03"],
                "201604": ["19", "20", "21", "29"],
                "201605": ["03", "04"],
                "201703": ["09", "10", "11", "12", "14", "20", "23", "24"],
                "201704": ["03", "05", "06", "07", "11", "19"],
                "201803": ["22"],
                "201804": ["03", "04", "06", "07", "08", "14", "16"]
                }



    all_data = {}

    for year in tqdm.trange(2012, 2019):

        tracks = np.load(f'/home/robbie/Dropbox/SP_LG/tracks/tracks_array_{year - 1}.npy')

        tracks_dict = {}

        year_keys = [key for key in daysdict.keys() if key[:4] == str(year)]

        print(year_keys)

        for key in year_keys:

            month = key[-2:]

            days = daysdict[key]

            for day in days:

                print(year, month, day)

                try:

                    #######################################

                    # Get and process file

                    dat = OIB_get(day=day, month=month, year=str(year))

                    dat['x'], dat['y'] = lonlat_to_xy(np.array(dat['lon']),
                                                      np.array(dat['lat']),
                                                      hemisphere = hemisphere)

                    diffs = list(zip(np.diff(dat['x']), np.diff(dat['y'])))

                    dists = [np.sqrt(x ** 2 + y ** 2) for (x, y) in diffs]

                    dists.insert(0, 0)

                    dat['dist'] = dists

                    dat = dat[dat['dist'] > 0.01]

                    dat['cum_dist'] = np.cumsum(dat['dist'])

                    date = datetime.date(year=int(year), month=int(month), day=int(day))
                    track_formal_start = datetime.date(year=int(year) - 1, month=8, day=31)

                    day_no = (date - track_formal_start).days

                    tracks_on_day = tracks[:, day_no, :]

                    valid_indexes = []
                    valid_values = []

                    for i in range(tracks_on_day.shape[1]):

                        vals = tracks_on_day[:, i]

                        if ~np.isnan(vals).all():
                            valid_indexes.append(i)
                            valid_values.append(tuple(vals))

                    tree = spatial.KDTree(valid_values)

                    nearest_valid_index = []
                    nearest_valid_dist = []

                    for row_num in range(dat.shape[0]):
                        loc = (dat.iloc[row_num]['x'],
                               dat.iloc[row_num]['y'])

                        distance, index = tree.query(loc)

                        nearest_valid_index.append(index)
                        nearest_valid_dist.append(distance)

                    unique_valid_index = set(nearest_valid_index)

                    tracks_dict[(year, month, day)] = unique_valid_index

                except Exception as e:
                    print(e)

        year_set = set()
        for key in tracks_dict:
            year_set.update(tracks_dict[key])

        all_data[year] = list(year_set)