from geopy import geocoders
import pandas as pd

def id_manage_df(df, id_col='id_tuple'):
    '''
    returns dataframe of all unique ids and columns to state block status and reason
    :param df: dataframe with ids
    :param id_col: which column to check for unique ids
    '''
    ids_unique = df[id_col].unique()
    ids_df = pd.DataFrame(data=ids_unique, columns=[id_col])
    ids_df['blocked'] = False
    ids_df['block reason'] = ''
    return ids_df

def id_allow_df(idmanage_df, id_col='id_tuple', block_col='blocked'):
    '''
    returns series of ids that are not blocked
    :param idmanage_df: dataframe with info about block status
    :param id_col: name of column with ids
    :param block_col: name of column with block status
    '''
    ids_allowed_df = idmanage_df[id_col][idmanage_df[block_col]==False]
    return ids_allowed_df
    
def update_id_block_df(df,
                    block_df_current, 
                    block_direction, 
                    block_value,
                    block_reason, 
                    id_col = 'id_tuple',
                    block_col = 'value',
                    insights = True
                    ):
    '''
    returns updated block_df with id, block status and reason
    :param df: dataframe with data to check for blocking
    :param block_df_current: dataframe with columns for id, block status and reason
    :param block_col: column to be checked
    :param block_direction: how to compare cell value to block value, sets what will be blocked, available settings: equal to, different from, less than, greater than, less eq, greater eq, outside of (needs geodata with fitting format)
    :param block_value: cell value will be compared to this
    :param block_reason: reason to be stated if an id is blocked
    :param insights: if True returns extended block reason'''
    
    # load dict with comparison methods, dict might be expanded, loading of dict not yet implemented
    comp_dict = {
        'equal to':(lambda cell, blockval: cell ==blockval),
        'greater than':(lambda cell, blockval: cell>blockval),
        'greater eq':(lambda cell, blockval: cell >=blockval),
        'less than':(lambda cell, blockval: cell<blockval),
        'less eq':(lambda cell, blockval: cell<=blockval),
        'different from':(lambda cell, blockval: cell != blockval),
        'outside of':(lambda cell, blockval: not blockval.contains(cell))
        }
    
    # get subset that is not already blocked: to_check_df
    to_check_df = df[df['id_tuple'].isin(block_df_current['id_tuple'])==False]
    # get subset of dataframe to block
    if block_direction == 'outside of':
        # if the block is related to geodata, use the geoblock function to block correctly
        block_df_additions = geoblock_id(df, block_col, block_value,id_col,block_direction)
        block_df_additions = block_df_additions[block_df_additions['blocked']==True]
        block_df_additions = block_df_additions[[id_col,block_col,'blocked']]
    else:
        block_df_additions = to_check_df[comp_dict[block_direction](to_check_df[block_col],block_value)==True]  # drop unnecessary columns
        block_df_additions = block_df_additions[[id_col,block_col]]
        # add block status and reason
        block_df_additions['blocked'] = True
    
    # if requested return extended reason for blocking
    if insights:
        block_df_additions['block reason'] = (block_reason + ' (' + block_col + ' is ' + block_direction + ' '+ str(block_value) +')')
    else:
        block_df_additions['block reason'] = block_reason

    # update current block_df
    block_df_updated = block_df_current.append(block_df_additions[[id_col,'blocked','block reason']])
    return block_df_updated

def updateblocks_idmanage_df(block_df, idmanage_df, id_col='id_tuple'):
    '''
    returns dataframe with all ids and updated block status, reason
    :param block_df: dataframe with block data
    :param idmanage_df: dataframe with ids and (outdated) block data
    :param id_col: name of column with ids, must be congruent in both dfs 
    '''
    # append block data at the end of the idmanage_df
    idmanage_df_updated = idmanage_df.append(block_df)
    # drop duplicates of ids, only keep the last occurence (which is the updated, appended block data)
    idmanage_df_updated.drop_duplicates(subset=id_col, keep='last', inplace=True)
    return idmanage_df_updated

def geoblock_id(df, geo_col,reference, id_col, block_direction):
    '''
    returns dataframe with blocked ids
    :param df: dataframe with geodata
    :param geocol: column name of the geometry column
    :param reference: reference polygon to check with
    :param id_col: column name of the id column
    :param block_direction: method to use for checking, only 'outside of' is supported
    '''
    if block_direction == 'outside of':
        geoblock_df = df
        geoblock_df['blocked'] = geoblock_df.apply(lambda x: not reference.contains(x[geo_col]), axis=1)
    else:
        print('other options for geoblocking arent implemented. pls update id_management.py')
    return geoblock_df