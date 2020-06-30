import os
import numpy as np
import subprocess
from snow_models.snowpack.pro_utils import read_pro
import pandas as pd

def run_snowpack(my_track,
                 config):

    create_smet_file(my_track,
                     config)

    create_sno_file(my_track,
                    config)

    create_ini_file(my_track,
                    config)

    args = ['snowpack',
            '-c',
            f'{config.tmp_dir}/config_{my_track.track_no}.ini',
            '-e',
            f'{my_track.info["end_date"]}']

    subprocess.call(args,
                    cwd=f'{config.tmp_dir}',
                    stdout=subprocess.DEVNULL)

    snowpro_list = read_pro(my_track,
                            config)  # Read the .pro file into a profile object

    my_track.output = process_results(snowpro_list)

    if config.microwave_model:

        my_track.snowpro_list = snowpro_list

    if config.delete:

        delete_snowpack_files(my_track,
                              config)

    return(my_track)


def process_results(snowpro_list):

    dict_of_lists = {

                    'snow_depth' : [snowpro.snowdepth for snowpro in snowpro_list],
                    'snow_density' : [snowpro.snowdensity for snowpro in snowpro_list],
                    'ice_thickness' : [snowpro.icethickness for snowpro in snowpro_list],
                    'date' : [snowpro.datetime.date() for snowpro in snowpro_list],
                    'snow_surface_temp' : [snowpro.sst for snowpro in snowpro_list],
                    'ice_snow_temp': [snowpro.ist for snowpro in snowpro_list]

    }

    df = pd.DataFrame(dict_of_lists)

    df.set_index(['date'], inplace=True, drop=True)

    return(df)

def create_sno_file(my_track,
                    config):

    sno_file_name = f'{config.tmp_dir}/{my_track.track_no}_SPLG.sno'
    station_name = f'track_{my_track.track_no}'

    iso_startdate = my_track.info['start_date'].isoformat()

    SIT = my_track.init_vals[0]
    snow_depth = my_track.init_vals[1]


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


def create_ini_file(my_track,
                    config):

    ini_file_name = f'{config.tmp_dir}/config_{my_track.track_no}.ini'

    details = f"""IMPORT_BEFORE = {config.aux_data_dir}basic_config.ini
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
STATION1	=	track_{my_track.track_no}.smet
SNOWFILE1	=	{my_track.track_no}_SPLG.sno
[OUTPUT]
METEOPATH	=	{config.tmp_dir}

"""
    f = open(ini_file_name, "w+", encoding='utf8')
    f.write(details)

    f.close()


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


def create_smet_file(my_track, config):

    smet_frame = create_smet_df(my_track.met_forcing)

    smet_file_name= f'{config.tmp_dir}/track_{my_track.track_no}.smet'

    pd.set_option('display.float_format', lambda x: '%.5f' % x)

    preamble = f"""SMET 1.1 ASCII
[HEADER]
station_id = {my_track.track_no}
latitude      = -77.527010
longitude     = -38.892820
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

def delete_snowpack_files(my_track,
                          config):

    track_no = my_track.track_no

    deletion_list = [f'{track_no}_SPLG.haz',
                     f'{track_no}_SPLG.ini',
                     f'{track_no}_SPLG.sno',
                     f'{track_no}_SPLG.pro',
                     f'config_{track_no}.ini',
                     f'track_{track_no}.smet']

    with open(f'{config.output_dir}{config.log_f_name}', 'ab') as log:
        for file in deletion_list:
            cleaner_command = ['rm', f'{file}']
            subprocess.call(cleaner_command,
                            cwd=f'{config.tmp_dir}',
                            stderr=log)