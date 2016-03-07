# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 19:44:26 2016

@author: Dalton
"""

def remove_rank_indifferences(group):
#    make an empty DF to concatonate the many ranking on 
    multiple_rakning_DF = pd.DataFrame()
#    Get a DF of the options and thier ranks
    # What Rank should I use? _exp_rank or _imp_rank
    ranker = '_exp_rank'
    option1s = group.loc[:,['opt1'+ranker, 'option1']].copy()
    option1s.rename(columns={'opt1'+ranker: 'rank', 'option1': 'option_code'}, inplace=True)
    option2s = group.loc[:,['opt2'+ranker, 'option2']].copy()
    option2s.rename(columns={'opt2'+ranker: 'rank', 'option2': 'option_code'}, inplace=True)
    options = pd.concat([option1s, option2s])
    unique_options = options.drop_duplicates(['option_code'])
#    make a backup copy of the original ranking. 
    unique_options['original_rank'] = unique_options['rank']
    for option_index in unique_options[unique_options['rank'] == 1].index:
        # let option_index have  temp_rank 1 
        group.loc[group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 1
        group.loc[group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 1
#        and make the rank for all other options that iser to be 1, in to 2
        #I'm sorry that the line below is almost unreadable. 
        unique_options.loc[unique_options[unique_options['rank'] == 1].index[unique_options[unique_options['rank'] == 1].index != option_index],'rank'] = 2
        for option_index in unique_options[unique_options['rank'] == 2].index:
            # let option_index have  temp_rank 1 
            group.loc[group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 2
            group.loc[group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 2
    #        and make the rank for all other options that iser to be 1, in to 2
            #I'm sorry that the line below is almost unreadable. 
            unique_options.loc[unique_options[unique_options['rank'] == 2].index[unique_options[unique_options['rank'] == 2].index != option_index],'rank'] = 3
            for option_index in unique_options[unique_options['rank'] == 3].index:
                # let option_index have  temp_rank 1 
                group.loc[group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 3
                group.loc[group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 3
        #        and make the rank for all other options that iser to be 1, in to 2
                #I'm sorry that the line below is almost unreadable. 
                unique_options.loc[unique_options[unique_options['rank'] == 3].index[unique_options[unique_options['rank'] == 3].index != option_index],'rank'] = 4
                for option_index in unique_options[unique_options['rank'] == 4].index:
                    # let option_index have  temp_rank 1 
                    group.loc[group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 4
                    group.loc[group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 4
            #        and make the rank for all other options that iser to be 1, in to 2
                    #I'm sorry that the line below is almost unreadable. 
                    unique_options.loc[unique_options[unique_options['rank'] == 4].index[unique_options[unique_options['rank'] == 4].index != option_index],'rank'] = 5
                    for option_index in unique_options[unique_options['rank'] == 5].index:
                        # let option_index have  temp_rank 1 
                        group.loc[group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 5
                        group.loc[group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 5
                #        and make the rank for all other options that iser to be 1, in to 2
                        #I'm sorry that the line below is almost unreadable. 
                        unique_options.loc[unique_options[unique_options['rank'] == 5].index[unique_options[unique_options['rank'] == 5].index != option_index],'rank'] = 6
                        for option_index in unique_options[unique_options['rank'] == 6].index:
                            # let option_index have  temp_rank 1 
                            group.loc[group['option1'] == unique_options.loc[option_index,'option_code'], 'opt1_temp_rank'] = 6
                            group.loc[group['option2'] == unique_options.loc[option_index,'option_code'], 'opt2_temp_rank'] = 6
                    #        and make the rank for all other options that iser to be 1, in to 2
                            #I'm sorry that the line below is almost unreadable. 
                            unique_options.loc[unique_options[unique_options['rank'] == 6].index[unique_options[unique_options['rank'] == 6].index != option_index],'rank'] = 7
                            # Add the 7's in to the group
                            group.loc[group['option1'] == unique_options.loc[unique_options['rank'] == 7,'option_code'], 'opt1_temp_rank'] = 7
                            group.loc[group['option2'] == unique_options.loc[unique_options['rank'] == 7,'option_code'], 'opt2_temp_rank'] = 7
#                           concat a copy of the group DF to the DF that you're going to aggrigate
                            multiple_rakning_DF.append(group.copy())
#                           rest the rank column in the option_index df
                            unique_options['rank'] = unique_options['original_rank']
                            
#    reduce the DF so that there is one value for each comparieson.
    return group
                            
trial_by_trial.groupby(['sid', 'treatment']).apply(remove_rank_indifferences)