import datetime
import pandas as pd
import os
import numpy as np
# from smrt import make_snowpack, make_ice_column, make_model, sensor_list
from classes import snowpro
import smrt



# def print_preamble(filename):
#     '''Iterates through a .PRO file until it finds the line [DATA].
#     It then prints out the header with all the metainformation'''
#
#     with open(filename, "r") as f:
#         for line in enumerate(iter(f.readline, '[DATA]\n'), start=1):
#             print(line)


def read(track_no):
    '''Reads a .PRO file line by line,
    establishes which variable the line is for and adds that line to the relevant list'''

    # Which variables are you interested in?
    var_codes = ['0500','0501','0502','0503','0506','0512','0513','0515','0516','0535','0540','0541']

    # Set up the dictionary to be returned. Dictionary is organised by variable name.

    code_dict = pro_code_dict(return_all=True)

    variables = {}
    for var in var_codes:
        variables[code_dict[var]] = []

    # Open the .PRO file

    with open(f'Snowpack_files/{track_no}_SPLG.pro', "r") as f:

        # Iterate line by line

        for line in f.readlines():

            # If the variable code (first four chars) matches the variable of interest,
            # append that line to the list of lines

            if line[:4] in var_codes:
                    variables[code_dict[line[:4]]].append(line)

    # Now remove the header data

    for variable in variables.keys():

        variables[variable].pop(0)


    series_length = len(variables['Date'])

    profile_list = [snowpro_from_snapshot(x, variables) for x in range(series_length)]

    return (profile_list)


def pro_code_dict(code=False,return_all=False):

    """Set code = #### (string) to get name of variable.
    Alternatively set return_all=True to just return the full
    code dictionary"""

    if code == False and return_all == False:
        print('enter code=#### to get variable name or set return_all=True')
        return(0)

    pro_code_dict = {"0500": "Date",
                     "0501": "height [> 0: top, < 0: bottom of elem.] (cm)",
                     "0502": "element density (kg m-3)",
                     "0503": "element temperature (degC)",
                     "0504": "element ID (1)",
                     "0506": "liquid water content by volume (%)",
                     "0508": "dendricity (1)",
                     "0509": "sphericity (1)",
                     "0510": "coordination number (1)",
                     "0511": "bond size (mm)",
                     "0512": "grain size (mm)",
                     "0513": "grain type (Swiss Code F1F2F3)",
                     "0514": "grain type, grain size (mm), and density (kg m-3) of SH at surface",
                     "0515": "ice volume fraction (%)",
                     "0516": "air volume fraction (%)",
                     "0517": "stress in (kPa)",
                     "0518": "viscosity (GPa s)",
                     "0519": "soil volume fraction (%)",
                     "0520": "temperature gradient (K m-1)",
                     "0521": "thermal conductivity (W K-1 m-1)",
                     "0522": "absorbed shortwave radiation (W m-2)",
                     "0523": "viscous deformation rate (1.e-6 s-1)",
                     "0531": "deformation rate stability index Sdef",
                     "0532": "natural stability index Sn38",
                     "0533": "stability index Sk38",
                     "0534": "hand hardness either (N) or index steps (1)",
                     "0535": "optical equivalent grain size (mm)",
                     "0540": "bulk salinity (g/kg)",
                     "0541": "brine salinity (g/kg)",
                     "0601": "snow shear strength (kPa)",
                     "0602": "grain size difference (mm)",
                     "0603": "hardness difference (1)",
                     "0604": "ssi",
                     "0605": "inverse texture index ITI (Mg m-4)",
                     "0606": "critical cut length (m)", }
    if code != False:
        return(pro_code_dict[code])
    if return_all==True:
        return(pro_code_dict)

def series_from_line(variables, varname, index):
    """This function takes a string corresponding to a snowpack variable and returns a list of floats"""

    # First split the string apart at the commas

    series = variables[varname][index].split(",")

    # Get the variable code (the first entry in the list)

    varcode = int(series[0])

    # Get the number of actual datapoints (the second entry in the list)

    if varcode > 500:

        nvars = int(series[1])

        # Isolate the actual datapoints from the metadata

        datapoints = series[-nvars:]

        # Remove carriage return from the last datapoint if present
        if "\n" in datapoints[-1]:
            datapoints[-1] = datapoints[-1].replace('\n', '')

        # If we're looking at ice type data, we have to remove a weird graupel classification (bug?)
        if varcode == 513:
            return (list(map(float, datapoints[:-1])))

        # Return a list of floats for that variable in the snowpack

        else:
            return (list(map(float, datapoints)))

    else:

        return (datetime.datetime.strptime(series[1][:-1], "%d.%m.%Y %H:%M:%S"))

def snowpro_from_snapshot(entry, variables):

    """This function takes a dictionary of variables (a processed .Pro file) and returns two dataframes for a given
    point in time; one for ice and one for snow"""

    dataframe_dict = {}

    for varname in variables.keys():

        if varname == 'Date':

            my_datetime = series_from_line(variables, varname, entry)

        else:

            dataframe_dict[varname] = series_from_line(variables, varname, entry)

    df = pd.DataFrame(dataframe_dict)

    h_0 = df['height [> 0: top, < 0: bottom of elem.] (cm)'][0]
    diffheights = [height - h_0 for height in df['height [> 0: top, < 0: bottom of elem.] (cm)']]

    thickness = [-999]
    for i in range(len(diffheights) - 1):
        thickness.append((diffheights[i + 1] - diffheights[i])/100)

    df['thickness_m'] = thickness

    df = df.iloc[1:].copy()

    # Reverse order so it fits into SMRT
    df = df.iloc[::-1].copy()

    ice_df = df[df['grain type (Swiss Code F1F2F3)'] == 880]
    snow_df = df[df['grain type (Swiss Code F1F2F3)'] != 880]

    # Make an object with the dataframes, the date of the profile and thickness of ice and snow.
    snapshot = snowpro(ice_df, snow_df, my_datetime)

    return (snapshot)

def pro_stripper(track_no,
                 dir='SP_LG_Output/'):

    """This function """

    with open(f'{dir}{track_no}.pro', "r") as f:

        outF = open(f"{dir}{track_no}.spro", "w")

        # Iterate line by line

        var_codes = ['0500', '0501', '0502', '0503', '0506', '0512', '0513', '0515', '0516', '0535', '0540', '0541',
                     '0602']

        for line in f.readlines():

            if line[:4] in var_codes:
                outF.write(line)
                outF.write("\n")
        outF.close()

    os.system(f'rm {dir}{track_no}.pro')

def rd2(num):
    return (np.round(num, decimals=2))

