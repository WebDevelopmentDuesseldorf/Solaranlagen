def est_paneltemp(air_temp, wind_speed, ventilated=True):
    '''
    returns estimated panel temperature
    :param air_temp: temperature of the air in C
    :param wind_speed: wind speed in beaufort
    :param ventilated: if the panel is naturally ventilated (at least 10cm distance to wall/ground)'''
    wind_cooling = wind_speed/2+.0625*wind_speed**2
    panel_temp = air_temp+40- wind_cooling
    return panel_temp

def est_snowthickness(snow_depth):
    '''
    returns estimation of snow thickness on the solar panel
    :param snow_depth: current snow depth at given location
    '''
    est = snow_depth-5
    if est < 0:
        est =0
    return est
