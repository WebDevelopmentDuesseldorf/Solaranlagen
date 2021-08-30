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

from d07_visualisation.create_geometries import polygonize

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
            # get sorted list with unique lat values
            lats = sorted(list(
                {
                    tup[0]
                    for tup
                    in df.index
                }))
            # get sorted list with unique lon values
            lons = sorted(list(
                {
                    tup[1]
                    for tup
                    in df.index
                }))

        else:
            print('Please make sure the id is stored in the index')

    else:
        print('pls store id in tuples, other options arent available yet')
    # compute distance between lat and lon points in degrees
    ns_deg = lats[1]-lats[0]
    ew_deg = lons[1]-lons[0]
    # create polygons
    df_with_polygons = df
    if id_col == 'index':
        df_with_polygons[name_for_col] = [
            polygonize(
                tup[0],
                tup[1],
                ns_deg,
                ew_deg)
            for tup
            in df_with_polygons.index
        ]
    else:
        df_with_polygons[name_for_col] = [
            polygonize(
                tup[0],
                tup[1],
                ns_deg,
                ew_deg)
            for tup
            in df_with_polygons[id_col]
        ]
    return df_with_polygons