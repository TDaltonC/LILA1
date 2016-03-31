# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 11:01:16 2016

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
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices_all.csv', index_col=False)
tvs = pd.DataFrame.from_csv(dataDir + 'tvs5.csv', index_col=False)
greedy = pd.DataFrame.from_csv(dataDir + 'greedy_rankings.csv', index_col='option_code')
max_amount = pd.DataFrame.from_csv(dataDir + 'max_amount_rankings.csv', index_col='option_code')
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
trial_by_trial['treatment'] = [treatments[x] for x in trial_by_trial.treatment]
age_groups = {0:'0&1', 1:'0&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
# Set whether you want to see implicit('_imp_rank') or explicit ranking('_exp_rank').
ranker = '_imp_rank'
treatment = 'Risk'
measure = 'tv_half'
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
    return unique_options

def get_distance_to_norm(group, norm):
    # take the difference between the subjects ranking and each greedy ranking
    ranks = group.set_index('option_code')
    norm_diff = norm.apply(lambda rank: rank - ranks['rank'])
    # get the sumtotal distance from each greedy ranking
    norm_dist = norm_diff.abs().sum()
    # retun the min() of those sumtotals
    d = {'distance': norm_dist.min()}
    min_distance_DF = pd.DataFrame(data = d, index = [group.name])
    return min_distance_DF
    

#%% get the explicit ranking for each subject
trial_by_trial_social = trial_by_trial[trial_by_trial['treatment']== treatment]
rankings_series = trial_by_trial_social.groupby(['treatment', 'sid', 'grade']).apply(get_complete_ranking, ranker = ranker)
rankings = rankings_series.reset_index()
rankings.drop(['level_3'], axis = 1, inplace = True)

#%% Get the distance to rule
if treatment == "Social":
    norm = greedy
elif treatment == "Risk":
    norm = max_amount
distance_series = rankings.groupby(['treatment', 'sid', 'grade']).apply(get_distance_to_norm, norm = norm)

distance = distance_series.reset_index()
distance.drop('level_3', axis = 1, inplace = True)

#%% Plot a cummulative distribution of of distance scores
def cumm_plot(dataframe, score_col):
    dataframe.sort(score_col, inplace = True)
    dataframe['order'] = dataframe.sort(score_col).groupby(['treatment'])[score_col].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(score_col, 'order', dataframe, fit_reg = False)

cumm_plot(distance, 'distance')

#%% PLOT THE DISTRIBUTION of DISTANCE SCORES BY GRADE
distance['age_group'] = [age_groups[x] for x in distance.grade]

def cumm_plot(dataframe, score_col):
    dataframe.sort(score_col, inplace = True)
    dataframe['order'] = dataframe.sort(score_col).groupby(['age_group'])[score_col].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(score_col, 'order', dataframe, fit_reg = False, hue = 'age_group')

cumm_plot(distance, 'distance')

#%% Make violation summaries
trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial.grade]
treatment_summary = trial_by_trial.groupby(['sid', 'treatment', 'grade', 'age_group']).sum()
treatment_summary.reset_index(inplace = True)
treatment_summary = pd.merge(treatment_summary, tvs, on = ['treatment', 'sid'])

treatment_summary = pd.merge(treatment_summary, distance, on = ['sid', 'age_group', 'grade', 'treatment'], how = 'left')

#%% Remove heuristics users from main effect

sb.factorplot(
    x='age_group',
    y = 'tv_half',
    hue = 'treatment',
    data = treatment_summary[
        ((treatment_summary['distance']>1) |
        (treatment_summary['treatment']=='Goods'))],
    kind="point",
    x_order = ['0&1', '2&3', '4&5', 'U'])


#%% t-tests
groups = ['0&1', '2&3', '4&5', 'U']
trimmed = treatment_summary[treatment_summary['distance']>2]

goods = treatment_summary[treatment_summary['treatment'] == "Goods"]

stats_between = dict()
for i, group in enumerate(groups):
    stats = sp.stats.ttest_ind(
        trimmed.loc[trimmed['age_group'] == group, 'tv_half'],
        goods.loc[goods['age_group'] == group, 'tv_half'],                
        False)
    stats_between[group] = stats[1]
                
# t-tests within
stats_within = dict()
for i, group1 in enumerate(groups):
    for j, group2 in enumerate(groups):
        if i < j:
            stats = sp.stats.ttest_ind(
                trimmed.loc[(trimmed['treatment'] == treatment) & (trimmed['age_group'] == group1), measure],
                trimmed.loc[(trimmed['treatment'] == treatment) & (trimmed['age_group'] == group2), measure],
                False)
            stats_within[group1+" and "+group2] = stats[1]
