# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 19:14:41 2016

@author: Dalton
"""
import pandas as pd
import numpy as np
import scipy as sp
import seaborn as sb
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from remove_indifference_from_rank import remove_rank_indifferences
#%%
# Import the choices
dataDir = '/Users/Dalton/Documents/Projects/LILA1/dataFrames/'
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices_all.csv', index_col=False)
trial_by_trial_without_indifferences = trial_by_trial.groupby(['sid', 'treatment']).apply(remove_rank_indifferences, ranker = '_imp_rank')
trial_by_trial_without_indifferences.reset_index(inplace = True, drop = True)
trial_by_trial = trial_by_trial_without_indifferences
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'K&1', 1:'K&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}

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
bbr_map = {
         'red':   ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 0.0),
                   (1.0, 1.0, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 1.0, 1.0),
                   (0.5, 0.0, 0.0),
                   (1.0, 0.0, 0.0))}
greener = colors.LinearSegmentedColormap('Green_map', green_map)
reder = colors.LinearSegmentedColormap('Red_map', red_map)
bbr = colors.LinearSegmentedColormap('bbr_map', bbr_map)

#%% Functions

def heatmap_fromDF(data, **kwargs):
    heatdata = pd.pivot_table(
        data,
        values='ice_full',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    mask = heatdata != heatdata
    sb.heatmap(
        heatdata, 
        mask = mask, 
        cmap = "gist_heat", 
#        cbar = False,
        vmin = 0, 
        vmax = 0.2, 
        **kwargs)
        
def slope_heatmap_fromDF(data, **kwargs):
    data['slope'] = -data['slope']
    heatdata = pd.pivot_table(
        data,
        values='slope',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    mask = heatdata != heatdata
    sb.heatmap(
        heatdata, 
        mask = mask, 
        cmap = bbr,
        center = 0,
        cbar = False,
        vmin = -0.03, 
        vmax =  0.03, 
        **kwargs)
        
def intercept_heatmap_fromDF(data, **kwargs):
    heatdata = pd.pivot_table(
        data,
        values='intercept',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    mask = heatdata != heatdata
    sb.heatmap(
        heatdata, 
        mask = mask, 
        cmap = greener, 
        cbar = False,
        vmin = 0, 
        vmax = 0.2, 
        **kwargs)

def p_value_heatmap_fromDF(data, **kwargs):
    data["p_value"][data.p_value > .0001] = 1 
    heatdata = pd.pivot_table(
        data,
        values='p_value',
        index='rank_low',
        columns='rank_high', 
        aggfunc=np.mean)
    mask = heatdata != heatdata
    sb.heatmap(
        heatdata, 
        mask = mask, 
        cmap = "winter", 
  #      annot = True
  #      cbar = False,
  #      vmin = 0, 
  #      vmax = 0.5, 
        **kwargs)

#%%
# Plot all of the data across all subjects
heatdata = pd.pivot_table(trial_by_trial,
                          values='ice_full',
                          index='rank_low',
                          columns='rank_high', 
                          aggfunc=np.mean)
    
mask = heatdata != heatdata
plot = sb.heatmap(heatdata, mask = mask, cmap = "gist_heat")
sb.plt.title('Inconsistencies with Elicited Rank - All Ages')


#%%
## Plot each treatment for each subeject
grade_treatment_grouped = trial_by_trial.groupby(["grade", "treatment", 'sid'])
for name, group in grade_treatment_grouped:
    plt.figure()
    treatment = [treatments[x] for x in group.treatment]
    heatdata = pd.pivot_table(group,
                          values='ice_full',
                          index='rank_low',
                          columns='rank_high', 
                          aggfunc=np.mean)
    mask = heatdata != heatdata
    plot = sb.heatmap(heatdata, mask = mask, cmap = "gist_heat")    

#%%
## Plot each subtask for each grade
grade_treatment_grouped = trial_by_trial.groupby(["grade", "treatment"])
for name, group in grade_treatment_grouped:
    
    plt.figure()
    treatment = [treatments[x] for x in group.treatment]
    heatdata = pd.pivot_table(group,
                          values='ice_full',
                          index='rank_low',
                          columns='rank_high', 
                          aggfunc=np.mean)
    mask = heatdata != heatdata
    plot = sb.heatmap(heatdata, mask = mask, cmap = "gist_heat")
#    sb.plt.title('Inconsistencies in ' + treatment + ' treatment, grade ' + str(name[0]))

#%% Print a facet plot for each grade
grade_grouped = trial_by_trial.groupby("grade")
for name, group in grade_grouped:
    group['treatment'] = [treatments[x] for x in group.treatment]
    plt.figure()
    g = sb.FacetGrid(group, col="treatment", col_wrap=2)
    g = g.map_dataframe(heatmap_fromDF).set_titles("{col_name} Treatment")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle('Grade '+ str(name))
    
#%% Print a fact plot for each age group (Grouped in the K-1 2-3 4-5 U)

trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial.grade]
age_grouped = trial_by_trial.groupby('age_group')
for name, group in age_grouped:
    group['treatment'] = [treatments[x] for x in group.treatment]
    plt.figure()
    g = sb.FacetGrid(group, col="treatment", col_wrap=2)
    g = g.map_dataframe(heatmap_fromDF).set_titles("{col_name} Treatment")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle('Group '+ str(name))
    
    
#%% Do a regression for each sqaure in the heatmap across age.
    # Make a heatmap where the "intercept" is in red and the "slope" is in green. 
    # That will tell us what squares are "good and improving" "Bad but improving"
    
## Example cell regression with age
 # Recode undergrads to 6
regression_DF = trial_by_trial
regression_DF["grade"][regression_DF.grade == 14] = 6 
#regression_DF["grade"] = regression_DF["grade"] - 3


# groupby treatment, rank_high, rank_low 
trial_grouped = regression_DF.groupby(['treatment', 'rank_high','rank_low'])
# add the regression stats as columns

def regress_grade_and_ice_red(group):
#    group.plot(x = 'grade', y = 'ice', kind = 'scatter')
#    sb.lmplot(x = 'grade', y = 'ice', data = group)
    slope, intercept, r_value, p_value, stderr =  sp.stats.linregress(group.grade, group.ice_full)
    return pd.DataFrame({'slope': slope,'intercept': intercept, 'p_value': p_value}, index = group.name)

heahmap_data = trial_grouped.apply(regress_grade_and_ice_red)
heahmap_data = heahmap_data.reset_index()
heahmap_data = heahmap_data.drop_duplicates(['treatment', 'rank_high','rank_low'])
heahmap_data['treatment'] = [treatments[x] for x in heahmap_data.treatment]

plt.figure()
g = sb.FacetGrid(heahmap_data, col="treatment", col_wrap=2)
slope_plot = g.map_dataframe(slope_heatmap_fromDF).set_titles("{col_name} Treatment")
plt.subplots_adjust(top=0.9)
g.fig.suptitle('Regression Slopes')

h = sb.FacetGrid(heahmap_data, col="treatment", col_wrap=2)
intercept_plot = h.map_dataframe(intercept_heatmap_fromDF).set_titles("{col_name} Treatment")
plt.subplots_adjust(top=0.9)
h.fig.suptitle('Regression Intercepts')

p = sb.FacetGrid(heahmap_data, col="treatment", col_wrap=2)
p_plot = p.map_dataframe(p_value_heatmap_fromDF).set_titles("{col_name} Treatment")
plt.subplots_adjust(top=0.9)
p.fig.suptitle('Regression p-value')