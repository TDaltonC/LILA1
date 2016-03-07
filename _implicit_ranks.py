# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 17:53:15 2016

This script was used to calculate the implicit rankings for all of the options,
and scores each comparison for whether or not they agree with the implicit rank
Those rankings were saved in csv, so there shouldn't be a need to run it again. 

@author: Dalton
"""

import pandas as pd
import numpy as np
import scipy as sp
import seaborn as sb
import matplotlib.pyplot as plt
import matplotlib.colors as colors
#%%
# Import the choices
dataDir = '/Users/Dalton/Documents/Projects/LILA1/dataFrames/'
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices5.csv', index_col=False)

#%% Make the option datafarme
# optionDF format ['SID', 'item', 'task', 'exp_rank', 'imp_rank', 'gender', 'grade']

def get_vote(row):
    if row.choice_LR == 1:
        return min(row.option1, row.option2)
    elif row.choice_LR == 2:
        return max(row.option1, row.option2)

def find_implicit_rank(group):
#    Count the "votes" that each option gets. if indifferent, each option gets 1/2 vote. 
#       Duplicate the DF, in one version turn 0s to 1's and in the other version turn 0's to 2's
    group_one = group.copy()
    group_one['choice_LR'][group_one['choice_LR']==0] = 1
    group_two = group.copy()
    group_two['choice_LR'][group_two['choice_LR']==0] = 2    
    double_count = pd.concat([group_one, group_two])
    double_count['option'] = double_count.apply(get_vote, axis = 1)
# add this df to the end so that each option gets at least one vote and ends up in the count
    ballot_stuffer = pd.DataFrame(data = {'option':[1,2,3,4,5,6,7]})
    double_count = pd.concat([double_count, ballot_stuffer])
#       Now just count the votes for 1 or 2. A chouce will get 2 votes and an indiff will get 1. 
    vote_tally = double_count.groupby('option').count()
#    Get it down to just one well named column. I'm over writing sid, but it could be any of them
    vote_tally = vote_tally.rename(columns={'sid': 'vote_count'})
    vote_tally = vote_tally.loc[:, ['vote_count']]
#    sort them by vote count 
    vote_tally.sort('vote_count', ascending = False, inplace = True)
    # add in the rank
    vote_tally['rank'] = np.arange(1, (vote_tally.size+1))
    vote_tally.drop_duplicates(['vote_count'])
    vote_tally_without_duplicates = vote_tally.drop_duplicates(['vote_count'])
    vote_rank = pd.merge(vote_tally, vote_tally_without_duplicates, on = ['vote_count'], how = 'left', left_index = True)
    vote_rank.set_index(vote_tally.index, inplace = True)
    vote_rank.rename(columns={'rank_y': 'imp_rank'}, inplace=True)
#    return a DF with format [index['sid', 'item', 'treatment'], 'vote_count', 'imp_rank']'
    return vote_rank.loc[:,['vote_count', 'imp_rank']].copy()


one_task_group = trial_by_trial.groupby(['sid', 'treatment'])
options = one_task_group.apply(find_implicit_rank)
options.reset_index(inplace = True)

# Merge the new column in and rename everything
options_to_merge = options[['sid', 'treatment', 'option', 'imp_rank']].copy()
options_to_merge.rename(columns={'option': 'option1', 'imp_rank': 'opt1_imp_rank'}, inplace=True)
trial_by_trial = pd.merge(trial_by_trial, options_to_merge, on=['sid', 'treatment', 'option1'])
options_to_merge = options[['sid', 'treatment', 'option', 'imp_rank']].copy()
options_to_merge.rename(columns={'option': 'option2', 'imp_rank': 'opt2_imp_rank'}, inplace=True)
trial_by_trial = pd.merge(trial_by_trial, options_to_merge, on=['sid', 'treatment', 'option2'])
trial_by_trial.rename(columns={'item1': 'opt1_exp_rank', 'item2': 'opt2_exp_rank'}, inplace=True)



#%% Score the choices for violations
#

def choose_opt_1or2(row):
    if row.choice_LR == 1:
        if row.option1 > row.option2:
            return 2
        elif row.option1 < row.option2:
            return 1
    elif row.choice_LR == 2:
        if row.option1 > row.option2:
            return 1
        elif row.option1 < row.option2:
            return 2
    elif row.choice_LR == 0:
        return 0
        
trial_by_trial['chosen_opt'] = trial_by_trial.apply(choose_opt_1or2, axis = 1)

#choices5.csv is coded so that
#    a > b > c < a    : consistent
#    a == b == c == a : consistent
#    a > b > c > a    : 1 point violation
#    a == b > c > a   : 0.5 point violation 
#    a > b == c == a  : 0.5 point violation

def violation_scorer5(row):
#    if option 1 is ranked higher
    if row.opt1_imp_rank < row.opt2_imp_rank:
        if row.chosen_opt == 1:
            return 0
        elif row.chosen_opt == 2:
            return 1
        elif row.chosen_opt == 0:
            return 0.5
#    if option 2 is ranked higher
    elif row.opt1_imp_rank > row.opt2_imp_rank:
        if row.chosen_opt == 1:
            return 1
        elif row.chosen_opt == 2:
            return 0
        elif row.chosen_opt == 0:
            return 0.5
#    if the options have the same rank
    elif row.opt1_imp_rank == row.opt2_imp_rank:
        if row.chosen_opt == 1:
            return 0.5
        elif row.chosen_opt == 2:
            return 0.5
        elif row.chosen_opt == 0:
            return 0

#
#choices1.csv is coded so that
#    a > b > c < a    : consistent
#    a == b == c == a : consistent
#    a > b > c > a    : 1 point violation
#    a == b > c > a   : 1 point violation 
#    a > b == c == a  : 1 point violation

def violation_scorer1(row):
#    if option 1 is ranked higher
    if row.opt1_imp_rank < row.opt2_imp_rank:
        if row.chosen_opt == 1:
            return 0
        elif row.chosen_opt == 2:
            return 1
        elif row.chosen_opt == 0:
            return 1
#    if option 2 is ranked higher
    elif row.opt1_imp_rank > row.opt2_imp_rank:
        if row.chosen_opt == 1:
            return 1
        elif row.chosen_opt == 2:
            return 0
        elif row.chosen_opt == 0:
            return 1
#    if the options have the same rank
    elif row.opt1_imp_rank == row.opt2_imp_rank:
        if row.chosen_opt == 1:
            return 1
        elif row.chosen_opt == 2:
            return 1
        elif row.chosen_opt == 0:
            return 0

trial_by_trial['icr'] = trial_by_trial.apply(violation_scorer5, axis = 1)

#%% Save
trial_by_trial.to_csv(dataDir + 'choices5.csv', index = False)