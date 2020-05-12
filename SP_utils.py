import os
import numpy as np
import subprocess
from ERA5_utils import lonlat_to_xy
import xarray as xr
import psutil
from scipy import spatial
import time

def run(end_date,
        track_no,
        tmp_dir):

    # SP_command = f'snowpack -c {tmp_dir}/config_{track_no}.ini -e {end_date} 1> log.txt'
    # subprocess.run(SP_command,shell=True)

    #############################################################################################

    # args = ['snowpack', '-c', f'{tmp_dir}/config_{track_no}.ini', '-e', f'{end_date}', '1>', 'log.txt']
    # with open('SP_output.txt', 'a') as f:
    #     sp_output = subprocess.run(args, shell=False, stdout=f, text = True)
    # if sp_output.returncode != 0:
    #     print(sp_output.stderr)

    #########################################################

    args = ['snowpack', '-c', f'{tmp_dir}/config_{track_no}.ini', '-e', f'{end_date}']

    start_timer = time.time()

    # with open(f'log.txt', 'ab') as log:
    sp_output = subprocess.call(args,
                                    cwd=f'{tmp_dir}',
                                    stdout=subprocess.DEVNULL,
                                    # stderr=log,
                                    stderr=subprocess.DEVNULL)

    end_timer = time.time()

    duration = int(end_timer-start_timer)

    return(duration)



def get_init_vals(start_date,start_loc,pio_dir,w99_dir):

    if start_date.month == 8: # If ice parcel exists at start of simulation, then take W99 or

        pio_data = get_pio_field(start_date.year,start_date.month, pio_dir=pio_dir)
        w99_thick_field = get_w99_field(start_date.year,10,w99_dir=w99_dir)['depth']

        pio_thick_field = pio_data['thickness']

        lon_grid, lat_grid = np.array(pio_data['lon']), np.array(pio_data['lat'])
        x_grid, y_grid = lonlat_to_xy(lon_grid, lat_grid)
        xy_grid_points = list(zip(x_grid.ravel(), y_grid.ravel()))
        EASE_tree = spatial.KDTree(xy_grid_points)
        distance, index = EASE_tree.query(start_loc)
        nearest_index = np.unravel_index(index, (361, 361))

        # pio_thick_field = get_field('piomas',start_date.month,start_date.year,variable='thickness',resolution=361)['field']
        # w99_thick_field = get_field('w99',start_date.month,start_date.year,variable='depth',resolution=361)['field']

        pio_thick_point, w99_thick_point = pio_thick_field[nearest_index], w99_thick_field[nearest_index]

        if (np.isnan(w99_thick_point)) or (w99_thick_point < 0.01):

            # logging.info(f'Problematic snow depth: {w99_thick_point}')

            w99_thick_point = 0.01
    else:
        pio_thick_point, w99_thick_point = 0.2, 0.01

    return(pio_thick_point, w99_thick_point)

def get_w99_field(year,month,w99_dir):

    with xr.open_dataset(f'{w99_dir}/{year}_mW99.nc') as data:
        ds_month = data.where(int(month) == data.month, drop=True)
        field = np.array(ds_month['depth'])[0]
        lon = ds_month['lon']
        lat = ds_month['lat']

    return({'depth':field,
            'lon':lon,
            'lat':lat})


def get_pio_field(year, month, pio_dir):
    with xr.open_dataset(f'{pio_dir}/pio_{year}.nc') as data:
        ds_month = data.where(int(month) == data.month, drop=True)
        field = np.array(ds_month['thickness'])[0]
        lon = ds_month['lon']
        lat = ds_month['lat']

    return ({'thickness': field,
             'lon': lon,
             'lat': lat})

def create_sno_file(start_date,
                    start_loc,
                    track_no,
                    tmp_dir,
                    pio_dir,
                    w99_dir):

    SIT, snow_depth = get_init_vals(start_date,
                                    start_loc,
                                    pio_dir=pio_dir,
                                    w99_dir=w99_dir)

    sno_file_name = f'{tmp_dir}/{track_no}_SPLG.sno'
    station_name = f'track_{track_no}'

    iso_startdate = start_date.isoformat()


    preamble = f"""SMET 1.1 ASCII
[HEADER]
station_id    = {station_name}
station_name  = {station_name}
latitude      = -77.527010
longitude     = -38.892820
altitude      = 0
nodata        = -999
tz            = 1
source        = AWI and SLF
ProfileDate   = {iso_startdate}
HS_Last       = 0
SlopeAngle    = 0
SlopeAzi      = 0
nSoilLayerData= 0
nSnowLayerData= 2
SoilAlbedo    = 0.09
BareSoil_z0   = 0.2
CanopyHeight   = 0
CanopyLeafAreaIndex = 0
CanopyDirectThroughfall = 1
WindScalingFactor = 1
ErosionLevel      = 0
TimeCountDeltaHS  = 0
fields        = timestamp Layer_Thick  T  Vol_Frac_I  Vol_Frac_W  Vol_Frac_V  Vol_Frac_S Rho_S Conduc_S HeatCapac_S  rg  rb  dd  sp  mk mass_hoar ne CDot metamo Sal h
[DATA]"""

    data_amble = f"""
{iso_startdate} {SIT} -1.6250 0.9 0.0917 0.0083 0.00 0.00 0.00 0.00 3.00 2.00 1.00 0.00 7.00 0.00 1 0 0.00 2.759 -999
{iso_startdate} {snow_depth} -2 0.3 0.00 0.7 0.00 0.00 0.00 0.00 0.15 0.09 0.00 0.00 0 0.00 1 0 0.00 0 -999"""


    f = open(sno_file_name, "w+", encoding='utf8')
    f.write(preamble + '\n')
    f.write(data_amble)

    f.close()


def create_ini_file(track_no, tmp_dir):

    ini_file_name = f'{tmp_dir}/config_{track_no}.ini'

    x = os.getcwd()

    details = f"""IMPORT_BEFORE = {x}/basic_config.ini
[OUTPUT]
experiment = SPLG
USEREFERENCELAYER = TRUE
[SNOWPACK]
ENFORCE_MEASURED_SNOW_HEIGHTS = FALSE
GEO_HEAT = 8
[SNOWPACKADVANCED]
WATERTRANSPORTMODEL_SNOW	= BUCKET
WATERTRANSPORTMODEL_SOIL	= BUCKET
LB_COND_WATERFLUX		= SEAICE
[SNOWPACKSEAICE]
SALINITYPROFILE		= SINUSSAL
SALINITYTRANSPORT_SOLVER  = IMPLICIT
[INPUT]
STATION1	=	track_{track_no}.smet
SNOWFILE1	=	{track_no}_SPLG.sno
[OUTPUT]
METEOPATH	=	{tmp_dir}

"""
    f = open(ini_file_name, "w+", encoding='utf8')
    f.write(details)

    f.close()

def dangerous_temp():
    temps =  psutil.sensors_temperatures()['coretemp']
    too_hot = False
    for i in temps:
        if i[1] > 70:
            too_hot = True

    return(too_hot)