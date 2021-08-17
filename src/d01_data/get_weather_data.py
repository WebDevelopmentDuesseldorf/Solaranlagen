import requests
import pandas as pd
from requests.api import get
import d01_data.get_strings as getstr
import datetime as dt
from os.path import dirname, abspath, normpath
import os
import math
import pickle
from math import radians, degrees, sin, cos, tan, asin, acos, atan
from ast import literal_eval as make_tuple

def getload_weather(process_id,source='meteomatics',location='thueringen', use_available=True,resolution=24):
    '''
    returns weather data in dataframe, defaults to loading locally saved data
    :param location: which location/region to analyze. only small range of options available
    :param source: which source to use for api requests. onyl meteomatics is implemented
    :param use_available: if locally saved data can be used, defaults to True
    :param process_id: the unique id for the data science process, used to find and save the correct files'''
    # load or request raw weather data
    # check if weather data for the current round exists
    path = '../data/01_raw/weather_data_raw' +'_' + process_id +'.csv'
    # error returned if weather_df is not set to a value before the if-else check
    weather_df=1
    if os.path.exists(path) and use_available:
        print('available weather data will be loaded. change use_available or process_id to request new data')
        # if weather data is available locally, load it
        weather_df = pd.read_csv(path)
        weather_df['date'] = pd.to_datetime(weather_df['date'], format="%Y-%m-%d %H:%M:%S.%f")
        # turn id_tuple col into tuples
        tups = weather_df['id_tuple']
        tups = tups.apply(lambda x: make_tuple(x))
        weather_df['id_tuple'] = tups
    else:
        print('weather data requested. pls stand by')
        # if weather isn't available locally, request it from the api
        weather_df = get_weather_data(source,location,resolution)
        weather_df.reset_index(inplace=True,drop=True)
        # also save it to reduce number of requests
        weather_df.to_csv(path, index=False)
    return weather_df



# func: request weather data from API: get_weather_data
def get_weather_data(source='meteomatics',location='thueringen',resolution=24):
    '''
    make request to a weather API, returns weather data in dataframe,
    df contains location, time, date and parameter with value
    :param source: which API to use, only meteomatics is supported
    :param location: which location to use, available locations will be saved in /references/loc_dict.json
    '''
    use = source
    
    # load authentication data
    if use == 'meteomatics':
        auth_path = 'C:/Users/sonny/Documents/Data Science/TechLabs Project/conf/base/meteomatics_auth.txt'
        with open(auth_path, 'r') as f:
            auth = f.read()

    # check the source to request data
    if source == 'meteomatics':
        # get/set parts of the url
        date_str = getstr.get_datestr(use=use)
        param_str = getstr.get_paramstr(use=use)
        latlong_str = getstr.get_latlon_str(location,resolution,use)
        format_str = 'json?model=mix'
        # combine parts for full url: req_url
        req_url = 'https://'+auth+'@api.meteomatics.com'+'/'+date_str+'/'+param_str+'/'+latlong_str+'/'+format_str
        print(req_url)
        # send the request
        res = requests.get(req_url)    
        # begin to format/unpack result and put into dataframe: packed_weather_data_df
        res_json = res.json()['data']
        #create dataframe from response (identified by location&parameter)
        packed_weather_data_df = pd.json_normalize(res_json,record_path=['coordinates'],meta=['parameter'])

        # create ID for packed_weather_data_df rows by combining lat & lon
        # create empty list for ids: id_series
        id_series = []
        # iterate over index of responses to create IDs
        for i in packed_weather_data_df.index:
            id = str(packed_weather_data_df.lat[i])+'/'+str(packed_weather_data_df.lon[i])
            id_series.append(id)
        # create list of unique ids: iq_unique
        id_unique = list(set(id_series))
        # turn series into new column
        packed_weather_data_df['id'] = pd.Series(id_series)

        # create ID tuple for packed_weather_data_df by combining lat & lon to a tuple
        # id_tuple is advantageous over id, needs less computing power to use
        # standard id row will get dropped in the future
       
        packed_weather_data_df['id_tuple'] = packed_weather_data_df.apply(lambda x: (x.lat, x.lon), axis=1)

        # fully unpack weather data into df: weather_data_df
        # list of parameters to be included in the final dataframe, use all columns besides dates, dates column will be unpacked in following code
        param_list = packed_weather_data_df.columns.drop('dates')
        
        # unpack dates col with explode and get functions
        weather_data_df = packed_weather_data_df.explode('dates')
        weather_data_df['value'] = weather_data_df.apply(lambda x: x.dates.get('value'), axis=1)
        weather_data_df['date'] = weather_data_df.apply(lambda x: x.dates.get('date'), axis=1) 
        # drop the unpacked dates column
        weather_data_df.drop('dates', axis=1, inplace=True)
        # reorder the columns for better readability
        col_order = ['date','parameter','value','lat','lon','id_tuple','id']
        weather_data_df = weather_data_df[col_order]

        # change the type of the values in date column to datetime for better querying
        if not isinstance(weather_data_df.date.dtype, dt.datetime):
            # use meteodate2dt function to change the dtype of the date column
            # weather_data_df.date = weather_data_df.date.map(lambda x: dt.datetime.fromisoformat(x.replace('T',' ').replace('Z','')))weather_data_df.date = weather_data_df.date.map(lambda x: dt.datetime.fromisoformat(x.replace('T',' ').replace('Z','')))
            weather_data_df.date = weather_data_df.date.map(lambda x: meteodate2dt(x))
            # change time data so the time zone is CEST (summer time in germany)
            if source  == 'meteomatics':
                weather_data_df['date'] += dt.timedelta(hours=2)

    else:
        print("other sources for weather are not supported, update get_weather_data.py first")
    return weather_data_df

# func: turn type of date col from meteomatics data into datetime: meteodate2dt
def meteodate2dt(datestr):
    datestr = datestr.replace('T',' ').replace('Z','')
    date_and_time = dt.datetime.fromisoformat(datestr)
    return date_and_time

def get_solar_irradiance(date):
    '''
    returns the estimated value of the solar irradiance on top of the atmosphere at a given date
    :param date: date as timestamp, datetime.date or datetime.datetime 
    '''
    # set parameters
    amp = 91/2824
    freq = math.pi/6
    v = math.pi/2-36/365
    e=2733/2824
    # get date variable
    date = date.month+date.day*12/365
    irradiance = (amp*math.sin(freq*date+v)+e)
    return irradiance
