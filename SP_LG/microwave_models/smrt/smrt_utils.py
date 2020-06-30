import numpy as np
from smrt import make_snowpack, make_ice_column, make_model, sensor_list
from smrt.permittivity.saline_snow import saline_snow_permittivity_geldsetzer09
from smrt.permittivity.saline_ice import saline_ice_permittivity_pvs_mixing

import pandas as pd
# from smrt.utils import dmrt_qms_legacy

def process_SMRT_results(my_track,
                         config,
                         smrt_res):

    phys_res_df = my_track.output

    smrt_res_df = smrt_res.Tb_as_dataframe()

    for pol in ['V', 'H']:
        for freq in config.frequencies:

            my_list = list(smrt_res.Tb_as_dataframe(polarization=pol,frequency=freq)['Tb'])

            phys_res_df['Tb'+str((int(freq/1e9),pol))] = my_list

    my_track.output = phys_res_df

    return(my_track)


def prep_medium(snowpro,
                ice_type):

    brine_inc_corr_len = 1.0e-3

    snow_df, ice_df = snowpro.snowframe, snowpro.iceframe

    # Get the ice type in order to model the ice scatterers

    SSA = 3/((0.917/2)*np.array(snow_df['optical equivalent grain size (mm)']))
    IVF = np.array(snow_df['ice volume fraction (%)'])/100
    snow_df['CL'] = 4 * np.divide(np.subtract(1, IVF), 917*SSA)

    snowpack = make_snowpack(thickness=snow_df['thickness_m'],

                             temperature=snow_df['element temperature (degC)'] + 273.15,

                             microstructure_model='exponential',

                             corr_length=snow_df['CL'],

                             density=snow_df['element density (kg m-3)'],

                             salinity=snow_df['bulk salinity (g/kg)'] / 1000,

                             ice_permittivity_model = saline_snow_permittivity_geldsetzer09)

    ice_col = make_ice_column(ice_type=ice_type,

                              thickness=ice_df['thickness_m'],

                              temperature=ice_df['element temperature (degC)'] + 273.15,

                              microstructure_model='exponential',

                              corr_length=np.array([brine_inc_corr_len] * len(ice_df['thickness_m'])),

                              brine_inclusion_shape='spheres',

                              salinity=ice_df['bulk salinity (g/kg)'] / 1000,

                              density=ice_df['element density (kg m-3)'],

                              add_water_substrate='ocean',

                              ice_permittivity_model = saline_ice_permittivity_pvs_mixing)

    medium = snowpack + ice_col

    return(medium)


def run_media_series(mediums_list,
                 frequencies,
                 pol,
                 parallel,
                 solver='dort',
                 angle=55):


    # create the sensor
    radiometer = sensor_list.passive(frequencies, angle, pol)

    n_max_stream = 32  # TB calculation is more accurate if number of streams is increased (currently: default = 32);

    m = make_model("iba", solver,
                   rtsolver_options={"n_max_stream": n_max_stream,
                                     'prune_deep_snowpack':5})

    # run the model for snow-covered sea ice:

    res = m.run(radiometer,
                mediums_list,
                progressbar=True,
                parallel_computation=parallel)

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