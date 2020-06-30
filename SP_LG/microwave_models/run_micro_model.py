from microwave_models.smrt import smrt_utils
import shelve

def run_micro_model(my_track,
                    config):

    model_name = config.micro_model_name

    #############################################################################

    if model_name.lower() == 'smrt':

        # Create set of mediums suitable for SMRT

        mediums_list = [smrt_utils.prep_medium(snowpro, my_track.info['ice_type']) for snowpro in my_track.snowpro_list]

        if config.save_micro_input:

            shelf_dir = f"{config.output_dir}{config.media_f_name}_{config.year}"

            with shelve.open(shelf_dir, 'c') as d:
                d[str(my_track.track_no)] = mediums_list

        if config.run_micro_input:

            smrt_res = smrt_utils.run_media_series(mediums_list,
                                                   config.frequencies,
                                                   pol=['V', 'H'],
                                                   parallel=True)

            my_track = smrt_utils.process_SMRT_results(my_track,
                                                       config,
                                                       smrt_res)
    return(my_track)

    #############################################################################