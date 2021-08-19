import numpy as np
import pandas as pd
import math

def carpet2df(carpet_res):
    '''
    returns dataframe from carpet, first row is north, first column is west
    :param carpet_res: result of carpet request
    :type carpet_res: dict
    '''
    elevation_df = pd.DataFrame.from_records(carpet_res.get('carpet'))
    # first columns refers to southmost datapoints, restructure for better interpretation, north to the top, south to the bottom
    elevation_df.sort_index(ascending=False, inplace=True)
    elevation_df.reset_index(inplace=True, drop=True)
    return elevation_df

def ground_grad_ns(elevation_df, ns_stepsize):
    '''
    returns the average gradient from south to north around a location
    :param elevation_df: dataframe with elevation values, first row must be north, first col must be west
    :param ns_stepsize: distance between data points in meters
    '''
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

def ground_grad_ew(elevation_df, ew_stepsize):
    '''
    returns average gradient from west to east around a location
    :param elevation_df: dataframe with elevation values, first row must be north, first col must be west
    :param ew_stepsize: distance between data points in meters
    '''
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


def carpet_characterics(carpet_res):
    '''
    returns dict with characteristics of an elevation carpet (area, expansion)
    :param carpet_res: result of carpet request to api
    :rtype: dict
    :return: dict with carpet characteristics
    '''
    # get actual borders of the carpet
    carpet_bounds = carpet_res.get('bounds')
    lat_min = carpet_bounds.get('sw')[0]
    lon_min = carpet_bounds.get('sw')[1]
    lat_max = carpet_bounds.get('ne')[0]
    lon_max = carpet_bounds.get('ne')[1]
    # approximate distance in compass directions in meters for carpet borders (formula "Verbesserte Methode" from: https://www.kompf.de/gps/distcalc.html)
    ns_extension = 111.12 * (lat_max-lat_min)*1000
    ew_extension = 111.12 * math.cos(math.radians((lat_max+lat_min)/2)) * (lon_max-lon_min)*1000
    # calc distance between data points: ns_stepsize, ew_stepsize
    ### step_n could also be calculated with coordinate extension & degree_delta
    # save elevation data points in carpet: carpet_data
    carpet_data = carpet_res.get('carpet')
    ns_step_n = len(carpet_data)-1
    ew_step_n = len(carpet_data[0])-1
    ns_stepsize = ns_extension/ns_step_n
    ew_stepsize = ew_extension/ew_step_n
    # approximate area in carpet with extensions
    area = ns_extension*ew_extension
    characteristics = {'area':area,'ns_extension':ns_extension,'ew_extension':ew_extension,'ns_stepsize':ns_stepsize,'ew_stepsize':ew_stepsize}
    return characteristics

def elevation_std(carpet_df):
    '''
    returns standard deviation of elevation in a carpet
    '''
    # empty list for all data points
    elevation_list = []
    # append sublists to ele_list
    for column in carpet_df.columns:
        elevation_list.append(carpet_df[column].tolist())
    # calculate std for elevation
    ele_std = np.std(elevation_list)
    return ele_std

def maxgrad_inpath(elevation_path, stepsize):
    '''
    returns the highest gradient on elevation_path,
    probably solved inefficiently (use of dataframes)
    :param elevation_path: elevation_path as returned by get_topo_data.elevation_path or saved in ele_path_*_pickled
    :param stepsize: distance between data points in meters
    '''
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
            grad = ele_diff/(stepsize*i)
            grad_list.append([i,grad])
    # turn list into dataframe, use stepcount as index
    grad_df = pd.DataFrame.from_records(grad_list, columns=['index','gradient'])
    grad_df.set_index('index',inplace=True)
    # get max gradient
    max_grad = grad_df.gradient.max()
    return max_grad

def grads_to_alignment(ns_grad, ew_grad):
    '''
    returns clockwise alignment relative to meridians based on north-south and east-west gradients, 0 degrees correspond to panel facing south
    :param ns_grad: gradient from south to north
    :param ew_grad: gradient from west to east
    '''
    if ew_grad ==0:
        if ns_grad < 0:
            alignment=180
        else:
            alignment =0
    elif ns_grad == 0:
        if ew_grad > 0:
            alignment=-90
        else:
            alignment=90
    else:
        alignment = math.degrees(math.acos((ns_grad/(ns_grad**2+ew_grad**2)**.5)))
        if ew_grad > 0:
            alignment = -alignment
    return alignment

def shademinutes_by_elevations():
    '''
    returns approximated value for shaded minutes by elevations, based on '''