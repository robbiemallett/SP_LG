import numpy as np

class snowpro:
    """A combined column of ice and snow with vertical profiles
    and variables such as date, snow height and ice thickness"""

    def __init__(self, iceframe, snowframe, datetime):

        self.iceframe = iceframe
        self.snowframe = snowframe
        self.datetime = datetime
        self.snowdepth = np.sum(snowframe['thickness_m'])
        self.snowdensity = np.mean(snowframe['element density (kg m-3)'])
        self.icethickness = np.sum(iceframe['thickness_m'])

        if snowframe.empty:
            self.sst, self.ist = np.nan, np.nan
        else:
            self.sst = snowframe['element temperature (degC)'].iloc[0]
            self.ist = snowframe['element temperature (degC)'].iloc[-1]
