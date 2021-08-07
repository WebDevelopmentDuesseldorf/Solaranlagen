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
                    block_col = 'value'
                    ):
    '''
    returns updated block_df with id, block status and reason
    :param df: dataframe with data to check for blocking
    :param block_df_current: dataframe with columns for id, block status and reason
    :param block_col: column to be checked
    :param block_direction: how to compare cell value to block value, sets what will be blocked, available settings (equal_to, different_from, less_than, greater_than, less_eq, greater_eq
    :param block_value: cell value will be compared to this
    :param block_reason: reason to be stated if an id is blocked'''
    
    # load dict with comparison methods, dict might be expanded, loading of dict not yet implemented
    comp_dict = {
        'equal_to':(lambda cell, blockval: cell ==blockval),
        'greater_than':(lambda cell, blockval: cell>blockval),
        'greater_eq':(lambda cell, blockval: cell >=blockval),
        'less_than':(lambda cell, blockval: cell<blockval),
        'less_eq':(lambda cell, blockval: cell<=blockval),
        'different_from':(lambda cell, blockval: cell != blockval)
        }
    
    # get subset of dataframe to block
    block_df_additions = df[comp_dict[block_direction](df[block_col],block_value)==True]
    # drop unnecessary columns
    block_df_additions = block_df_additions[[id_col,block_col]]
    # add block status and reason
    block_df_additions['blocked'] = True
    block_df_additions['block reason'] = (block_reason + ' (' + block_col + ' is ' + block_direction + ' '+ str(block_value) +')')
    
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
