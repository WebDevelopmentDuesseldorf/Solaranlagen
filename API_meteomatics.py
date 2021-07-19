from numpy.core.numeric import NaN
from numpy.lib.arraypad import _set_reflect_both
from pandas.core.frame import DataFrame
import requests
import datetime as dt
import pandas as pd
import json
from requests.api import request
from geopy.geocoders import Nominatim
import numpy as np

# load authentication data for meteomatics
with open('meteomatics.txt', 'r') as f:
    auth = f.read()

# set datetimes for request
#start and end time, you can change these
start_date = '2021-07-18'
end_date = '2021-07-19'
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
latlong_str = '55.099161,5.8663153_47.2701114,15.0418087:3x3'
# create full URL
req_format = 'json?model=mix'
req_url = 'https://'+auth+'@api.meteomatics.com'+'/'+date_str+'/'+param_str+'/'+latlong_str+'/'+req_format
# send request
print(req_url)
res = requests.get(req_url)
res_json = res.json()['data']

#create dataframe from response (identified by location&parameter)
df_response = pd.json_normalize(res_json,record_path=['coordinates'],meta=['parameter'])

# create ID for df_response rows by combining lat & lon
# create empty list for ids: id_series
id_series = []
# iterate over index of responses to create IDs
for i in df_response.index:
    id = str(df_response.lat[i])+'/'+str(df_response.lon[i])
    id_series.append(id)
# create list of unique ids: iq_unique
id_unique = list(set(id_series))
# turn series into new column
df_response['id'] = pd.Series(id_series)
# create multi index with id as outer and parameter as inner
# df_response.set_index(['id','parameter'], inplace=True)
# df_response.sort_index(inplace=True)

# locator function
def locator(lat,lon):
    # basic url for reverse locating
    geo_url_base = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&'
    # define params for request
    # construct request url
    geo_url = geo_url_base+'lat='+str(lat)+'&lon='+str(lon)
    # make request
    res = requests.get(geo_url)
    # get address data
    locator_address = res.json().get('address',NaN)
    # check if the adress is part of germany
    if isinstance(locator_address, dict):
        locator_country_code = locator_address.get('country_code')
        if locator_country_code == 'de':
            locator_city = locator_address.get('city',NaN)
            locator_plz = locator_address.get('postcode',NaN)
            locator_county = locator_address.get('county',NaN)
        else:
            locator_city, locator_plz, locator_county = NaN, NaN, NaN
    else:
        locator_country_code, locator_city, locator_plz, locator_county = NaN, NaN, NaN, NaN
    address_data = [locator_country_code, locator_city, locator_plz, locator_county]
    return address_data

# use list with unique ids to get address data for each id
# create empty df to combine ids and address data later on
address_df = pd.DataFrame()
# iterate over length of the list
for i in range(len(id_unique)):
    id = id_unique[i]
    # check if the id separator is as pos 9 (which should be the case)
    if id[9] == '/':
        seperator = 9
    # if the separator is at an unexpected position, find the correct position
    else: 
        seperator = id.find('/')
    # separate lat and lon by slicing the id at the separator position
    id_lat = id[0:seperator]
    id_lon = id[seperator+1:]
    # get address data as list corresponding to coordinates
    address = locator(id_lat, id_lon)
    # put address data and id into single row dataframe
    single_row = pd.DataFrame(np.array(address).reshape(-1,len(address)), index=[i])
    single_row['id'] = id
    single_row.columns = ['Country Code','City','PLZ','County','id']
    # append single row to complete address_df
    address_df = address_df.append(single_row)


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

# set index of address_df to id
address_df.set_index('id', inplace=True)
# drop locations not in germany
address_df_in_ger = address_df[address_df['Country Code']=='de']
# join df_unpacked and address_df on id
df_unpacked = df_unpacked.join(address_df_in_ger, on='id', how='inner')
# reset index
df_unpacked = df_unpacked.reset_index(drop=True)
print(df_unpacked.head(3))
