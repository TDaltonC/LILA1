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
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices_all.csv', index_col=False)
#tvs = pd.DataFrame.from_csv(dataDir + 'tvs5.csv', index_col=False)
heuristics_wide = pd.DataFrame.from_csv(dataDir + 'heuristics.csv', index_col='sid')
discrep = pd.DataFrame.from_csv(dataDir + 'discrep.csv', index_col=False)
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'0&1', 1:'0&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
social_heuristic_dict = {'a': 'max_self', 'b':'max_other', 'c':'max_social', 'd': 'max_self_max_other', 'e':'max_self_min_other', 'f':'max_social_max_self', 'g':'max_social_max_other'}  
risk_heuristic_dict = {'a': 'max_prob', 'b': 'max_amount', 'c': 'max_ev', 'd': 'max_prob_max_amount', 'e': 'max_amount_max_prob', 'f': 'max_ev_max_amount', 'g': 'max_ev_max_prob'}

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

heuristics_wide = pd.merge(heuristics_wide, discrep, on = 'sid', how = 'left')

#%% Create a column for the min distance to any social heurisitic

heuristics_wide['all_social'] = heuristics_wide[[
    'max_other',
    'max_self',
    'max_self_max_other',
    'max_self_min_other',
    'max_social',
    'max_social_max_other',
    'max_social_max_self'
    ]].max(axis = 1)
#%% Create a column for the min distance to any Risk heurisitc 
heuristics_wide['all_risk'] = heuristics_wide[[
    'max_amount',
    'max_prob',
    'max_amount_max_prob',
    'max_prob_max_amount'
    ]].max(axis = 1)
    

#%% Make violation summaries
treatment_summary = trial_by_trial.groupby(['sid', 'treatment', 'grade', 'age_group']).sum()
treatment_summary.reset_index(inplace = True)
#treatment_summary = pd.merge(treatment_summary, tvs, on = ['treatment', 'sid'])

treatment_summary = pd.merge(treatment_summary, heuristics_wide, on = ['sid', 'age_group', 'grade'], how = 'left')

#%% Plot a cummulative distribution of each
def cumm_plot(dataframe, score_col, heuristic):
    dataframe.sort(score_col, inplace = True)
    dataframe['order'] = dataframe.sort(score_col).groupby(['heuristic'])[score_col].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(score_col, 'order', dataframe[dataframe['heuristic'] == heuristic], fit_reg = False)

cumm_plot(heuristics, 'heuro_score', 'max_amount')

#%% PLOT THE DISTRIBUTION of HEURISTIC SCORES BY GRADE
def cumm_plot(dataframe, score_col, heuristic):
    dataframe.sort(score_col, inplace = True)
    dataframe['order'] = dataframe.sort(score_col).groupby(['heuristic', 'age_group'])[score_col].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(score_col, 'order', dataframe[dataframe['heuristic'] == heuristic], hue = 'age_group', fit_reg = False)

def cumm_plot_wide(dataframe, heuristic):
    dataframe.sort(heuristic, inplace = True)
    dataframe['order'] = dataframe.sort(heuristic).groupby(['age_group'])[heuristic].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(heuristic, 'order', dataframe, hue = 'age_group', fit_reg = False)


cumm_plot(heuristics, 'heuro_score', 'max_amount')
heuristics_wide['risk_flip']= 21 - heuristics_wide['max_amount']
heuristics_wide['social_flip']= 21 - heuristics_wide['all_social']
cumm_plot_wide(heuristics_wide, 'social_flip')



#%% Look for corolations between heuristic scores. 

#sb.pairplot(heuristics_wide, hue = 'age_group')

#%% individual corrolations

sb.lmplot('all_risk', 'max_ev', heuristics_wide, hue = 'age_group', x_jitter = .5, y_jitter = .5, fit_reg = False)
plt.figure()


#%% 

#%%
data  = heuristics_wide.loc[(heuristics_wide['all_risk'] == heuristics_wide['all_risk']) & (heuristics_wide['age_group'] == '2&3'), 'all_risk']
data2 = heuristics_wide.loc[(heuristics_wide['max_ev'] == heuristics_wide['max_ev']) & (heuristics_wide['age_group'] == '2&3'), 'max_ev']
sb.kdeplot(data = data, data2 = data2, cmap = 'Oranges')

data  = heuristics_wide.loc[(heuristics_wide['all_risk'] == heuristics_wide['all_risk']) & (heuristics_wide['age_group'] == '4&5'), 'all_risk']
data2 = heuristics_wide.loc[(heuristics_wide['max_ev'] == heuristics_wide['max_ev']) & (heuristics_wide['age_group'] == '4&5'), 'max_ev']
sb.kdeplot(data = data, data2 = data2, cmap = 'Greens')

data  = heuristics_wide.loc[(heuristics_wide['all_risk'] == heuristics_wide['all_risk']) & (heuristics_wide['age_group'] == '0&1'), 'all_risk']
data2 = heuristics_wide.loc[(heuristics_wide['max_ev'] == heuristics_wide['max_ev']) & (heuristics_wide['age_group'] == '0&1'), 'max_ev']
sb.kdeplot(data = data, data2 = data2, cmap = 'Reds')

data  = heuristics_wide.loc[(heuristics_wide['all_risk'] == heuristics_wide['all_risk']) & (heuristics_wide['age_group'] == 'U'), 'all_risk']
data2 = heuristics_wide.loc[(heuristics_wide['max_ev'] == heuristics_wide['max_ev']) & (heuristics_wide['age_group'] == 'U'), 'max_ev']
a = sb.kdeplot(data = data, data2 = data2, cmap = 'Blues')
a.get_figure().savefig('../Figures/kde.svg', format =  'svg')

#%%
# Corrolate heuristic scores and tv or ice

sb.lmplot('all_social', 'tv_full', treatment_summary[treatment_summary['treatment']=='Social'], hue = 'age_group')
sb.lmplot('max_amount', 'tv_full', treatment_summary[treatment_summary['treatment']=='Risk'], hue = 'age_group')
#$%%



#%% Remove heuristics users from main effect

a = sb.factorplot(
    x='age_group',
    y = 'tv_half',
    hue = 'treatment',
    data = treatment_summary[
        ((treatment_summary['all_social']<21) |
        (treatment_summary['treatment']=='Goods')) &
        (treatment_summary['treatment']!='Risk')],
    kind="point",
    x_order = ['0&1', '2&3', '4&5', 'U'])
#a.savefig('../Figures/19.svg', format =  'svg')

#%%
b = sb.factorplot(
    x='age_group',
    y = 'tv_half',
    hue = 'treatment',
    data = treatment_summary[
        (((treatment_summary['all_risk']<20) &
        (treatment_summary['discrep2']<5)) |
        ((treatment_summary['treatment']=='Goods') &
        (treatment_summary['discrep1']<5))) &
        (treatment_summary['treatment']!='Social')],
    kind="point",
    x_order = ['0&1', '2&3', '4&5', 'U'])
b.savefig('../Figures/risk20.svg', format =  'svg')
#%% t-tests
stats = sp.stats.ttest_ind(
    treatment_summary.loc[
        (treatment_summary['all_social']<20) &
        (treatment_summary['treatment']=='Social') &
        (treatment_summary['age_group']=='2&3'),
        'tv_half'],
    treatment_summary.loc[
        (treatment_summary['treatment']=='Goods') &
        (treatment_summary['age_group']=='2&3'),
        'tv_half'])

#%% t-tests
treatment = 'Social'
stat = 'all_social'
measure = 'tv_half'
cutoff = 21
groups = ['0&1', '2&3', '4&5', 'U']
trimmed = treatment_summary.loc[
    (treatment_summary[stat]<cutoff) &
    (treatment_summary['treatment'] == treatment)]

goods = treatment_summary[treatment_summary['treatment'] == "Goods"]

# t-tests Between
stats_between = dict()
for i, group in enumerate(groups):
    stats = sp.stats.ttest_ind(
        trimmed.loc[trimmed['age_group'] == group, measure],
        goods.loc[goods['age_group'] == group, measure],                
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


#%% Export data for stata tests

data_for_test = treatment_summary.loc[(treatment_summary['all_social']<22) & (treatment_summary['treatment'] == "Risk"), ['sid', 'age_group', 'tv_half']]
