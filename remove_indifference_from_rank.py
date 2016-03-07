# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 19:44:26 2016

@author: Dalton
"""

#imports
import pandas as pd
import numpy as np


def remove_rank_indifferences(group, ranker='_exp_rank'):
#    hard copy the group so that it resets every loop
    temp_group = group.copy()
#    make an empty DF to concatonate the many ranking on 
    multiple_rakning_DF = pd.DataFrame()
#    Get a DF of the options and thier ranks
    # What Rank should I use? _exp_rank or _imp_rank
    ranker = ranker
    option1s = temp_group.loc[:,['opt1'+ranker, 'option1']].copy()
    option1s.rename(columns={'opt1'+ranker: 'rank', 'option1': 'option_code'}, inplace=True)
    option2s = temp_group.loc[:,['opt2'+ranker, 'option2']].copy()
    option2s.rename(columns={'opt2'+ranker: 'rank', 'option2': 'option_code'}, inplace=True)
    options = pd.concat([option1s, option2s])
    unique_options = options.drop_duplicates(['option_code'])
#    make a backup copy of the original ranking. 
    unique_options['original_rank'] = unique_options['rank']
    for option_index in unique_options[unique_options['rank'] == 1].index:
        # let option_index have  temp_rank 1 
        temp_group.loc[temp_group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 1
        temp_group.loc[temp_group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 1
#        and make the rank for all other options that iser to be 1, in to 2
        #I'm sorry that the line below is almost unreadable. 
        unique_options.loc[unique_options[unique_options['rank'] == 1].index[unique_options[unique_options['rank'] == 1].index != option_index],'rank'] = 2
        for option_index in unique_options[unique_options['rank'] == 2].index:
            # let option_index have  temp_rank 1 
            temp_group.loc[temp_group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 2
            temp_group.loc[temp_group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 2
    #        and make the rank for all other options that iser to be 1, in to 2
            #I'm sorry that the line below is almost unreadable. 
            unique_options.loc[unique_options[unique_options['rank'] == 2].index[unique_options[unique_options['rank'] == 2].index != option_index],'rank'] = 3
            for option_index in unique_options[unique_options['rank'] == 3].index:
                # let option_index have  temp_rank 1 
                temp_group.loc[temp_group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 3
                temp_group.loc[temp_group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 3
        #        and make the rank for all other options that iser to be 1, in to 2
                #I'm sorry that the line below is almost unreadable. 
                unique_options.loc[unique_options[unique_options['rank'] == 3].index[unique_options[unique_options['rank'] == 3].index != option_index],'rank'] = 4
                for option_index in unique_options[unique_options['rank'] == 4].index:
                    # let option_index have  temp_rank 1 
                    temp_group.loc[temp_group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 4
                    temp_group.loc[temp_group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 4
            #        and make the rank for all other options that iser to be 1, in to 2
                    #I'm sorry that the line below is almost unreadable. 
                    unique_options.loc[unique_options[unique_options['rank'] == 4].index[unique_options[unique_options['rank'] == 4].index != option_index],'rank'] = 5
                    for option_index in unique_options[unique_options['rank'] == 5].index:
                        # let option_index have  temp_rank 1 
                        temp_group.loc[temp_group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 5
                        temp_group.loc[temp_group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 5
                #        and make the rank for all other options that iser to be 1, in to 2
                        #I'm sorry that the line below is almost unreadable. 
                        unique_options.loc[unique_options[unique_options['rank'] == 5].index[unique_options[unique_options['rank'] == 5].index != option_index],'rank'] = 6
                        for option_index in unique_options[unique_options['rank'] == 6].index:
                            # let option_index have  temp_rank 1 
                            temp_group.loc[temp_group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 6
                            temp_group.loc[temp_group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 6
                    #        and make the rank for all other options that iser to be 1, in to 2
                            #I'm sorry that the line below is almost unreadable. 
                            unique_options.loc[unique_options[unique_options['rank'] == 6].index[unique_options[unique_options['rank'] == 6].index != option_index],'rank'] = 7
                            # Add the 7's in to the temp_group
                            temp_group.loc[temp_group['option1'] == np.int(unique_options.loc[unique_options['rank'] == 7,'option_code']), 'opt1_temp_rank'] = 7
                            temp_group.loc[temp_group['option2'] == np.int(unique_options.loc[unique_options['rank'] == 7,'option_code']), 'opt2_temp_rank'] = 7
#                            make sure that option1 is always higher ranked that option2, that will make pooling all instances of the same choice eisier. 
                            temp_group['temp_rank_high'] = temp_group[['opt1_temp_rank', 'opt2_temp_rank']].min(axis = 1)
                            temp_group['temp_rank_low'] = temp_group[['opt1_temp_rank', 'opt2_temp_rank']].max(axis = 1)
#                           concat a copy of the temp_group DF to the DF that you're going to aggrigate
                            multiple_rakning_DF = multiple_rakning_DF.append(temp_group.copy(), ignore_index=True)
                            # rest the rank column in the option_index df
                                # If you temp rank is worse then your original rank, and your temp rank is 7, make it 6 again. The others have the same format
                            unique_options.loc[(unique_options['rank'] > unique_options['original_rank']) & (unique_options['rank'] == 7), 'rank'] = 6
                        unique_options.loc[(unique_options['rank'] > unique_options['original_rank']) & (unique_options['rank'] == 6), 'rank'] = 5
                    unique_options.loc[(unique_options['rank'] > unique_options['original_rank']) & (unique_options['rank'] == 5), 'rank'] = 4
                unique_options.loc[(unique_options['rank'] > unique_options['original_rank']) & (unique_options['rank'] == 4), 'rank'] = 3
            unique_options.loc[(unique_options['rank'] > unique_options['original_rank']) & (unique_options['rank'] == 3), 'rank'] = 2
        unique_options.loc[(unique_options['rank'] > unique_options['original_rank']) & (unique_options['rank'] == 2), 'rank'] = 1
                            
                            
#    reduce the DF so that there is one value for each comparieson.
    group_without_indifferences = multiple_rakning_DF.groupby(['sid', 'treatment', 'grade', 'gender', 'temp_rank_high', 'temp_rank_low']).agg(np.mean)
    group_without_indifferences = group_without_indifferences.loc[:,['ice', 'icr', 'tv_trial']].copy()
    group_without_indifferences.reset_index(inplace = True)
    group_without_indifferences.rename(columns={'temp_rank_high': 'rank_high', 'temp_rank_low': 'rank_low'}, inplace=True)
    
#    return with format ['sid', 'treatment', 'grade', 'gender', 'high_rank_option', 'low_rank_option', 'ice']
    return group_without_indifferences
                            
if __name__ == "__main__":
    dataDir = '/Users/Dalton/Documents/Projects/LILA1/dataFrames/'
    trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices5.csv', index_col=False)
    trial_by_trial_without_indifferences = trial_by_trial.groupby(['sid', 'treatment']).apply(remove_rank_indifferences, ranker = '_exp_rank')
    trial_by_trial_without_indifferences.reset_index(drop=True)