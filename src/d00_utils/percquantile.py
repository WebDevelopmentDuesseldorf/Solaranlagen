def percfind(lower, upper, quantile):
    '''
    returns the expected percentile of a quantile in data on a continuous scale
    :param lower: lowest value of the data
    :param upper: highest value of the data
    :param quantile: quantile that should be looked for
    '''
    if quantile-lower == 0:
        expected_percentile = 0
    else:
        expected_percentile = (upper-lower)/(quantile-lower)/100
    return expected_percentile