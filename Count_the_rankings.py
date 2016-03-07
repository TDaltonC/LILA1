# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 15:27:16 2016

@author: Dalton
"""

import pandas as pd
import numpy as np
import scipy as sp
import seaborn as sb
import random
import matplotlib.pyplot as plt
import matplotlib.colors as colors
#%%
# Import the choices
dataDir = '/Users/Dalton/Documents/Projects/LILA1/dataFrames/'
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices5.csv', index_col=False)
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'K&1', 1:'K&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
# Set whether you want to see implicit('_exp_rank') or explicit ranking('_exp_rank').
rank = '_imp_rank'
#%% Oraganize things by ranking

def get_complete_ranking(group, ranker = '_exp_rank'):
#    create a duplicate of the group to be extra double sure that nothing form group carries over bwtween loops. 
    temp_group = group.copy()
    #    Get a DF of the options and thier ranks
    option1s = temp_group.loc[:,['opt1'+ranker, 'option1']].copy()
    option1s.rename(columns={'opt1'+ranker: 'rank', 'option1': 'option_code'}, inplace=True)
    option2s = temp_group.loc[:,['opt2'+ranker, 'option2']].copy()
    option2s.rename(columns={'opt2'+ranker: 'rank', 'option2': 'option_code'}, inplace=True)
    options = pd.concat([option1s, option2s])
    unique_options = options.drop_duplicates(['option_code'])
    # Put them in order by option code
    unique_options.sort(['option_code'], inplace = True)
    # Return a sting of the list of options (now in order by option-code)
    return str(unique_options['rank'].tolist())

# get the implied ranking for each subject
imp_rankings_series = trial_by_trial.groupby(['sid', 'treatment', 'grade']).apply(get_complete_ranking, ranker = '_imp_rank')
imp_rankings = imp_rankings_series.reset_index()
imp_rankings.rename(columns={0: 'imp_ranking'}, inplace=True)
# get the explicit ranking for each subject
exp_rankings_series = trial_by_trial.groupby(['sid', 'treatment', 'grade']).apply(get_complete_ranking, ranker = '_exp_rank')
exp_rankings = exp_rankings_series.reset_index()
exp_rankings.rename(columns={0: 'exp_ranking'}, inplace=True)
# Combine the rankings in to one DF
rankings = pd.merge(exp_rankings, imp_rankings, on = ['sid', 'treatment', 'grade'])

#%% Make the count for whichever rank you'd like to plot

# Set whether you want to see implicit('imp_ranking') or explicit ranking('exp_ranking').
rank = 'imp_ranking'

count = rankings.groupby([rank, 'grade', 'treatment']).count()
count.reset_index(inplace = True)
# Normalize across grade
count_corrected_series = count.groupby(['grade', 'treatment']).apply((lambda row: row.sid/np.sum(row.sid)))
count_corrected = count_corrected_series.reset_index(level = [0,1])
count['corrected'] = count_corrected['sid']
count.rename(columns={'sid': 'raw_count'}, inplace=True)
# Add an enumerator
def create_order_number(group):
    group.sort('corrected', ascending = False, inplace = True)
    group['order'] = np.arange(1, len(group['corrected'])+1)
    return group
order_number = count.groupby(['grade', 'treatment']).apply(create_order_number)
order_number.reset_index(drop = True)


#%% 
'''
==================
=====Plotting=====
==================
'''
#%% Plot by grade

sb.factorplot(x='order', y = 'corrected', hue = 'grade', data = order_number[order_number['treatment'] == 1], aspect = 8)
sb.factorplot(x='order', y = 'corrected', hue = 'grade', data = order_number[order_number['treatment'] == 2], aspect = 8)
sb.factorplot(x='order', y = 'corrected', hue = 'grade', data = order_number[order_number['treatment'] == 3], aspect = 8)

#%% Plot by age group

order_number['age_group'] = [age_groups[x] for x in order_number.grade]
order_number_by_age_group = order_number.groupby(['age_group', rank, 'treatment']).sum()
# reset index
order_number_by_age_group.reset_index(inplace = True)
# drop Grade, Corrected, and Order
order_number_by_age_group.drop(['grade', 'corrected', 'order'], axis = 1, inplace = True)
# Redo Correction (for group size) and Order
order_number_by_age_group['corrected'] = order_number_by_age_group.groupby(['age_group','treatment'])['raw_count'].transform(lambda raw_count: raw_count/np.sum(raw_count))
order_number_by_age_group['order'] = order_number_by_age_group.sort('raw_count', ascending = False).groupby(['age_group','treatment'])['raw_count'].transform(lambda raw: np.arange(1, len(raw)+1))
order_number.reset_index(drop = True)

sb.factorplot(x='order', y = 'corrected', hue = 'age_group', data = order_number_by_age_group[order_number_by_age_group['treatment'] == 1], aspect = 8)
sb.factorplot(x='order', y = 'corrected', hue = 'age_group', data = order_number_by_age_group[order_number_by_age_group['treatment'] == 2], aspect = 8)
sb.factorplot(x='order', y = 'corrected', hue = 'age_group', data = order_number_by_age_group[order_number_by_age_group['treatment'] == 3], aspect = 8)

#%% What are the exp rankings of people with imp_rankings == [1, 2, 3, 4, 5, 6, 7]

birds_of_a_feather = rankings[rankings['imp_ranking'] == '[1, 2, 3, 4, 5, 6, 7]']
grade_count = birds_of_a_feather.groupby(['grade', 'treatment']).count()
grade_count.reset_index(inplace = True)
cross_count = birds_of_a_feather.groupby(['exp_ranking', 'grade', 'treatment']).count()
cross_count.reset_index(inplace = True)