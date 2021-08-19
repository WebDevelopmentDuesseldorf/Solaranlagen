from bisect import bisect

def tilt_options(summer_consumption, winter_consumption):
    '''
    returns options for the tilt as list
    :param summer_consumption: total energy consumption in july
    :param winter_consumption: total energy consumption in january
    '''
    # get the ratio between winter and summer consumption
    sw_ratio = summer_consumption/winter_consumption
    # save lists with corresponding ratios and tilt values
    ratio_list = [.5,.6,.7,.8,.9,1]
    tilt_list = [60,55,50,45,40,35,30,25,20]
    # find the position of the real ratio in the list, use the position to get suggestions for the tilt
    suggestion_pos = bisect(ratio_list,sw_ratio)
    tilt_suggestion = tilt_list[suggestion_pos+2]
    tilt_sug_lowest = tilt_suggestion-10
    tilt_sug_lower = tilt_suggestion-5
    tilt_sug_higher = tilt_suggestion+5
    tilt_sug_highest = tilt_suggestion+10
    # combine suggestions into a list
    tilt_opts = [tilt_sug_lowest, tilt_sug_lower, tilt_suggestion, tilt_sug_higher, tilt_sug_highest]
    return tilt_opts

def align_options(night_consumption, morning_consumption, afternoon_consumption, evening_consumption):
    '''
    returns a list with suggestions for the alignment
    :param night_consumption: amount of energy used during 00:00 and 06:00
    :param morning_consumption: amount of energy consumed durch 06:00 and 12:00
    :param afternoon_consumption: amount of energy consumed durch 12:00 and 18:00
    :param evening_consumption: amount of energy consumed durch 18:00 and 24:00
    '''
    # compute 'center of gravity' of time consumption phases
    cog = (night_consumption+2*morning_consumption+3*afternoon_consumption+4*evening_consumption)/(night_consumption+morning_consumption+evening_consumption+afternoon_consumption)
    # cog value can take values between 1 and 4, borders between phases correspond to 1.75, 2.5, 3.25
    # compute suggestions for the alignment
    align_main_sug = (cog-2.5)*60
    align_sug_lower = align_main_sug -10
    align_sug_lowest = align_main_sug -20
    align_sug_higher = align_main_sug +10
    align_sug_highest = align_main_sug +20
    # put suggestions into list
    align_opts = [align_sug_lowest, align_sug_lower, align_main_sug, align_sug_higher, align_sug_highest]
    return align_opts