from numpy import nan
import numpy as np
import requests
from numpy.core.numeric import NaN
import pandas as pd
import math
from itertools import product
from d07_visualisation.create_geometries import create_polygons
import pickle
import os
import geopandas as gpd
from geojson import Feature, Point, Polygon, MultiPolygon, FeatureCollection

def locator(lat,lon,relevant_fields=['postcode','city','county','state']):
    '''
    get address data corresponding to a pair of coordinates, returns a dict. does NOT return id.
    :param lat: latitude
    :param lon: longitude
    :param relevant_fields: address field to request, country code will always be returned
    '''
    # basic url for reverse locating
    geo_url_base = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&'
    # define params for request
    # construct request url
    geo_url = geo_url_base+'lat='+str(lat)+'&lon='+str(lon)
    # make request
    res = requests.get(geo_url)
    # get address data
    locator_address = res.json().get('address',NaN)
    # create empty dict to store unpacked address data
    address_data = {}
    if isinstance(locator_address, dict):
        # add country code to dict, check if in germany, drop otherwise
        address_data['country code'] = locator_address.get('country_code')
        if address_data['country code'] == 'de':
            # add data for relevant fields to dict, might be possible without loop
            for field in relevant_fields:
                address_data[field] = locator_address.get(field,'unknown')
            if address_data['city'] == 'unknown':
                address_data['city'] = locator_address.get('town','unknown')
                if address_data['city'] == 'unknown':
                    address_data['city'] = locator_address.get('municipality','unknown')
        else:
            # set all address values to NaN
            for field in relevant_fields:
                address_data[field] = NaN
    else:
        # if no dict is returned, set country code 
        address_data['country code'] = NaN
    return address_data

def get_address_data(tuple_list, ger_only=False):
    '''
    returns address data for multiple locations, return includes id_tuples
    :param tuple_list: list of coordinate tuples, must start with latitude
    :param ger_only: if true only addresses in germany are included, pls don't set True, setting is not fully implemented
    '''
    # drop duplicates in tuple list
    tuple_list = list(set(tuple_list))
    # create empty list to store addresses: address_data_list
    address_data_list=[]
    for tuple in tuple_list:
        # get address data for location, also keep tuple for identification
        address_dict = locator(tuple[0],tuple[1])
        address_dict['id_tuple'] = tuple
        address_data_list.append(address_dict)
    # turn list with data into dataframe: address_data_df
    address_data_df = pd.DataFrame(address_data_list)
    # drop addresses outside of germany if requested
    if ger_only:
        address_data_df = address_data_df[address_data_df['country code']=='de']
    return address_data_df

def get_address_grid(lat_min, lat_max,lon_min,lon_max,optimal_res=2000):
    '''
    returns a geodataframe with locations, polygons around them and the coutry code of the locations
    :param optimal_res: optimal number of polygons
    '''
    # create a fitting width and height of the grid
    # calculate range of latitude and longitude
    lat_delta = lat_max-lat_min
    lon_delta = lon_max-lon_min
    # get the total area in degrees²
    degree_res = lat_delta*lon_delta
    # calculate the length of a polygon side in degrees
    poly_size = (degree_res/optimal_res)**.5
    # calculate the number of poly next to and above each other
    poly_ontop_n = lat_delta/poly_size
    poly_sidebyside_n = lon_delta/poly_size
    
    # create polygons
    # create list of latlon values for the lower left point of the polygon
    lat_list = list(np.arange(lat_min+.5*poly_size,lat_max+.5*poly_size,poly_size))
    lon_list = list(np.arange(lon_min+.5*poly_size,lon_max+.5*poly_size,poly_size))
    # combine all possible latlon combinations into tuples
    center_list = list(product(*[lat_list,lon_list]))
    # get address data for each center
    center_address_df = get_address_data(center_list)

    # create a geometry column with polygons corresponding to the area around the location
    center_address_df = create_polygons(center_address_df, id_col='id_tuple')
    return center_address_df


def get_reference_data(location,get_all=False,use_available=True,threshold=0.0):
    '''
    returns a dict with a reference shape and the outermost point in each compass direction
    can return a list with dicts for each possible reference polygon
    there definitely is a more efficient way to solve the reference loading part, did not figure it out yet
    :param location: for which location to get the data
    :param get_all: set if you want a list with all fitting polygons, should rarely be necessary
    :param use_available: if True locally saved data will be accessed if possible
    :param threshold: lowers the resolution of the returned reference polygon, values between 0.0 and 0.1 might yield fine results. probably not necessary so far 
    '''
    # replace spaces in the location
    location = location.replace(' ',',')
    # set the path to load/save data
    path =  '../references/locations/'+location+'.pkl'
    # check if there's geodata to reference
    if os.path.exists(path):
        # load reference data if available
        with open(path,'rb') as f:
            res = pickle.load(f)
    else:
        # request geodata and save it for future reference
        url = 'https://nominatim.openstreetmap.org/search?q='+location+'&format=json&polygon_geojson=1&polygon_threshold'+str(threshold)
        res = requests.get(url).json()[0].get('geojson')     
        with open(path,'wb') as f:
            pickle.dump(res,f)
    # put the geo data in a gdf
    myfeat = Feature(geometry=res,properties={'location':location})
    col = FeatureCollection([myfeat])
    location_reference_df = gpd.GeoDataFrame.from_features(col['features'])
    # load the reference geometry
    reference = location_reference_df.geometry.iloc[0]

    # get the the border points of the smallest meridian aligned rectangle that contains the reference
    bounds = reference.bounds
    # reformat the bounds
    lon_min = bounds[0]
    lat_min =bounds[1]
    lon_max =bounds[2]
    lat_max =bounds[3]
    
    # roughly estimate the covered area, output a warning if below 1km²
    area = (lat_max-lat_min)*111*(lon_max-lon_min)*71
    if area <1:
        print("WARNING! You're looking at a area of less than 1km². Expect problems!")

    # create dict to return
    info = {'polygon':reference, 'lon_min':lon_min,'lon_max':lon_max,'lat_min':lat_min,'lat_max':lat_max}
    return info

def load_save_reference(location,force_update=False,create_new_save=False):
    '''
    returns reference polygon while adding the location data to the saved location reference dict
    :param location: city, region, country
    :param force_update: if True overwrites already saved reference
    :param create_new_save: if True overwrites whole saved dictionary
    '''
    ref = get_reference_data(location)
    # set the load/save path
    path = '../references/location_dictionary.pkl'
    # load the current dict if available
    if os.path.exists(path) and not create_new_save:
        with open(path,'rb') as f:
            loc_dict=pickle.load(f)
    else:
        loc_dict = {}

    # check if the location is already included in the dict
    if (not location in loc_dict) or force_update:
        # if the location is new, add the reference data
        loc_dict[location] = ref
        with open(path,'wb') as f:
            pickle.dump(loc_dict,f) 
    return ref['polygon']
        