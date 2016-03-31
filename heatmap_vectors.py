# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 18:12:59 2016

@author: Dalton
"""

import pandas as pd
import numpy as np
import scipy as sp
import seaborn as sb
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import math
from remove_indifference_from_rank import remove_rank_indifferences
#%%
# Import the choices
dataDir = '/Users/Dalton/Documents/Projects/LILA1/dataFrames/'
#trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices_all.csv', index_col=False)
#trial_by_trial_without_indifferences = trial_by_trial.groupby(['sid', 'treatment']).apply(remove_rank_indifferences, ranker = '_exp_rank')
#trial_by_trial_without_indifferences.reset_index(inplace = True, drop = True)
#trial_by_trial = trial_by_trial_without_indifferences
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'K&1', 1:'K&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 6:'4&5', 14:'U'}

#%% Functions

def heatmap_fromDF(data, **kwargs):
    heatdata = pd.pivot_table(
        data,
        values='tv_half',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    mask = heatdata != heatdata
    
    sb.heatmap(
        heatdata, 
        mask = mask, 
        cmap = "inferno", 
#        cbar = False,
#        vmin = 0, 
#        vmax = .9,
        **kwargs)
def vector_data(data, **kwargs):
    i=0
    high_ranks = [1,2,3,4,5]
    low_ranks  = [2,3,4,5,6]
#    vectors = pd.DataFrame()
    vectors = pd.DataFrame(columns = ['high_rank', 'low_rank', 'x', 'y'])
    heatdata = pd.pivot_table(
        data,
        values='tv_half',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    heatdata.fillna(0, inplace=True)
    for high_rank in high_ranks:
        for low_rank in low_ranks:
            if low_rank > high_rank + 1:
                top_left    = heatdata.loc[low_rank, high_rank]
                top_right   = heatdata.loc[low_rank, high_rank+1]
                bottom_left = heatdata.loc[low_rank+1, high_rank]
                bottom_right= heatdata.loc[low_rank+1, high_rank+1]
                
                x = (top_right + bottom_right) - (top_left + bottom_left)
                y = (top_left + top_right) - (bottom_left + bottom_right)
                vectors.loc[i] = [high_rank, low_rank, x, y]
                i = i + 1
    return vectors

def lr_gradient(data, **kwargs):
    i=0
    high_ranks = [1,2,3,4,5,6]
    low_ranks  = [2,3,4,5,6,7]
#    vectors = pd.DataFrame()
    vectors = pd.DataFrame(columns = ['high_rank', 'low_rank', 'left_grad'])
    heatdata = pd.pivot_table(
        data,
        values='tv_half',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    heatdata.fillna(0, inplace=True)
    for high_rank in high_ranks:
        for low_rank in low_ranks:
            if low_rank > high_rank+1:
                left = heatdata.loc[low_rank, high_rank]
                right =heatdata.loc[low_rank, high_rank+1]
                gradient = left-right
                vectors.loc[i] = [high_rank, low_rank, gradient]
                i = i+1
    return vectors
                
def ud_gradient(data, **kwargs):
    i=0
    high_ranks = [1,2,3,4,5,6]
    low_ranks  = [2,3,4,5,6,7]
#    vectors = pd.DataFrame()
    vectors = pd.DataFrame(columns = ['high_rank', 'low_rank', 'left_grad'])
    heatdata = pd.pivot_table(
        data,
        values='tv_half',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    heatdata.fillna(0, inplace=True)
    for high_rank in high_ranks:
        for low_rank in low_ranks:
            if low_rank-1 > high_rank:
                down = heatdata.loc[low_rank, high_rank]
                up =heatdata.loc[low_rank-1, high_rank]
                gradient = up-down
                vectors.loc[i] = [high_rank, low_rank, gradient]
                i=i+1
    return vectors

def find_angle(row):
    x = row.x
    y = row.y
    Q1_angle = np.arctan(abs(y/x))
    if (x >=0) & (y >=0):   # Q1
        angle = Q1_angle
    elif (x >=0) & (y < 0): # Q4
        angle =  - Q1_angle 
    elif (x < 0) & (y >=0): # Q2
        angle = (math.pi) - Q1_angle
    elif (x < 0) & (y < 0): # Q3
        angle = math.pi + Q1_angle
    return angle
    
#%% Print a wide fact plot for each age group (Grouped in the K-1 2-3 4-5 U) for 1 task
treatment = "Risk"
trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial.grade]
trial_by_trial['treatment_name'] = [treatments[x] for x in trial_by_trial.treatment]
heat_map_subjects = trial_by_trial

# Use this line to only use the SID's in the df 'trimmed' from heurisitic or distance scripts
#heat_map_subjects = heat_may_subjects[heat_may_subjects['sid'].isin(trimmed['sid'])]

plt.figure()
g = sb.FacetGrid(heat_map_subjects[heat_map_subjects['treatment_name']==treatment], col="age_group", col_order = ['0&1', '2&3', '4&5', 'U'])
g = g.map_dataframe(heatmap_fromDF)
#plt.subplots_adjust(top=0.9)
#g.fig.suptitle('Group '+ str(name))  
#g.savefig('../Figures/social_heatmap.svg', format =  'svg') 

#%% Angles and amps
treatment = "Social"
heatmap_fromDF(trial_by_trial[trial_by_trial['treatment_name']==treatment])
vectors = vector_data(trial_by_trial[(trial_by_trial['treatment_name']==treatment)&(trial_by_trial['age_group']=='K&1')])
vectors['amp'] = vectors.apply(lambda row: (row.x**(2.) + row.y**(2.))**(0.5), axis = 1)
vectors['angle'] = vectors.apply(find_angle, axis = 1)

sb.lmplot("x", "y", vectors)
stats_lr = sp.stats.ttest_1samp(vectors['angle'],0)
stats_mid= sp.stats.ttest_1samp(vectors['angle'],math.pi/4)
stats_ud = sp.stats.ttest_1samp(vectors['angle'],math.pi/2)

#%% left and right
treatment = "Goods"
heatmap_fromDF(trial_by_trial[trial_by_trial['treatment_name']==treatment])
vectors_lr = lr_gradient(trial_by_trial[(trial_by_trial['treatment_name']==treatment) & (trial_by_trial['age_group'] == 'U')])
vectors_ud = ud_gradient(trial_by_trial[(trial_by_trial['treatment_name']==treatment) & (trial_by_trial['age_group'] == 'U')])

stats_lr = sp.stats.ttest_1samp(vectors_lr['left_grad'],0)
stats_ud = sp.stats.ttest_1samp(vectors_ud['left_grad'],0)
