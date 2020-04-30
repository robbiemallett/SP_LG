import numpy as np
import pro_utils
from smrt import make_snowpack, make_ice_column, make_model, sensor_list
import os
import sys
import logging
import itertools
import pandas as pd
# from smrt.utils import dmrt_qms_legacy

def process_results(snowpro_list,smrt_res,frequencies):

    dict_of_lists = {

                    'snow_depth' : [snowpro.snowdepth for snowpro in snowpro_list],
                    'snow_density' : [snowpro.snowdensity for snowpro in snowpro_list],
                    'ice_thickness' : [snowpro.icethickness for snowpro in snowpro_list],
                    'date' : [snowpro.datetime.date() for snowpro in snowpro_list]

                    }

    if smrt_res != None:

        for pol in ['V', 'H']:
            for freq in frequencies:
                dict_of_lists['Tb'+str((int(freq/1e9),pol))] = smrt_res.Tb_as_dataframe(polarization=pol,frequency=freq)['Tb']

    df = pd.DataFrame(dict_of_lists)

    df.set_index(['date'], inplace=True, drop=True)

    return(df)



def prep_medium(snowpro,
                brine_inc_corr_len=1.0e-3):

    snow_df, ice_df = snowpro.snowframe, snowpro.iceframe


    # Establish correlation length using Vargel 2020

    SSA = 3/((0.917/2)*np.array(snow_df['optical equivalent grain size (mm)']))
    IVF = np.array(snow_df['ice volume fraction (%)'])/100
    snow_df['CL'] = 4 * np.divide(np.subtract(1, IVF), 917*SSA)

    snowpack = make_snowpack(thickness=snow_df['thickness_m'],

                             temperature=snow_df['element temperature (degC)'] + 273.15,

                             microstructure_model='exponential',

                             corr_length=snow_df['CL'],

                             density=snow_df['element density (kg m-3)'],

                             salinity=snow_df['bulk salinity (g/kg)'] / 1000)

    ice_col = make_ice_column(ice_type='firstyear',
                              thickness=ice_df['thickness_m'],
                              temperature=ice_df['element temperature (degC)'] + 273.15,
                              microstructure_model='exponential',
                              corr_length=np.array([brine_inc_corr_len] * len(ice_df['thickness_m'])),
                              brine_inclusion_shape='spheres',
                              salinity=ice_df['bulk salinity (g/kg)'] / 1000,
                              density=ice_df['element density (kg m-3)'],
                              add_water_substrate='ocean')

    medium = snowpack + ice_col

    return(medium)


def run_media_series(mediums_list,
                 frequencies,
                 solver='dort',
                 angle=55,
                 pol='V'):


    # create the sensor
    radiometer = sensor_list.passive(frequencies, angle, pol)

    n_max_stream = 32  # TB calculation is more accurate if number of streams is increased (currently: default = 32);

    m = make_model("iba", solver,
                   rtsolver_options={"n_max_stream": n_max_stream})

    # run the model for snow-covered sea ice:

    res = m.run(radiometer, mediums_list, progressbar=True)

    # CODE FOR SWITCHING TO DMRT IN EVENT OF DORT FAILURE:
    #
    # try:
    #     if solver == 'dort':
    #         m = make_model("iba", solver,
    #                        rtsolver_options={"n_max_stream": n_max_stream})
    #
    #         # run the model for snow-covered sea ice:
    #
    #         res = m.run(radiometer, mediums_list)
    #     elif solver == 'dmrt_qms':
    #         print('qms')
    #         res = dmrt_qms_legacy.run(radiometer,
    #                                   snowpack,
    #                                   dmrt_qms_path = '/home/robbie/DMRT-QMS/')
    # except:
    #     if solver == 'dort':
    #         logging.warning('Renormalisation failed - forcing...')
    #
    #         m = make_model("iba", solver,
    #                        rtsolver_options={"n_max_stream": n_max_stream,
    #                                          "phase_normalization": 'forced'})
    #
    #         # run the model for snow-covered sea ice:
    #         res = m.run(radiometer, medium)
    #     else:
    #         logging.error('QMS Failed')
    #         return(0)

    return (res)

# if __name__ == '__main__':
#     os.chdir("Snowpack_files")
#     result_list = run_track()
#     print(result_list)