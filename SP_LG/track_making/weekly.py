from netCDF4 import Dataset
import datetime
from track_making.funcs import get, one_iteration, select_and_save_track
from scipy.spatial import KDTree
from misc.calibration_tools.identify_relevant_tracks import lonlat_to_xy
import numpy as np
import sys
import tqdm
from tqdm import trange


def make_weekly_tracks():
    """ Makes tracks from weekly ice motion vectors

    Returns:

    """

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Start Time =", current_time)

    # What year?
    if len(sys.argv) == 1:
        year = 2018
    else:
        year = int(sys.argv[1])

    if '-hpc' in sys.argv:
        data_dir = '/home/ucfarm0/tracks'
        grid_dir = '/home/ucfarm0/tracks/track_making/'
        output_dir = '/home/ucfarm0/Scratch/'
    else:
        data_dir = '/home/robbie/Dropbox/Data/IMV'
        output_dir = '/home/robbie/Dropbox/SP_LG/tracks/'
        grid_dir = ''

    # What day do you want to start?

    start_day = datetime.date(year=year, month=8, day=31)
    start_week_of_year = start_day.isocalendar()[1]

    # Get dataset
    data_first_half = Dataset('/home/robbie/Dropbox/Data/IMV/icemotion_weekly_nh_25km_20180101_20181231_v4.1.nc')
    data_scnd_half = Dataset('/home/robbie/Dropbox/Data/IMV/icemotion_weekly_nh_25km_20190101_20200602_ql.nc')

    # Get EASE_lons & EASE_lats

    EASE_lons = get('lon', grid_dir)
    EASE_lats = get('lat', grid_dir)

    EASE_xs, EASE_ys = lonlat_to_xy(EASE_lons.ravel(), EASE_lats.ravel(), hemisphere=hemisphere)

    EASE_tree = KDTree(list(zip(EASE_xs, EASE_ys)))

    EASE_xs_grid = EASE_xs.reshape((361, 361))
    EASE_ys_grid = EASE_ys.reshape((361, 361))

    start_x, start_y = EASE_xs.ravel(), EASE_ys.ravel()

    all_u16, all_v16 = np.array(data_first_half['u']), np.array(data_first_half['v'])
    all_u17, all_v17 = np.array(data_scnd_half['u']), np.array(data_scnd_half['v'])

    all_u = np.ma.concatenate((all_u16, all_u17), axis=0)
    all_v = np.ma.concatenate((all_v16, all_v17), axis=0)

    all_u = np.ma.masked_where(all_u == -9999.0, all_u)
    all_u = np.ma.filled(all_u, np.nan)
    all_v = np.ma.masked_where(all_v == -9999.0, all_v)
    all_v = np.ma.filled(all_v, np.nan)

    #######################################################

    tracks_array = np.full((2,
                            35,  # 35 weeks from Aug 31 till May 1st
                            70_000), np.nan)

    end_date = datetime.date(year=year + 1, month=4, day=30)

    data_for_start_day = {'u': all_u[start_week_of_year - 1],
                          'v': all_v[start_week_of_year - 1]}

    u_field = data_for_start_day['u'].ravel()

    # Select points on ease grid with valid velocity data on day 0

    valid_start_x = start_x[~np.isnan(u_field)]
    valid_start_y = start_y[~np.isnan(u_field)]

    valid_points = list(zip(valid_start_x, valid_start_y))

    for week_num in trange(0, 35):
        # for week_num in trange(0, 5):

        valid_points_x = list(zip(*valid_points))[0]
        valid_points_y = list(zip(*valid_points))[1]

        tracks_array[0, week_num, :len(valid_points_x)] = valid_points_x
        tracks_array[1, week_num, :len(valid_points_y)] = valid_points_y

        date = start_day + datetime.timedelta(weeks=week_num)

        week_of_year = date.isocalendar()[1]

        print(f'Week_num: {week_num}, Total tracks: {len(valid_points)}')

        # Get the ice motion field for that day

        data_for_week = {'u': all_u[start_week_of_year + week_num - 1],
                         'v': all_v[start_week_of_year + week_num - 1]}

        # Update points

        updated_points = [one_iteration(point,
                                        data_for_week,
                                        EASE_tree,
                                        7 * 24 * 60 * 60) if point != (np.nan, np.nan) else point for point in
                          valid_points]

        # Make list of points that are still alive

        clean_points = [point for point in updated_points if point != (np.nan, np.nan)]

        print(f'Tracks killed: {len(updated_points) - len(clean_points)}')

        # Create new parcels in gaps
        # Make a decision tree for the track field

        track_tree = KDTree(clean_points)

        # Identify all points of ease_grid with valid values

        u_field = np.ma.masked_values(data_for_week['u'].ravel(), np.nan)

        valid_x, valid_y = start_x[~np.isnan(u_field)], start_y[~np.isnan(u_field)]

        # Iterate through all valid points to identify gaps using the tree

        new_points = []

        for point in zip(valid_x, valid_y):
            distance, index = track_tree.query(point)

            if distance > 20_000:  # Initiate new track
                new_points.append(point)

        print(f'Tracks added: {len(new_points)}')

        # Add newly intitiated tracks to other tracks

        valid_points = updated_points + new_points

        if (len(valid_points) > 70_000) or (date > end_date): break

    output_array = np.full((2, 35 * 7, 70_000), np.nan)

    for coord_index in [0, 1]:

        x_coords = tracks_array[coord_index]

        x_to_eval = np.array(range(0, 35 * 7))

        x_existing = np.array(range(0, 35 * 7, 7))

        for track_no in tqdm.trange(70_000):

            y_existing = x_coords[:, track_no]

            if ~np.isnan(y_existing).all():
                interped = np.interp(x_to_eval, x_existing, y_existing, left=np.nan, right=np.nan)

                output_array[coord_index, :, track_no] = interped

    np.save(f'{output_dir}tracks_array_{year}_daily.npy', output_array)

    for track_no in tqdm.trange(output_array.shape[2]):
        track = output_array[:, :, track_no]

        select_and_save_track(track,
                              track_no,
                              f'{output_dir}qt_{year}.h5')

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("End Time =", current_time)


if __name__ == '__main__':
    make_weekly_tracks()
