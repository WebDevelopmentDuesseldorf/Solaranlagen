def albedo(lat=50,lon=10,date='2020-08-08',snow_thickness=0):
    '''
    //not fully implemented, always returns same value, pls update est_albedo.py// returns estimation for the albedo value in surrounding area
    defaults to .3, no matter the inputs
    :param lat: latitude in degs
    :param lon: longitude in degs
    :param date: date in a date format (timestamp, date or datetime)
    :param snow_thickness: snow in cm, defaults to zero
    '''
    if snow_thickness > 5:
        al=.8
    else:
        al = .2+snow_thickness*.1
    return al