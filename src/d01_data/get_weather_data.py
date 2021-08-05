import requests
import pandas as pd
import d00_utils.get_strings as getstr
import datetime as dt


# func: request weather data from API: get_weather_data
def get_weather_data(source='meteomatics',location='thueringen'):
    '''
    make request to a weather API, returns weather data in dataframe
    :param source: which API to use, only meteomatics is supported
    :param location: which location to use, available locations will be saved in /references/loc_dict.json
    '''
    
    # load location dict with test locations, will be implemented later: loc_dict
    loc_dict = {
        'garmisch':'47.4938417,11.0829',
        'thueringen':'51.6492842,9.8767193_50.2043467,12.6539178:2x3'
        }
    
    # define the use case
    use = source
    
    # load authentication data
    if use == 'meteomatics':
        with open('conf/base/meteomatics_auth.txt', 'r') as f:
            auth = f.read()
            print(auth)

    # check the source to request data
    if source == 'meteomatics':
        # get/set parts of the url
        date_str = getstr.get_datestr(use=use)
        param_str = getstr.get_paramstr(use=use)
        latlong_str = loc_dict[location]
        format_str = 'json?model=mix'
        # combine parts for full url: req_url
        req_url = 'https://'+auth+'@api.meteomatics.com'+'/'+date_str+'/'+param_str+'/'+latlong_str+'/'+format_str
        print('========='+req_url)
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
        print(packed_weather_data_df)

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
        print(weather_data_df.head())

        # change the type of the values in date column to datetime for better querying
        if not isinstance(weather_data_df.date.dtype, dt.datetime):
            # use meteodate2dt function to change the dtype of the date column
            # weather_data_df.date = weather_data_df.date.map(lambda x: dt.datetime.fromisoformat(x.replace('T',' ').replace('Z','')))weather_data_df.date = weather_data_df.date.map(lambda x: dt.datetime.fromisoformat(x.replace('T',' ').replace('Z','')))
            weather_data_df.date = weather_data_df.date.map(lambda x: meteodate2dt(x))

    else:
        print("other sources for weather are not supported, update get_weather_data.py first")
    return weather_data_df

# func: turn type of date col from meteomatics data into datetime: meteodate2dt
def meteodate2dt(datestr):
    datestr = datestr.replace('T',' ').replace('Z','')
    date_and_time = dt.datetime.fromisoformat(datestr)
    return date_and_time