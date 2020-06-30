from snow_models import nesosim, degree_days


def simple_model(df):
    NE_snowpack = nesosim.nesosim_snowpack()
    DD_snowpack = degree_days.degree_days_snowpack()

    NE_depths = []
    NE_SWEs = []
    DD_depths = []
    DD_SWEs = []

    for prec, temp, wind in zip(df['cum_prec'],
                                df['t2m'],
                                df['wind_speed']):

        if temp < 273:
            NE_snowpack.accumulate(prec)

        if wind > 5:
            NE_snowpack.wind_pack()

        NE_depths.append(NE_snowpack.total('dep'))
        NE_SWEs.append(NE_snowpack.total('SWE'))
        DD_depths.append(DD_snowpack.total('dep'))
        DD_SWEs.append(DD_snowpack.total('SWE'))

    df['NE_depths'] = NE_depths
    df['NE_SWEs'] = NE_SWEs
    df['DD_depths'] = DD_depths
    df['DD_SWEs'] = DD_SWEs

    return (df)