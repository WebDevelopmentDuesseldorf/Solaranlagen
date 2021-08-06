from numpy import nan
import requests
from numpy.core.numeric import NaN
import pandas as pd
import math

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
    print(geo_url)
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

def get_address_data(tuple_list, ger_only=True):
    '''
    returns address data for multiple locations, return includes id_tuples
    :param tuple_list: list of coordinate tuples, must start with latitude
    :param ger_only: if true only addresses in germany are included
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
    print(address_data_df)
    # drop addresses outside of germany if requested
    if ger_only:
        address_data_df = address_data_df[address_data_df['country code']=='de']
    return address_data_df