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

def getload_weather(process_id,source='meteomatics',location='thueringen', use_available=True,resolution=24,min_hrs=7):
    '''
    returns weather data in dataframe, defaults to loading locally saved data, drops incomplete days
    :param location: which location/region to analyze. only small range of options available
    :param source: which source to use for api requests. onyl meteomatics is implemented
    :param use_available: if locally saved data can be used, defaults to True
    :param process_id: the unique id for the data science process, used to find and save the correct files
    :param resolution: resolution of request, will be decreased by roughly 50%
    :param min_hrs: minimum hours for a day to be included in analysis'''
    # load or request raw weather data
    # check if weather data for the current round exists
    path = '../data/01_raw/weather_' + process_id +'.pqt'
    # error returned if weather_df is not set to a value before the if-else check
    weather_df=1
    if os.path.exists(path) and use_available:
        print('available weather data will be loaded. change use_available or process_id to request new data')
        # if weather data is available locally, load it

        weather_df = pd.read_parquet(path)
        # drop rows corresponding to incomplete days
        # check if there's enough data to compute some half day values
        if weather_df.date.iloc[-1].hour < min_hrs:
            last_date = str(
                weather_df
                .date.iloc[-1]
                .date()
                - dt.timedelta(days=1))
            weather_df = (
                weather_df
                .set_index('date')
                .loc[:last_date]
                .reset_index()
            )
        
        weather_df['date'] = pd.to_datetime(weather_df['date'], format="%Y-%m-%d %H:%M:%S.%f")
        # turn id_tuple col into tuples
        weather_df['id_tuple'] = [make_tuple(x) for x in weather_df.id_tuple]
    else:
        print('weather data requested. pls stand by')
        # if weather isn't available locally, request it from the api
        weather_df = get_weather_data(source,location,resolution)
        weather_df.reset_index(inplace=True,drop=True)
        
        # drop rows corresponding to incomplete days
        # check if there's enough data to compute some half day values
        if weather_df.date.iloc[-1].hour < 7:
            last_date = str(
                weather_df
                .date.iloc[-1]
                .date()
                - dt.timedelta(days=1))
            weather_df = (
                weather_df
                .set_index('date')
                .loc[:last_date]
                .reset_index()
            )
            print('incomplete days dropped from weather data')

        # turn the id_tuple into a string
        # this is bad, but works for now
        weather_df.id_tuple = weather_df.id_tuple.astype('str')
        # also save it to reduce number of requests
        weather_df.to_parquet(path, index=False)
        weather_df.id_tuple = [make_tuple(x) for x in weather_df.id_tuple]
    return weather_df



def get_weather_data(source='meteomatics',location='thüringen',resolution=24):
    '''
    make request to a weather API, returns weather data in dataframe,
    df contains location, time, date and parameter with value
    :param source: which API to use, only meteomatics is supported
    :param location: which location to use, available locations will be saved in /references/loc_dict.json
    '''
    use = source
    
    # load authentication data
    if use == 'meteomatics':
        auth_path = 'C:/Users/Techie/Documents/soenke/Solaranlagen/conf/base/meteomatics_auth.txt'
        with open(auth_path, 'r') as f:
            auth = f.read()

        # get/set parts of the url
        date_str = getstr.get_datestr(use=use)
        param_str = getstr.get_paramstr(use=use)
        latlong_str = getstr.get_latlon_str(location,resolution,use)
        format_str = 'json?model=mix'
        # combine parts for full url: req_url
        req_url = 'https://'+auth+'@api.meteomatics.com'+'/'+date_str+'/'+param_str+'/'+latlong_str+'/'+format_str
        print(req_url)
        # send the request
        res = (
            requests
            .get(req_url)
            .json()['data']
        )    
        #create dataframe from response (identified by location&parameter)
        packed_weather_data_df = pd.json_normalize(res,record_path=['coordinates'],meta=['parameter'])

        # create ID tuple for packed_weather_data_df by combining lat & lon to a tuple
        # id_tuple is advantageous over id, needs less computing power to use       
        packed_weather_data_df['id_tuple'] = [
            (lat,lon)
            for lat, lon
            in zip(
                packed_weather_data_df.lat,
                packed_weather_data_df.lon
            )
        ]

        # fully unpack weather data into df: weather_data_df
        # list of parameters to be included in the final dataframe, use all columns besides dates, dates column will be unpacked in following code
        param_list = packed_weather_data_df.columns.drop('dates')
        
        # unpack dates col with explode and get functions
        weather_data_df = packed_weather_data_df.explode('dates')
        weather_data_df['value'] = [
            cell['value']
            for cell
            in weather_data_df.dates
        ]
        weather_data_df['date'] = [
            date.tz_localize(None) + dt.timedelta(hours=2)
            for date 
            in (pd.to_datetime([
                    cell['date']
                    for cell
                    in weather_data_df.dates
                ]))]
        # drop unpacked col
        weather_data_df.drop('dates', axis=1, inplace=True)
                
        # reorder the columns for better readability
        col_order = ['date','parameter','value','lat','lon','id_tuple']
        weather_data_df = weather_data_df[col_order]

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
    irradiance = (amp*math.sin(freq*date+v)+e)*1420
    return irradiance
