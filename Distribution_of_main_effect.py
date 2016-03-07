# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 10:41:41 2016

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
tvs = pd.DataFrame.from_csv(dataDir + 'tvs5.csv', index_col=False)
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'0&1', 1:'0&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
trial_by_trial['treatment'] = [treatments[x] for x in trial_by_trial['treatment']]
trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial['grade']]
#%% Plot ICE/TV by grade and treatment

treatment_summary = trial_by_trial.groupby(['sid', 'treatment', 'grade', 'age_group']).sum()
treatment_summary.reset_index(inplace = True)
treatment_summary = pd.merge(treatment_summary, tvs, on = ['treatment', 'sid'])
sb.factorplot(x='age_group', y = 'tv', hue = 'treatment', data = treatment_summary, kind="point")

sp.stats.ttest_ind(
    treatment_summary.loc[(treatment_summary['treatment'] == 'Social') & (treatment_summary['age_group'] == 'U'), 'tv'],
    treatment_summary.loc[(treatment_summary['treatment'] == 'Social') & (treatment_summary['age_group'] == '4&5'), 'tv'],
    False)

#%% 

def cumm_plot(dataframe, x):
    dataframe['order'] = dataframe.sort(x).groupby(['treatment', 'age_group'])[x].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(x, 'order', dataframe, col = 'age_group', row = 'treatment', fit_reg = False)

cumm_plot(treatment_summary, 'ice')
#sb.kdeplot(treatment_summary.loc[treatment_summary['treatment'] == 1, 'tv'])