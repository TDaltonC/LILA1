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
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices_all.csv', index_col=False)
#tvs = pd.DataFrame.from_csv(dataDir + 'tvs5.csv', index_col=False)
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'0&1', 1:'0&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
trial_by_trial['treatment'] = [treatments[x] for x in trial_by_trial['treatment']]
trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial['grade']]
measure = 'icr_half'
#%% Plot ICE/TV by grade and treatment

treatment_summary = trial_by_trial.groupby(['sid', 'treatment', 'grade', 'age_group']).sum()
treatment_summary.reset_index(inplace = True)
#treatment_summary = pd.merge(treatment_summary, tvs, on = ['treatment', 'sid'])
#treatment_summary[measure] =treatment_summary[measure]/3
a = sb.factorplot(x='age_group', y = measure, hue = 'treatment', data = treatment_summary, kind="point")
a.savefig('../Figures/mainEffect.svg', format =  'svg')
#%% t-tests
persistent = dict()
groups = ['0&1', '2&3', '4&5', 'U']
for i, group1 in enumerate(groups):
    for j, group2 in enumerate(groups):
        if i < j:
            stats = sp.stats.ttest_ind(
                treatment_summary.loc[(treatment_summary['treatment'] == 'Risk') & (treatment_summary['age_group'] == group1), measure],
                treatment_summary.loc[(treatment_summary['treatment'] == 'Risk') & (treatment_summary['age_group'] == group2), measure],
                False)
            persistent[group1+" and "+group2] = stats[1]

#%% 

#def cumm_plot(dataframe, x):
#    plt.figure()
#    dataframe['order'] = dataframe.sort(x).groupby(['treatment', 'age_group'])[x].transform(lambda score: np.linspace(0, 1, len(score)))
#    g = sb.lmplot(x, 'order', dataframe, col = 'age_group', row = 'treatment', fit_reg = False)
#    plt.subplots_adjust(top=0.97)
#    g.fig.suptitle('measure = ' + x)
#    
#cumm_plot(treatment_summary, measure)
##sb.kdeplot(treatment_summary.loc[treatment_summary['treatment'] == 1, 'tv'])