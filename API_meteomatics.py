from numpy.core.numeric import NaN
from numpy.lib.arraypad import _set_reflect_both
from numpy.lib.utils import byte_bounds
from pandas.core.frame import DataFrame
import requests
import datetime as dt
import pandas as pd
import json
from requests.api import request
from geopy.geocoders import Nominatim
import numpy as np
import math
import bisect
from scipy.stats import zscore

# load authentication data for meteomatics
with open('meteomatics.txt', 'r') as f:
    auth = f.read()

# choose to set start date of weather request automatically
start_auto = True
# set start date
if start_auto:
    end_date = dt.date.today()
    start_date = end_date + dt.timedelta(days=-1)
    end_date = str(end_date)
    start_date = str(start_date)
else:
    # set datetimes for request
    # start and end time, you can change these
    start_date = '2021-07-27'
    end_date = '2021-07-28'
# don't change the timezone
time_zone = '02:00'

# correct dates
# turn str into datetime objs if they aren't
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
latlong_str = '51.6492842,9.8767193_50.2043467,12.6539178:20x20'
# create full URL
req_format = 'json?model=mix'
req_url = 'https://'+auth+'@api.meteomatics.com'+'/'+date_str+'/'+param_str+'/'+latlong_str+'/'+req_format
# send request
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
def locator(lat,lon,relevant_data=['postcode','city','county','state']):
    # basic url for reverse locating
    geo_url_base = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&'
    # define params for request
    # construct request url
    geo_url = geo_url_base+'lat='+str(lat)+'&lon='+str(lon)
    # make request
    res = requests.get(geo_url)
    # get address data
    locator_address = res.json().get('address',NaN)
    # create empty list to store unpacked address data
    address_data = []
    # check if the request returned packed address data
    if isinstance(locator_address, dict):
        # check the country, drop everything outside of germany
        locator_country_code = locator_address.get('country_code')
        if locator_country_code == 'de':
            # add country code to address_data
            address_data.append(locator_country_code)
            # iterate over requested data fields, append corresponding value to list address_data 
            for field in relevant_data:
                address_data.append(locator_address.get(field,NaN))
        else:
            # set all address values to NaN
            address_data.append(locator_country_code)
            for field in relevant_data:
                address_data.append(NaN)
    else:
        # set country code to NaN
        address_data.append(NaN)
        # set additional requested fields to NaN
        for i in range(len(relevant_data)):
            address_data.append(NaN)
    # return complete list with adress data
    return address_data

# create list with requested address fields and prepare readable column names accordingly
# create list with address fields to request: fields
fields = ['postcode','city','county','state']
# dictionary to turn the requested fields into readable column names: fields_dict
fields_dict = {'postcode':'PLZ','city':'Stadt','county':'County','state':'Bundesland'}
# use fields and fields_dict to create list for column names: col_names
# create list with fixed first name
col_names = ['Country Code']
# iterate over fields to fill col_names
for i in range(len(fields)):
    col_names.append(fields_dict[fields[i]])
# add id to col names
col_names.append('id')

# use list with unique ids to get address data for each id
# create empty df to combine ids and address data later on
address_df = pd.DataFrame()
# iterate over length of the id list
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
    address = locator(id_lat, id_lon, relevant_data=fields)
    # put address data and id into single row dataframe
    single_row = pd.DataFrame(np.array(address).reshape(-1,len(address)), index=[i])
    single_row['id'] = id
    single_row.columns = col_names
    # append single row to complete address_df
    address_df = address_df.append(single_row)

# gather data to judge hilliness, tilts, alignments
# func: get raw data from airmap api for an area around a location: elevation_carpet
### returns dict with all relevant data
def elevation_carpet(lat,lon):
    # set degree delta for best resolution (found in airmaps documentation)
    degree_delta = float(0.000277778)
    # turn given vars into float
    loc_lat = float(lat)
    loc_lon = float(lon)
    # set url bases
    carpet_url_base = 'https://api.airmap.com/elevation/v1/ele/carpet?points='
    # create corner points for surrounding area
    SW_lat = str(loc_lat-degree_delta)
    SW_lon = str(loc_lon-degree_delta)
    NE_lat = str(loc_lat+degree_delta)
    NE_lon = str(loc_lon+degree_delta)
    # create URL for surrounding area: carpet_url
    carpet_url = carpet_url_base + SW_lat+','+SW_lon+','+NE_lat+','+NE_lon
    # requests carpet data, save as carpet_res
    carpet_res = requests.get(carpet_url).json().get('data')
    return carpet_res

# func: get raw data from airmap api for a southward path from a location: elevation_path
def elevation_path(lat, lon):
    # set degree delta for best resolution (found in airmaps documentation)
    degree_delta = float(0.000277778)
    # turn given lat into float
    loc_lat = float(lat)
    # set url bases
    carpet_url_base = 'https://api.airmap.com/elevation/v1/ele/path?points='
    # create corner points for surrounding area
    start_lat = str(loc_lat)
    end_lat = str(loc_lat-100*degree_delta)
    # create URL for surrounding area: carpet_url
    path_url = carpet_url_base + start_lat+','+str(lon)+','+end_lat+','+str(lon)
    # requests carpet data, save as carpet_res
    path_res = requests.get(path_url).json().get('data')
    return path_res

# func: get raw data from airmap api for a specific location: elevation_point
### returns single elevation value (from nearest available location relative)
def elevation_point(lat, lon):
    # set url bases
    loc_url_base = 'https://api.airmap.com/elevation/v1/ele?points='
    # create URL for location: loc_url
    loc_url = loc_url_base + str(lat)+','+str(lon)
    # requests location data, save as loc_res
    loc_res = requests.get(loc_url).json().get('data')

# func: get average north-south-gradient of the ground surrounding location: ground_grad_ns
def ground_grad_ns(elevation_df, ns_stepsize):
    ### ns_grad should be close to tan(35°) = 0.70021, according to "https://www.rechnerphotovoltaik.de/photovoltaik/voraussetzungen/dachneigung"
    # first calculate gradient between ns neighbor data pairs
    # create empty df for ns gradient
    # set size of gradient dataframe
    ew_range = range(len(elevation_df.columns))
    ns_range = range(len(elevation_df.index)-1)
    ns_grad_df = pd.DataFrame(index=ns_range, columns=ew_range)
    # begin with westmost data points
    for ew_id in ew_range:
        # begin with northmost data point
        for ns_id in ns_range:
            # calculate elevation change: ele_delta
            ele_delta = (elevation_df[ew_id][ns_id]-elevation_df[ew_id][ns_id+1])
            # calc the gradient
            grad = ele_delta/ns_stepsize
            # put gradient into gradient dataframe
            ns_grad_df[ew_id][ns_id] = grad
    # calculate average ns-gradient around the location
    grad_avg = np.mean(ns_grad_df.values.tolist())
    return grad_avg

# func: get gradient data in east and west direction: ground_grad_ew
def ground_grad_ew(elevation_df, ew_stepsize):
    # first calculate gradient between east-west neighbor data pairs
    ew_range = range(len(elevation_df.columns)-1)
    ns_range = range(len(elevation_df.index))
    ew_grad_df = pd.DataFrame(index=ns_range, columns=ew_range)
    # begin with westmost data points
    for ew_id in ew_range:
        # begin with northmost data point
        for ns_id in ns_range:
            # calculate elevation change: ele_delta
            ele_delta = (elevation_df[ew_id][ns_id]-elevation_df[ew_id+1][ns_id])
            # calc the gradient
            grad = ele_delta/ew_stepsize
            # put gradient into gradient dataframe
            ew_grad_df[ew_id][ns_id] = grad
    # calculate average ns-gradient around the location
    grad_avg = np.mean(ew_grad_df.values.tolist())
    return grad_avg


# func: standard deviation of elevation in area around location: ele_std
def ele_std(carpet_data):
    # calculate standard deviation of elevation in carpet
    # empty list for all data points
    ele_list = []
    # append sublists to ele_list
    for sublist in carpet_data:
        ele_list.append(sublist)
    # calculate std for elevation
    ele_std = np.std(ele_list)
    return ele_std

# func: calculate key characteristics of carpet for easier access and interpretation: carpet_characteristics
### returns area in m², expansions in m
def carpet_characterics(carpet_res):
    # get actual borders of the carpet
    carpet_bounds = carpet_res.get('bounds')
    lat_min = carpet_bounds.get('sw')[0]
    lon_min = carpet_bounds.get('sw')[1]
    lat_max = carpet_bounds.get('ne')[0]
    lon_max = carpet_bounds.get('ne')[1]
    # approximate distance in compass directions in meters for carpet borders (formula "Verbesserte Methode" from: https://www.kompf.de/gps/distcalc.html)
    ns_extension = 111.3 * (lat_max-lat_min)*1000
    ew_extension = 111.3 * math.cos(math.radians((lat_max+lat_min)/2)) * (lon_max-lon_min)*1000
    # calc distance between data points: ns_stepsize, ew_stepsize
    ### step_n could also be calculated with coordinate extension & degree_delta
    # save elevation data points in carpet: carpet_data
    carpet_data = carpet_res.get('carpet')
    ns_step_n = len(carpet_data)
    ew_step_n = len(carpet_data[0])
    ns_stepsize = ns_extension/ns_step_n
    ew_stepsize = ew_extension/ew_step_n
    # approximate area in carpet with extensions
    area = ns_extension*ew_extension
    return area, ns_extension, ew_extension, ns_stepsize, ew_stepsize

# function to calculate min and max values for sun elevation during noon
# max is maximum sun elevation during summer, min is maximum sun elevation during winter
# formula from "https://www.mpptsolar.com/de/optimale-ausrichtung-dachneigung-solaranlage.html"
def minmax_sunheight(lat):
    max = 90-(lat-23)
    min = 90-(lat+23)
    avg = 90-lat
    return min, avg, max 

# function to find best tilt for solar panel
# summer, yearround, winter return tuple of best tilts when the energy consumption is the highest in the corresponding season
# first value is highest tilt, for energy consumption close to winter solstice, second value is for energy consumption close to summer solstice 
def besttilt(lat):
    min, avg, max = minmax_sunheight(lat)
    winter = [90-min,90-min-12]
    yearround = [90-avg-6,90-avg+6]
    summer = [90-max,90-max+12]
    return winter, yearround, summer

# function to find expected percentile delta in continuous categorical data
def percfind(lower, upper, quantile):
    if quantile-lower == 0:
        expected_percentile = 0
    else:
        expected_percentile = (upper-lower)/(quantile-lower)/100
    return expected_percentile


# load table with loss data by tilt and alignment into dataframe
path = 'Efficiency of solar panels by tilt and alignment in germany.xlsx'
efficiency_df = pd.read_excel(path, index_col=0)
# only use highest efficiency alignment (panel facing south)
efficiency_tosouth_df = efficiency_df[0]

# define function to calculate expected loss by alignment of the solar panels if mounted on the ground
### not yet included: tilt in ew direction, differences by latitude
def expect_loss_tilt(tilt, lat=50):
    # find neighbors so that tilt lies between them
    # get list of index of efficiency_df
    tilt_borders = efficiency_tosouth_df.index
    # find positions of values closest to tilt (nearest greater and nearest lesser value)
    tilt_pos_higher  = bisect.bisect(tilt_borders, tilt)
    tilt_pos_lower = tilt_pos_higher-1
    # get exact tilts from those positions
    tilt_lower, tilt_higher = efficiency_df.index[[tilt_pos_lower, tilt_pos_higher]]
    efficiency_lower, efficiency_higher = efficiency_tosouth_df[[tilt_lower, tilt_higher]]
    # calculate efficiency difference between borders: efficiency_diff
    efficiency_diff = efficiency_higher-efficiency_lower
    # expected efficiency by expected percentile
    efficiency = efficiency_lower+efficiency_diff*percfind(tilt_lower, tilt_higher, tilt)
    # calc loss percentage
    loss_pct = 1-efficiency
    return loss_pct

# func: loss by alignment and tilt if built on ground: expect_loss_aligntilt
### not included: impact of latitude
def expect_loss_aligntilt(tilt, alignment, lat=50):
    # find all four neighbors to actual tilt-align-tuple
    # use absolute value of alignment
    alignment = abs(alignment)
    # find tilt neighbors first
    tilt_borders = efficiency_df.index
    # find positions of values closest to tilt (nearest greater and nearest lesser value)
    # check for positive tilt
    if tilt >0:
        tilt_pos_higher  = bisect.bisect(tilt_borders, tilt)
        tilt_pos_lower = tilt_pos_higher-1
    # if tilt is negative, use absolute value, but rotate on alignment axis to face north
    else: 
        tilt_pos_higher  = bisect.bisect(tilt_borders, abs(tilt))
        tilt_pos_lower = tilt_pos_higher-1
        alignment = 180-alignment

    # find align borders
    align_borders = efficiency_df.columns
    # find positions of values closest to alignment (nearest greater and nearest lesser value)
    align_pos_higher  = bisect.bisect(align_borders, alignment)
    align_pos_lower = align_pos_higher-1
    # check if alignment is equal to 180, if yes, change the position so the position fits the index
    if alignment == 180:
        align_pos_higher += -1
        align_pos_lower += -1
    print(alignment)

    # get subset dataframe to calculate expected efficiency, only including neighbors of tilt-align-tuple: subset_df
    subset_df = efficiency_df.iloc[tilt_pos_lower:tilt_pos_higher+1,align_pos_lower:align_pos_higher+1]
    # get average efficiency delta for a tilt shift
    eff_dif_tilt = np.mean(subset_df.iloc[1,:] - subset_df.iloc[0,:])
    eff_dif_align = np.mean(subset_df.iloc[:,1]- subset_df.iloc[:,0])
    # get difference between requested tuple and smallest neighbors
    tilt_diff = tilt - tilt_pos_lower*10
    align_diff = alignment - align_pos_lower*10
    # get estimated efficiency and loss percentage
    efficiency = subset_df.iloc[0,0] + tilt_diff/10*eff_dif_tilt + align_diff/10*eff_dif_align
    loss_pct = 1-efficiency
    return loss_pct

# func: get the most relevant elevation south of a location which might cast a significant shadow: southern_ele
### functions checks 3km in southern direction, returns highest gradient in that path
def southern_ele(elevation_path, ns_stepsize):
    # empty list to store gradient data
    grad_list = []
    # save value of location to look at: compare_to
    compare_to = elevation_path[0]
    # iterate over number of path data points
    for i in range(len(elevation_path))[1:]:
        # get elevation difference: ele_diff, check if greater than start elevation
        ele_diff = - compare_to + elevation_path[i]
        if ele_diff > 0:
            # calc gradient and save
            grad = ele_diff/(ns_stepsize*i)
            grad_list.append([i,grad])
    # turn list into dataframe, use stepcount as index
    grad_df = pd.DataFrame.from_records(grad_list, columns=['index','gradient'])
    grad_df.set_index('index',inplace=True)
    # get max gradient
    max_grad = grad_df.gradient.max()
    return max_grad

# func: turn the ns and ew gradients into alignment: grad_to_alignment
def grad_to_alignment(ns_grad, ew_grad):
    alignment = math.degrees(math.atan(ew_grad/ns_grad))
    return alignment

#  create dataframe with data about hilliness
# func: combine data regarding topography: topo
def topo(lat,lon):
    # request elevation data around location: carpet_res
    carpet_res = elevation_carpet(lat, lon)
    # save elevation data points in carpet: carpet_data
    carpet_data = carpet_res.get('carpet')
    # create dataframe for better access: elevation_df
    elevation_df = pd.DataFrame.from_records(carpet_data)
    # first columns refers to southmost datapoints, restructure for better interpretation, north to the top, south to the bottom
    elevation_df.sort_index(ascending=False, inplace=True)
    elevation_df.reset_index(inplace=True, drop=True)
    # get characteristics of the carpet
    carpet_area, carpet_ns_extension, carpet_ew_extension, ns_stepsize, ew_stepsize = carpet_characterics(carpet_res)
    # get value for std of elevation around location
    ele_stdev_value = ele_std(carpet_data)
    # get average ns_gradient around location
    ns_grad_avg = ground_grad_ns(elevation_df, ns_stepsize)
    tilt_deg = math.degrees(math.tan(ns_grad_avg))
    # get expected loss by tilt if build on ground
    tilt_loss = expect_loss_tilt(tilt_deg)
    # get gradient data in east and west direction
    ew_grad_avg = ground_grad_ew(elevation_df,ew_stepsize)
    align_deg = grad_to_alignment(ns_grad_avg,ew_grad_avg)
    # get expected loss by tilt & alignment
    tiltalign_loss = expect_loss_aligntilt(tilt_deg,align_deg)
    # check for elevations south of location: gradient_to_south
    path_data = elevation_path(lat,lon)[0].get('profile')
    degrees_to_south = southern_ele(path_data, ns_stepsize)
    # calculate degrees of elevation
    elevation_degrees_south = math.degrees(math.atan(degrees_to_south))
    # return all gathered data
    # set column names
    # topo_columns = ['id','std of elevation', 'north-south gradient', 'north-south tilt', 'east_west gradient','natural alignment','tilt align loss', 'elevation degrees to south']
    # set description for each column
    topo_columns_descr = []
    # combine date to dict: topo_data_dict
    id = str(lat)+'/'+str(lon)
    topo_data_dict = {
                        'id':id, 
                        'std of elevation':ele_stdev_value, 
                        'north-south gradient':ns_grad_avg, 
                        'north-south tilt':tilt_deg, 
                        'east_west gradient':ew_grad_avg, 
                        'natural alignment':align_deg, 
                        'tilt align loss':tiltalign_loss, 
                        'elevation degrees to south':degrees_to_south
                    }   
    return topo_data_dict

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
# get IDs in germany to gather additional data
ids_germany = df_unpacked.id.unique()

# gather additional data
# generate empty list to collect data_dicts
dict_list = []
# iterate over locations in germany to gather additional data
for i in range(len(ids_germany)):
    id = id_unique[i]
    # check if the id separator is as pos 9 (which should be the case)
    if id[9] == '/':
        seperator = 9
    # if the separator is at an unexpected position, find the correct position
    else: 
        seperator = id.find('/')
    # separate lat and lon by slicing the id at the separator position
    ger_id_lat = id[0:seperator]
    ger_id_lon = id[seperator+1:]
    # actually gather data
    # get topographic key values with topo call
    # append result to dict_list
    dict_list.append(topo(ger_id_lat,ger_id_lon))
# put topo data into DataFrame, use id as index
ger_data = pd.DataFrame.from_dict(dict_list)
ger_data.set_index('id',inplace=True)
# join data on topo, address and weather
# join df_unpacked and ger_data on id
df_unpacked = df_unpacked.join(ger_data, on='id', how='inner')
# reset index
df_unpacked = df_unpacked.reset_index(drop=True)

# create dataframe with simple data to turn into map: map_df
map_df = df_unpacked.loc[:,['id','lat','lon','PLZ','north-south tilt','tilt align loss']]
map_df.drop_duplicates(subset='id',inplace=True)
map_df['tilt align percent'] = map_df['tilt align loss']*100
map_df[map_df.columns[4:7]] = round(map_df[map_df.columns[4:7]],2)
map_df['z_score'] = zscore(map_df['tilt align percent'])
map_df.to_csv('testdata_for_map.csv')

