import requests

def elevation_carpet(lat, lon):
    '''
    returns dict of raw elevation data around a given location (area of approx 60m*60m with location as center), source: airmaps api
    :param lat: latitude
    :param lon: longitude
    '''
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

def elevation_path(lat, lon):
    '''
    returns list of elevation data from lat, lon to south, distance between data points ~30m
    '''
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
    path_res = requests.get(path_url).json().get('data')[0]
    return path_res

def elevation_point(lat, lon):
    '''
    returns elevation value for a specific location
    '''
    # set url bases
    loc_url_base = 'https://api.airmap.com/elevation/v1/ele?points='
    # create URL for location: loc_url
    loc_url = loc_url_base + str(lat)+','+str(lon)
    # requests location data, save as loc_res
    loc_res = requests.get(loc_url).json().get('data')[0]
    return loc_res