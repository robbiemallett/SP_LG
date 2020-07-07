from netCDF4 import Dataset
import h5py
import numpy as np

def get(string,grid_dir):
    """Returns a 361x361 grid of lon lat values for the 25 km EASE grid from netcdf file

    Args:
        string: 'lon' or 'lat', depending on which grid you want
        grid_dir: directory where grid is stored

    Returns:
        numpy array of lon/lat coordinates

    #TODO it's unnecessary to call this twice (and read the file twice), to get lon and lat grids. You always want both

    """

    path_grid = f'{grid_dir}nh_grid.nc'

    if string == 'lon':
        grid_data = Dataset(path_grid)
        lon = np.array(grid_data.variables["lon"])
        return(lon)
    elif string == 'lat':
        grid_data = Dataset(path_grid)
        lat = np.array(grid_data.variables["lat"])
        return(lat)

# def get_day_vectors(date_obj):
#
#     """Returns a 2-part dictionary of u and v vectors for a given date, on 361x361 25 km EASE grid.
#     CURRENTLY UNUSED"""
#
#     day_of_year = date_obj.timetuple().tm_yday
#
#     data = Dataset('/home/robbie/Dropbox/Data/IMV/icemotion_daily_nh_25km_20160101_20161231_v4.1.nc')
#
#     data_for_day = {'u': data['u'][day_of_year - 1],
#                     'v': data['v'][day_of_year - 1]}
#
#     return (data_for_day)


def one_iteration(point, field, tree, timestep):

    """Iterates a point based on its position in an ice motion field.

    Must be passed a pre-calculated KDTree of the field (which saves time). If the point's nearest velocity value is
    nan (representing open water), then it returns a nan point (np.nan, np.nan)

    Args:
        point: tuple of EASE grid xy coordinates
        field: velocity field in cm/s
        tree: pre-calculated KDTree of grid points of velocity field
        timestep: time in seconds

    Returns:
        Tuple of floats representing xy coordinates of iterated point. If floe disappears then coords are np.nan.

    """

    distance, index = tree.query(point)

    u_vels, v_vels = np.array(field['u']) / 100, np.array(field['v']) / 100

    u_vels = np.ma.masked_where(u_vels == -99.99, u_vels)
    u_vels = np.ma.masked_values(u_vels, np.nan)

    u_vel, v_vel = u_vels.ravel()[index], v_vels.ravel()[index]

    if np.isnan(u_vel):
        #         print('Failed')
        return ((np.nan, np.nan))

    else:

        u_disp, v_disp = u_vel * timestep, v_vel * timestep

        new_position = (point[0] + u_disp, point[1] + v_disp)

        return (new_position)


def select_and_save_track(track, track_no, f_name):

    """ Writes floe trajectory to hdf5 file in append mode

    #TODO check the datatype of the track input to this function

    Args:
        track: track coords
        track_no: int representing track number (for later data retrieval)
        f_name: file name of hdf5 storage file

    Returns:
        no return, writes to file.

    """

    with h5py.File(f_name, 'a') as hf:
        hf[f't{track_no}'] = track
