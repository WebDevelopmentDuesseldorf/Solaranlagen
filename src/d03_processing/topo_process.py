import bisect
import numpy as np

def tiltalign_loss_lowres(tilt, alignment, efficiency_df, lat=50):
    '''
    returns relative loss of power output by tilt and alignment over a year, does not include differences caused by different sun heights in different months
    :param tilt: tilt of the solar panel relative to the ground in degrees, positive values mean the panel faces south
    :param alignment: alignment of the solar panel relative to meridians in degrees
    :param efficiency_df: dataframe with efficiency values for different tilt, alignment values
    :param lat: latitude of a location where the loss should be estimated, not relevant in lowres version of the function
    '''
    # find all four neighbors to actual tilt-align-tuple
    # use absolute value of alignment
    alignment = abs(alignment)
    # find tilt neighbors first
    tilt_borders = efficiency_df.index
    # find positions of values closest to tilt (nearest greater and nearest lesser value)
    # check for positive tilt
    if tilt >0:
        tilt_pos_higher  = bisect.bisect(tilt_borders, tilt)
        tilt_pos_lower = tilt_pos_higher-1
    # if tilt is negative, use absolute value, but rotate on alignment axis to face north
    else: 
        tilt_pos_higher  = bisect.bisect(tilt_borders, abs(tilt))
        tilt_pos_lower = tilt_pos_higher-1
        alignment = 180-alignment

    # find align borders
    align_borders = efficiency_df.columns
    # find positions of values closest to alignment (nearest greater and nearest lesser value)
    align_pos_higher  = bisect.bisect(align_borders, alignment)
    align_pos_lower = align_pos_higher-1
    # check if alignment is equal to 180, if yes, change the position so the position fits the index
    if alignment == 180:
        align_pos_higher += -1
        align_pos_lower += -1

    # get subset dataframe to calculate expected efficiency, only including neighbors of tilt-align-tuple: subset_df
    subset_df = efficiency_df.iloc[tilt_pos_lower:tilt_pos_higher+1,align_pos_lower:align_pos_higher+1]
    # get average efficiency delta for a tilt shift
    eff_dif_tilt = np.mean(subset_df.iloc[1,:] - subset_df.iloc[0,:])
    eff_dif_align = np.mean(subset_df.iloc[:,1]- subset_df.iloc[:,0])
    # get difference between requested tuple and smallest neighbors
    tilt_diff = tilt - tilt_pos_lower*10
    align_diff = alignment - align_pos_lower*10
    # get estimated efficiency and loss percentage
    efficiency = subset_df.iloc[0,0] + tilt_diff/10*eff_dif_tilt + align_diff/10*eff_dif_align
    loss_pct = 1-efficiency
    return loss_pct
