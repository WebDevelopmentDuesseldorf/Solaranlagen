from math import pi, sin
from datetime import datetime

def consumption_by_date(date,winter_consumption,summer_consumption):
    '''
    returns estimate for the total energy consumption of a day in kWh, based on consumption profile
    '''
    # turn date into a fitting format if necessary
    if type(date) == str:
        date=datetime.strptime(date,"%Y-%m-%d")
    # rename some vars for easier qc
    w = winter_consumption
    s=summer_consumption
    x = date.month + date.day/30
    a=pi/6
    b=pi/4
    est = (w-s)/2*sin(a*x+b)+(w+s)/2
    return est/30

def consumption_ampm(daily_total, early_indicator, late_indicator):
    '''
    returns estimate for the am and pm consumption, unit will be the same as in given params
    :param daily_total: total consumption
    :param early_indicator: value or list of consumption
    :param late_indicator: value or list of consumption
    '''
    if type(early_indicator)==list:
        early_indicator = sum(early_indicator)
    if type(late_indicator)==list:
        late_indicator = sum(late_indicator)
    early_pct = early_indicator/(early_indicator+late_indicator)
    early_consumption = daily_total*early_pct
    late_consumption = daily_total-early_consumption
    return [[early_consumption,False],[late_consumption,True]]
    