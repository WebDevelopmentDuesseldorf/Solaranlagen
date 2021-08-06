import requests
from numpy.core.numeric import NaN

def locator(lat,lon,relevant_fields=['postcode','city','county','state']):
    '''
    get address data corresponding to a pair of coordinates, returns a dict
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
                address_data[field] = locator_address.get(field,NaN)
        else:
            # set all address values to NaN
            for field in relevant_fields:
                address_data[field] = NaN
    else:
        # if no dict is returned, set country code 
        address_data['country code'] = NaN
    return address_data