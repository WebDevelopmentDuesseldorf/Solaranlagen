import datetime as dt
import pickle
import pandas as pd

# func: create date string for requests to meteomatics API
# maybe possible to use later on for other requests, this is not yet planned but prepared
def get_datestr(start_auto=True, use='meteomatics',**dates):
    """ returns date_string to use for the meteomatics request
    :param start_auto: True = get the last two days, False = get passed dates
    :param start, end: sets specific date range
    :param use: check the use case for the str to generate correct format
    :kwargs dates: custom start, end dates and custom duration, end overwrites duration
    """
    if start_auto:
        # automatically set the dates to the dates available for free requests
        end_date = dt.date.today()
        start_date = end_date + dt.timedelta(days=-1)
        end_date = str(end_date)
        start_date = str(start_date)
    # if there is custom info for the dates, use it
    else:
        if 'start' in dates:
            start_date = dates['start']
            # turn str into datetime obj if not already
            start_date = dt.datetime.strptime(start_date,'%Y-%m-%d')
        # check if there's a given duration for which to check
        if 'days' in dates:
            # set end date corresponding to requested duration        
            end_date = start_date + dt.timedelta(days=dates['days']-1)
            # the -1 in timedelta might not be necessary, stems from old code, just left it there
        if 'end' in dates:
            end_date = dates['end']
            # turn str into datetime obj if not already
            end_date = dt.datetime.strptime(end_date,'%Y-%m-%d')

    # check the use case to get correct time zone value
    if use == 'meteomatics':
        # don't change the timezone
        time_zone = '02:00'

    # correct dates
    # turn str into datetime objs if they aren't
    if type(start_date) != dt.datetime:
        start_date = dt.datetime.strptime(start_date,'%Y-%m-%d')
    if type(end_date) != dt.datetime:
        end_date = dt.datetime.strptime(end_date,'%Y-%m-%d')
    # include end date
    end_date += dt.timedelta(days=1)
    # calculate time zone correction in hrs and mins
    time_zone = dt.datetime.strptime(time_zone, '%H:%M')
    # include time zone in dates
    start_date += dt.timedelta(hours=int(time_zone.strftime('%H')))
    end_date += dt.timedelta(hours=int(time_zone.strftime('%H')))
    # generate date string for request
    # generate components of date string
    start_day = start_date.strftime('%Y-%m-%d')
    start_time = start_date.strftime('%H:%M:%S.%f')[:-3]
    end_day = end_date.strftime('%Y-%m-%d')
    end_time = end_date.strftime('%H:%M:%S.%f')[:-3]
    time_zone = time_zone.strftime('%H:%M')

    # combine components for complete date string
    # generate the date string to fit with use case
    if use == 'meteomatics':
        date_str = start_day+'T'+start_time+'+'+time_zone+'--'+end_day+'T'+end_time+'+'+time_zone+':PT1H'

    return date_str

# create a string with parameters to requests from an API
def get_paramstr(use='meteomatics',custom_params=False,*params):
    '''
    :param use: use case for the parameters, changes the output format
    :param custom_params: if True use the kwargs, else use the standard params
    :args *params: list with all parameters to request
    '''
    # create list with standard parameters: standard_params
    standard_params = ['global radiation','direct radiation','diffuse radiation','sunshine','clouds','precipitation','temperature','snow depth', 'aerosols']


    # create dataframe for parameters, replace with loading the params_df.csv with all available parameters and use cases
    columns = ['parameter','unit','description']
    data = {
        'global radiation':['global_rad','W','global radiation'],
        'direct radiation':['direct_rad','W','direct radiation'],
        'diffuse radiation':['diffuse_rad','W', 'diffuse radiation'],
        'sunshine':['sunshine_duration_1h','min','minutes of sunshine per hour'],
        'clouds':['total_cloud_cover','p','relative cloud covered area of the sky'],
        'precipitation':['precip_1h','mm','precipitation in the last hour'],
        'temperature':['t_2m','C','temperature 2m above ground'],
        'wind speed':['wind_speed_10m','bft','wind speed in beaufort, 10m above ground'],
        'snow depth':['snow_depth','mm','snow depth in mm'],
        'aerosols':['total_aod_550nm','idx','percentage of light that is absorbed/reflected']
        }
    req_params_df = pd.DataFrame.from_dict(data=data, columns=columns, orient='index')
    
    #create empty string for parameters: param_str
    param_str = ''
    
    # check if a list of custom parameters is requested
    if custom_params:
        print("custom params aren't supported, update get_paramstr.py first")
        if use == 'meteomatics':
            for item in params:
                z=1
    else:
        if use == 'meteomatics':
            for param in standard_params:
                row = req_params_df.loc[param]
                param_str += row['parameter']+':'+row['unit']+','
            param_str = param_str[:-1]
    return param_str

def get_latlon_str(location,resolution,use='meteomatics'):
    '''
    returns the latlon string for the requested use case
    :param location: description of the location (eg City name)
    :param use: use case for the string, only meteomatics is implemented
    '''
    # load the location dict
    path = '../references/location_dictionary.pkl'
    with open(path,'rb') as f:
        loc_dict = pickle.load(f)
    # put info about location in variable: ld
    ld = loc_dict[location]
    # drop the polygon
    ld.pop('polygon',None)
    # compute the resolution part of the string 
    # estimate the width and height of the area in degrees and km²: wd, hd, wk, hk
    wd = ld['lon_max']-ld['lon_min']
    wk = wd*71
    hd = ld['lat_max']-ld['lat_min']
    hk = hd*111
    # compute the ratio between hk and wk
    r = hk/wk
    # compute the resolution of the area if it was a square
    res_sq = resolution/r
    # compute the number of data points per direction: wn, hn
    wn = round(res_sq**.5)
    hn = round(wn*r)
    # combine the values: res_str
    res_str = str(wn)+'x'+str(hn)
    print(res_str)
    # change type of all info to str    
    keys_values = ld.items()
    ld = {str(key): str(value) for key, value in keys_values}

    # create constructor dict with instructions on how to create the latlon str: con_dict
    con_dict={'meteomatics':ld['lat_max']+','+ld['lon_min']+'_'+ld['lat_min']+','+ld['lon_max']+':'+res_str}
    # construct the latlon string for the use case
    string = con_dict[use]
    return string