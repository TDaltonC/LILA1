# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 16:29:37 2016

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
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices_all.csv', index_col=False)
norms = pd.DataFrame.from_csv(dataDir + 'moral_norms.csv', index_col=False)
## Recode Choice LR so that 1 is higher rank, -1 is lower rank and 0 is indiff if you're visualizing preferences and chocies
trial_by_trial.loc[trial_by_trial['choice_LR'] == 2, 'choice_LR'] = -1
# magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'K&1', 1:'K&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial.grade]

#%% Colors

green_map = {
         'red':   ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 1.0, 1.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0))}
red_map = {
         'red':   ((0.0, 0.0, 0.0),
                   (1.0, 1.0, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0))}
# Green<-->Black<-->Red
gbr_map = {
         'red':   ((0.0, 1.0, 1.0),
                   (0.5, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 0.0),
                   (1.0, 1.0, 1.0)),

         'blue':  ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0))}
greener = colors.LinearSegmentedColormap('Green_map', green_map)
reder = colors.LinearSegmentedColormap('Red_map', red_map)
gbr = colors.LinearSegmentedColormap('bbr_map', gbr_map)

#%% Functions

def heatmap_fromDF(data, **kwargs):
    heatdata = pd.pivot_table(
        data,
        index='item2',
        columns='item1', 
        aggfunc=np.median)
    mask = heatdata != heatdata
    sb.heatmap(
        heatdata, 
        mask = mask, 
        cmap = gbr, 
#        cbar = False,
#        vmin = 0, 
#        vmax = 0.5, 
        **kwargs)

#%% Add implied choices
# an implied choice is the choice you would have made if you followed your ranking
def implied_choice(row):
    if row.opt1_exp_rank > row.opt2_exp_rank:
        if row.option1<row.option2:
            return -1
        if row.option1>row.option2:
            return 1
    if row.opt1_exp_rank < row.opt2_exp_rank:
        if row.option1<row.option2:
            return 1
        if row.option1>row.option2:
            return -1
    if row.opt1_exp_rank == row.opt2_exp_rank:
        return 0

trial_by_trial['implied_choice'] = trial_by_trial.apply(implied_choice, axis = 1)

#%% Make heatmaps for **SOCIAL** but use option in stead of rank. 

## Plot the subtask for each age-group
trial_by_trial_social = trial_by_trial[trial_by_trial.treatment == 3]
grade_treatment_grouped = trial_by_trial_social.groupby(["age_group"])
for name, group in grade_treatment_grouped:
    
    plt.figure()
    treatment = [treatments[x] for x in group.treatment]
    group['opt_min'] = group[['option2', 'option1']].min(axis = 1)
    group['opt_max'] = group[['option2', 'option1']].max(axis = 1)
    heatdata = pd.pivot_table(group,
                          values='implied_choice',
                          index='opt_max',
                          columns='opt_min',  
                          aggfunc=np.mean)
    mask = heatdata != heatdata
    ax = plt.axes()
    plot = sb.heatmap(
        heatdata, 
        mask = mask,
        cbar = False,
        center = 0,
        vmin =  1, 
        vmax =  1,
        cmap = gbr)
    
    ax.set_title(name)
    plt.show()
    
#%% Make heatmaps for **RISK** but use option in stead of rank. 

## Plot the subtask for each age-group
trial_by_trial_social = trial_by_trial[trial_by_trial.treatment == 2]
grade_treatment_grouped = trial_by_trial_social.groupby(["age_group"])
for name, group in grade_treatment_grouped:
    
    plt.figure()
    treatment = [treatments[x] for x in group.treatment]
    group['opt_min'] = group[['option2', 'option1']].min(axis = 1)
    group['opt_max'] = group[['option2', 'option1']].max(axis = 1)
    heatdata = pd.pivot_table(group,
                          values='choice_LR',
                          index='opt_max',
                          columns='opt_min',  
                          aggfunc=np.mean)
    mask = heatdata != heatdata
    ax = plt.axes()
    plot = sb.heatmap(
        heatdata, 
        mask = mask,
#        cbar = False,
        center = 0,
#        vmin =  0, 
#        vmax =  0.22,
        cmap = gbr)
    
    ax.set_title(name)
    plt.show()


#%% Plot the ethical norms
norms[norms == 0] = np.nan
norms['conflict'] = abs(norms['equality'] - norms['socialmax'])

heatdata = pd.pivot_table(norms,
                      values='conflict',
                      index='option2',
                      columns='option1',  
                      aggfunc=np.mean)
mask = heatdata != heatdata
ax = plt.axes()
plot = sb.heatmap(
    heatdata,
    mask = mask,
#    cbar = False,
#    center = 0,
#    vmin =  -1, 
#    vmax =  1,
    cmap = 'gist_heat')