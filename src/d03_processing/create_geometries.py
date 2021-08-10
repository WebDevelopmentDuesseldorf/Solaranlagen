import pandas as pd
from shapely.geometry import Point, Polygon
import geopandas as gpd

def polygonize(lat, lon, ns_deg, ew_deg):
    '''
    returns a polygon around a given location
    '''
    lat_delta = float(ns_deg)/2
    lon_delta = float(ew_deg)/2
    UL = Point(lon-lon_delta, lat+lat_delta)
    UR = Point(lon+lon_delta, lat+lat_delta)
    LR = Point(lon+lon_delta, lat-lat_delta)
    LL = Point(lon-lon_delta, lat-lat_delta)
    polygon = Polygon([UL,UR,LR,LL])
    return polygon

def create_polygons(df, id_in_tuple=True, id_col='index', name_for_col='geometry'):
    '''
    returns a dataframe with a polygon around each location, polygons will have the same size and border each other but not overlap
    :param df: dataframe that needs polygons
    :param id_col: name of the cols with id data, can also use index
    :param name_for_col: the name of the polygon column, defaults to 'geometry'
    :param id_in_tuple: if the id is saved in a tuple, False is not implemented
    '''
    # calculate the distance between the locations in degrees
    # get unique lat and lon values
    # check if the ids are stored in tuples
    if id_in_tuple:
        # get the tuples in a list or series
        if id_col == 'index':
            tuple_list = df.index
        else:
            tuple_list = df[id_col]
        # create empty lists for lat and lon values
        lat_unique, lon_unique=[],[]
        # iterate over ids to find unique lat and lon values
        for tup in tuple_list:
            if not tup[0] in lat_unique:
                lat_unique.append(tup[0])
            if not tup[1] in lon_unique:
                lon_unique.append(tup[1])
    else:
        print('pls store id in tuples, other options arent available yet')
    # sort the lists
    lat_unique.sort()
    lon_unique.sort()
    # compute distance between lat and lon points in degrees
    ns_deg = lat_unique[1]-lat_unique[0]
    ew_deg = lon_unique[1]-lon_unique[0]
    # create polygons
    df_with_polygons = df
    df_with_polygons[name_for_col] = df_with_polygons.apply(lambda x: polygonize(x.name[0],x.name[1],ns_deg,ew_deg),axis=1)
    return df_with_polygons

