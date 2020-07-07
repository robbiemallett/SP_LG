import pickle

def OIB_intersection_tracks(year):

    """ Loads a premade dictionary of the tracks for each year that end up under with OIB flights.

    This is a dictionary where each member is a set of track numbers (ints) required for cal/val with OIB. The function
    takes the year argument and gets the relevant set.

    #TODO remove absolute path reference

    Args:
        year: year of tracks

    Returns:
        set: set of ints representing the cal/val track numbers for each year

    """

    track_dict = pickle.load(open('/home/robbie/Dropbox/SP_LG/utility_files/tracks_for_cal.p', 'rb'))
    year_tracks = track_dict[year]
    return(year_tracks)

if __name__ == '__main__':
    OIB_intersection_tracks(2013)