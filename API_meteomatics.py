from pandas.core.frame import DataFrame
import requests
import datetime as dt
import pandas as pd
import json
from requests.api import request
from geopy.geocoders import Nominatim

# load authentication data for meteomatics
with open('meteomatics.txt', 'r') as f:
    auth = f.read()

# set datetimes for request
#start and end time, you can change these
start_date = '2021-07-14'
end_date = '2021-07-15'
time_zone = '02:00'

# correct dates
# turn str into datetime objs
start_date = dt.datetime.strptime(start_date,'%Y-%m-%d')
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
date_str = start_day+'T'+start_time+'+'+time_zone+'--'+end_day+'T'+end_time+'+'+time_zone+':PT1H'

# choose requested parameters
# create dataframe for parameters
columns = ['parameter','unit','description']
data = {'sunshine':['sunshine_duration_1h','min','minutes of sunshine per hour'], 'clouds':['total_cloud_cover','p','relative cloud covered area of the sky']}
req_params_df = pd.DataFrame.from_dict(data=data, columns=columns, orient='index')
# turn dataframe into parameter string
param_str = ''
for i in req_params_df.index:
    param_str += req_params_df['parameter'][i]+':'+req_params_df['unit'][i]+','
param_str = param_str[:-1]

# choose locations (will use geopy 2.2.0 later on)
latlong_str = '50.938361,6.959974+51.2254018,6.7763137+51.4582235,7.0158171'
# create full URL
req_format = 'json?model=mix'
req_url = 'https://'+auth+'@api.meteomatics.com'+'/'+date_str+'/'+param_str+'/'+latlong_str+'/'+req_format
# send request
res = requests.get(req_url)
res_json = res.json()['data']

#create dataframe from response (identified by location&parameter)
df_response = pd.json_normalize(res_json,record_path=['coordinates'],meta=['parameter'])

# locator function
def locator(lat,lon):
    # basic url for reverse locating
    geo_url_base = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&'
    # define params for request
    # construct request url
    geo_url = geo_url_base+'lat='+str(lat)+'&lon='+str(lon)
    # make request
    res = requests.get(geo_url)
    city = res.json()['address']['city']
    return city

# create empty list: cities
cities = []
# iterate over df_response and add cities corresponding to coordinates
for i in df_response.index:
    city = locator(df_response.lat[i],df_response.lon[i])
    cities.append(city)
df_response['city'] = pd.Series(cities)

# list of parameters to be included in the final dataframe, use all columns besides dates, dates column will be unpacked in following code
param_list = df_response.columns.drop('dates')

# create empty df to unpack dates column
df_unpacked = pd.DataFrame()

# create df to unpack dates column
# iterate over df_response (identified by location&parameter) and create a df for packed data: df_step
for i in df_response.index:
    df_step = pd.DataFrame.from_dict(df_response.dates[i])
    # add needed columns to df_step, fill with correct values from df_response
    for k in param_list:
        df_step[k] = df_response[k][i]
    # print(df_step.head(2))
    # print('=======')
    # append df_step to df_unpacked to create complete unpacked dataframe
    df_unpacked = df_unpacked.append(df_step)
# reset misleading index
df_unpacked = df_unpacked.reset_index(drop=True)

print(df_unpacked)