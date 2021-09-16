def est_paneltemp(air_temp, wind_speed, ventilated=True):
    '''
    returns estimated panel temperature
    :param air_temp: temperature of the air in C
    :param wind_speed: wind speed in beaufort
    :param ventilated: if the panel is naturally ventilated (at least 10cm distance to wall/ground)'''
    wind_cooling = wind_speed/2+.0625*wind_speed**2
    panel_temp = air_temp+40- wind_cooling
    return panel_temp

def loss_by_temp(temp, coeff=-0.4):
    '''
    returns the estimated loss (or gain) by cell temperature
    :param temp: temperature of the cell in deg C
    :param coeff: temperature coefficient of the panel in deg C
    '''
    loss = -(temp-25)*coeff/100
    return loss



def est_snowdepth_panel(snow_depth, paneltilt=35):
    '''
    returns estimation of snow thickness on the solar panel, tilt not yet implemented in calculation
    :param snow_depth: current snow depth at given location
    :param paneltilt: tilt of the solar panel
    '''
    est = snow_depth-5
    if est < 0:
        est =0
    return est


def loss_by_snow(snow_depth):
    '''
    returns estimated loss of energy output by snow cover
    :param snow_depth: depth of snow on the panel in cm
    '''
    if snow_depth > 5:
        loss=1
    else:
        loss = snow_depth*.2
    return loss

import numpy as np

def time_since_rain(
    index,
    precipitation,
    datetime_min,
    datetime_current,
    precipitation_for_cleaning = .3,
    rain_reference = 0
    ):
    '''
    returns time since last rain in hrs
    '''
    if precipitation >= precipitation_for_cleaning:
        hrs = 0
    elif datetime_min==datetime_current:
        hrs = rain_reference
    else:
        hrs = np.nan
    return hrs


def compute_aod_mean(df,idx,aod_col='total_aod_550nm',hrs_col='hrs_since_rain'):
    '''
    returns mean aod value since the last significant precipitation'''
    mean = (
        # filter the relevant slice from just after the last precipitation to the current datetime
        df.iloc[
            # just after last rain
            (idx - df.iloc[idx][hrs_col])+1
            # to current datetime
            :idx+1
         ]
        # look only at the col with aod data
        [aod_col]
         # compute the mean aod
         .mean())
    if not mean > 0:
        mean = 0 
    return mean


import math

def est_soil_loss_value(tilt, hrs_since, aod_mean):
    '''
    returns estimation of the loss by soiling of a solar panel
    '''
    if hrs_since > 0:
        # days since last precip: d
        d = hrs_since/24
        # estimate the maximum loss by soiling in standard conditions (AOD = .15): m
        m = 64.4*math.e**(-.0155*tilt)
        # loss by soiling after 14 days, standard conds: l14
        l14 = .604444*math.e**(-.012145*(tilt-340.954))
        # growth factor to include in exponent: b
        b=(-1/14)*math.log((m-l14)/m)*.9
        # function for loss percentage: f
        f = (m-m*math.e**(-b*d))*1.1
        # compute the correction of the loss by mean AOD: AOD_correction
        AOD_correction = aod_mean/.15

        # include AOD influence in f: est
        est = f*AOD_correction
    else:
        # if it just rained, estimate a loss of 0%
        est = 0

    return est/100


import math 

def est_soiling_loss_data(tilt, dust_precip_df, dust_col, precip_col, datetime_col,hrs_reference=48):
    '''
    //not fully implemented// returns dataframe with estimation for loss of output by dirt on the panel by the hour
    estimation is based on: (doi s41598-018-32291-8), (Dust effect on solar flat surfaces devices in Kuwait., 1985), (own estimations)
    :param tilt: tilt of the solar panel in degrees
    :param dust_precip_df: dataframe with info about dust in the atmosphere (AOD) and precipitation, must include datetime
    :param dust_col: col name for dust data, can be a list
    :param precip_col: col name for precipitaiton data
    :param date_col: col name for datetimes
    :param hrs_reference: estimated time since the last precipitation before the time covered by the df in hours
    '''
    # drop unnecessary cols, rename df for workflow: df
    df = dust_precip_df[[datetime_col,precip_col,dust_col]]
    # add new cols to dust_precip_df with reference values
    df['hrs_since_rain'] =-99
    df['aod_sum'] =0
    df['aod_mean'] = -99
    # set time passed since last significant precipitation to zero if it rains
    df['hrs_since_rain'] = df['hrs_since_rain'].mask(df[precip_col]>.5,0)
    # reset the index if necessary
    if df.index[0] != 0:
        df.reset_index(inplace= True,drop=True)
    # set time passed for the start datetime to the reference value if there's no precip at the start, add aod_sum too in that case
    if df['hrs_since_rain'][0] ==-99:
        df.loc[0,'hrs_since_rain'] = hrs_reference
        df.loc[0,'aod_sum'] = hrs_reference*df[dust_col][0]
        df.loc[0,'aod_mean'] = df[dust_col][0]

    # iterate over rows, set correct values for hrs_since and aod_sum
    # hrs_since = hours passed since last precipitation
    # aod_sum = sum of aod values since last precip (used for upcoming calculations)
    for i in df.index:
        if df['hrs_since_rain'][i] ==-99:
            # compute values for hrs_since and aod_sum
            hrs_since = df['hrs_since_rain'][i-1]+1
            aod_sum = df['aod_sum'][i-1] + df[dust_col][i]
            # put the values into the cells
            df.loc[i,'hrs_since_rain'] = hrs_since
            df.loc[i,'aod_sum'] = aod_sum
            # compute the mean aod since last precipitation
            df.loc[i,'aod_mean'] = aod_sum/hrs_since
            # print(i, df.loc[i,'aod_sum'], df.loc[i,'hrs_since'])
    
    # replace missing values in aod_mean with zero
    df.loc[df['aod_mean']==-99,'aod_mean'] = 0
    # compute the relative loss of energy output for each hour with the func 'est_soil_loss_value'

    df['soil loss pct'] = df.apply(lambda x: est_soil_loss_value(tilt,x['hrs_since_rain'],x['aod_mean'])/100,axis =1)

    return df


import json
import datetime as dt

# helper function to prepare the last rain datetime col for an ffill
def rain_prep(precip,datetime,dt_min,next=True):
    '''
    returns current datetime if raining or NaT else
    :param precip: amount of precipitation in the last hour in mm
    :param datetime: current datetime
    :param dt_min: earliest available datetime
    :param next: if True returns the next datetime with rain, if False returns the last datetime with rain'''
    # load reference values from settings

    # first load relevant settings
    with open('../references/settings/dev_settings.json','r') as f:
        settings = json.load(f)['losses']
    # look up amount of needed precipitation for self cleaning to work
    precipitation_for_cleaning = settings['self_clean_precip']
    # look up standard value of hours since the last self cleaning
    # standard value will be used if no data is available
    rain_reference = settings['rain_reference']

    if precip>=precipitation_for_cleaning:
        # if self cleaning took effect in the last hour, return the current datetime
        raintime = datetime
    elif (not next) and (datetime==dt_min):
        # if the last rain datetime is requested but the data is missing,
        # estimate the time since based on the rain reference value from the settings
        raintime = dt_min - dt.timedelta(hours=rain_reference)
    else:
        # return nan (this prepares ffills and bfills)
        raintime = np.nan
    return raintime