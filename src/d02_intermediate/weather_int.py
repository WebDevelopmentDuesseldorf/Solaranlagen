def est_paneltemp(air_temp, wind_speed, ventilated=True):
    '''
    returns estimated panel temperature
    :param air_temp: temperature of the air in C
    :param wind_speed: wind speed in beaufort
    :param ventilated: if the panel is naturally ventilated (at least 10cm distance to wall/ground)'''
    wind_cooling = wind_speed/2+.0625*wind_speed**2
    panel_temp = air_temp+40- wind_cooling
    return panel_temp