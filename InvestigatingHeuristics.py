# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 13:21:15 2016

@author: Dalton
"""

import pandas as pd
import numpy as np
import scipy as sp
import seaborn as sb
import random
import matplotlib.pyplot as plt
import matplotlib.colors as colors

#%% Load data

dataDir = '/Users/Dalton/Documents/Projects/LILA1/dataFrames/'
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices5.csv', index_col=False)
tvs = pd.DataFrame.from_csv(dataDir + 'tvs5.csv', index_col=False)
heuristics_wide = pd.DataFrame.from_csv(dataDir + 'heuristics.csv', index_col='sid')
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'K&1', 1:'K&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
social_heuristic_dict = {'a': 'max_self', 'b':'max_other', 'c':'max_social', 'd': 'max_self_max_other', 'e':'max_self_min_other', 'f':'max_social_max_self', 'g':'max_social_max_other'}  
risk_heuristic_dict = {'a': 'max_prob', 'b': 'max_payoff', 'c': 'max_ev', 'd': 'max_prob_max_amount', 'e': 'max_payoff_max_prob', 'f': 'max_ev_max_payoff', 'g': 'max_ev_max_prob'}

trial_by_trial['treatment'] = [treatments[x] for x in trial_by_trial['treatment']]
trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial['grade']]
subjects = trial_by_trial[['sid', 'gender', 'grade', 'age_group']].copy()
subjects.drop_duplicates(inplace = True)
#%% get heuristics in shape(long) and get heuristics wide cleaned up.
heuristics_wide.drop(['disttonearestheuro2', 'disttonearestheuro3', 'nearheuro2','nearheuro3', 'heuro2', 'heuro3'], inplace = True, axis = 1)
heuristics_long = heuristics_wide.stack()
heuristics = heuristics_long.reset_index()
heuristics['treatment'] = heuristics['level_1'].apply(lambda level_1: int(level_1[5]))
heuristics['heuro_code'] = heuristics['level_1'].apply(lambda level_1: level_1[6])
heuristics.loc[heuristics['treatment'] == 2, 'heuristic'] = [risk_heuristic_dict[x] for x in heuristics['heuro_code']]
heuristics.loc[heuristics['treatment'] == 3, 'heuristic'] = [social_heuristic_dict[x] for x in heuristics['heuro_code']]
heuristics.drop(['level_1', 'heuro_code'], axis = 1, inplace = True)
heuristics.rename(columns={0: 'heuro_score'}, inplace=True)
heuristics = pd.merge(heuristics, subjects, on = 'sid', how = 'left')

heuristics_wide = heuristics.pivot(index = 'sid', columns = 'heuristic', values = 'heuro_score')
heuristics_wide.reset_index(inplace = True)
heuristics_wide = pd.merge(heuristics_wide, subjects, on = 'sid', how = 'left')

#%% Make violation summaries
treatment_summary = trial_by_trial.groupby(['sid', 'treatment', 'grade', 'age_group']).sum()
treatment_summary.reset_index(inplace = True)
treatment_summary = pd.merge(treatment_summary, tvs, on = ['treatment', 'sid'])

treatment_summary = pd.merge(treatment_summary, heuristics_wide, on = ['sid', 'age_group', 'grade', 'gender'])

#%% Plot a cummulative distribution of each
def cumm_plot(dataframe, score_col, heuristic):
    dataframe.sort(score_col, inplace = True)
    dataframe['order'] = dataframe.sort(score_col).groupby(['heuristic'])[score_col].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(score_col, 'order', dataframe[dataframe['heuristic'] == heuristic], fit_reg = False)

cumm_plot(heuristics, 'heuro_score', 'max_payoff')

#%% PLOT THE DISTRIBUTION of HEURISTIC SCORES BY GRADE
def cumm_plot(dataframe, score_col, heuristic):
    dataframe.sort(score_col, inplace = True)
    dataframe['order'] = dataframe.sort(score_col).groupby(['heuristic', 'age_group'])[score_col].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(score_col, 'order', dataframe[dataframe['heuristic'] == heuristic], hue = 'age_group', fit_reg = False)

cumm_plot(heuristics, 'heuro_score', 'max_payoff')

#%% Look for corolations between heuristic scores. 

sb.pairplot(heuristics_wide, hue = 'age_group')

#%% individual corrolations

sb.lmplot('max_payoff', 'max_self', heuristics_wide, hue = 'age_group', x_jitter = .5, y_jitter = .5)

#%%
# Corrolate heuristic scores and tv or ice

sb.lmplot('max_self', 'tv', treatment_summary[treatment_summary['treatment']=='Social'], hue = 'age_group')
sb.lmplot('max_payoff', 'tv', treatment_summary[treatment_summary['treatment']=='Risk'], hue = 'age_group')


#%% Remove heuristics users from main effect

sb.factorplot(
    x='age_group',
    y = 'tv',
    hue = 'treatment',
    data = treatment_summary[
        ((treatment_summary['max_self']<22) |
        (treatment_summary['treatment']=='Goods')) &
        (treatment_summary['treatment']!='Risk')],
    kind="point",
    x_order = ['K&1', '2&3', '4&5', 'U'])


sb.factorplot(
    x='age_group',
    y = 'tv',
    hue = 'treatment',
    data = treatment_summary[
        ((treatment_summary['max_payoff']<15) |
        (treatment_summary['treatment']=='Goods')) &
        (treatment_summary['treatment']!='Social')],
    kind="point",
    x_order = ['K&1', '2&3', '4&5', 'U'])

