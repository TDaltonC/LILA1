# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 19:35:00 2016

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
trial_by_trial_original   = pd.DataFrame.from_csv(dataDir + 'choices_all.csv', index_col=False)
social_heuristics= pd.DataFrame.from_csv(dataDir + 'simple_social_policies_unique.csv', index_col=False)
risk_heuristics = pd.DataFrame.from_csv(dataDir + 'simple_risk_policies_unique.csv', index_col=False)## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'0&1', 1:'0&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
trial_by_trial_original['treatment'] = [treatments[x] for x in trial_by_trial_original['treatment']]
trial_by_trial_original['age_group'] = [age_groups[x] for x in trial_by_trial_original['grade']]
trial_by_trial = trial_by_trial_original
#%% Reorganize the choices so they agree with the heuristic codings

def option_choice(row):
    if row.high_opt == row.option1:
        if   row.chosen_opt == 1:
            return 1
        elif row.chosen_opt ==2:
            return 2
        elif row.chosen_opt ==0:
            return 0
    else:
        if   row.chosen_opt == 1:
            return 2
        elif row.chosen_opt ==2:
            return 1
        elif row.chosen_opt ==0:
            return 0
            

trial_by_trial['high_opt'] = trial_by_trial[['option1', 'option2']].min(axis = 1)
trial_by_trial['low_opt'] = trial_by_trial[['option1', 'option2']].max(axis = 1)
trial_by_trial['high_low_choice'] = trial_by_trial.apply(option_choice, axis = 1)

trial_by_trial['option1']   = trial_by_trial['high_opt']
trial_by_trial['option2']   = trial_by_trial['low_opt']
trial_by_trial['chosen_opt']= trial_by_trial['high_low_choice']

# cut trial-by-trial down to just [sid, option1,  option2, chosen_opt]
social_choices= trial_by_trial.loc[trial_by_trial['treatment']=='Social', ['sid', 'option1', 'option2', 'chosen_opt']]
risk_choices  = trial_by_trial.loc[trial_by_trial['treatment']=='Risk', ['sid', 'option1', 'option2', 'chosen_opt']]

# merge the heuristics in to the trimmed t-b-t on option1 and option2 
social_choices = pd.merge(social_choices, social_heuristics, on = ['option1', 'option2'], how = 'left')
risk_choices = pd.merge(risk_choices, risk_heuristics, on = ['option1', 'option2'], how = 'left')

# test the behavioral columns against each of the heurisitic colunms
social_tests = social_choices.loc[:,['sid']].copy()
social_tests[social_choices.columns[4::]] = social_choices[social_choices.columns[4::]].apply(lambda column: column != social_choices['chosen_opt'])

risk_tests = risk_choices.loc[:,['sid']].copy()
risk_tests[risk_choices.columns[4::]] = risk_choices[risk_choices.columns[4::]].apply(lambda column: column != risk_choices['chosen_opt'])

# Sum the Trues (true when different)
social_deviation_scores = social_tests.groupby('sid').sum()
risk_deviation_scores = risk_tests.groupby('sid').sum()


#%% Create a column for the min distance to any social heurisitic
social_deviation_scores['all_social'] = social_deviation_scores.min(axis = 1)
    
#%% Create a column for the min distance to any Risk heurisitc 
risk_deviation_scores['all_risk'] = risk_deviation_scores.min(axis = 1)

#%% Make violation summaries
treatment_summary = trial_by_trial.groupby(['sid', 'treatment', 'grade', 'age_group', 'gender']).sum()
treatment_summary.reset_index(inplace = True)
treatment_summary = treatment_summary[['sid', 'treatment', 'grade', 'age_group', 'gender', 'ice_full', 'ice_half', 'tv_full', 'tv_half']]
# the sum of tv's counts each tv three times. 
treatment_summary['tv_full'] = treatment_summary['tv_full']/3
treatment_summary['tv_half'] = treatment_summary['tv_half']/3

goods_treatment_summary = treatment_summary[treatment_summary['treatment'] == 'Goods']
social_treatment_summary = treatment_summary[treatment_summary['treatment'] == 'Social']
risk_treatment_summary = treatment_summary[treatment_summary['treatment'] == 'Risk']

#%% Merge treatment summaries to heuristics scores
social_deviation_scores.reset_index(inplace = True)
risk_deviation_scores.reset_index(inplace = True)

social_deviation_scores = pd.merge(social_treatment_summary, social_deviation_scores, on = 'sid')
risk_deviation_scores = pd.merge(risk_treatment_summary, risk_deviation_scores, on = 'sid')

#%% plot the distribution of deviation scores
def cumm_plot_wide(dataframe, heuristic):
    dataframe.sort(heuristic, inplace = True)
    dataframe['order'] = dataframe.sort(heuristic).groupby(['age_group'])[heuristic].transform(lambda score: np.linspace(0, 1, len(score)))
    sb.lmplot(heuristic, 'order', dataframe, hue = 'age_group', fit_reg = False)

cumm_plot_wide(social_deviation_scores, 'all_social')

#%% plot corolations between tv and dev_score
sb.lmplot('all_social', 'tv_half', social_deviation_scores, hue = 'age_group')

#%% Count howmany heuristic users there are for each heurisitic in each age_group
threshold = 0
social_deviation_scores_thresh_test = social_deviation_scores.copy()
risk_deviation_scores_thresh_test   = risk_deviation_scores.copy()
#Test if each dev_score is below the threshold
social_deviation_scores_thresh_test[social_deviation_scores_thresh_test.columns[5::]] = social_deviation_scores_thresh_test[social_deviation_scores_thresh_test.columns[5::]] <= threshold
risk_deviation_scores_thresh_test[risk_deviation_scores_thresh_test.columns[5::]] = risk_deviation_scores_thresh_test[risk_deviation_scores_thresh_test.columns[5::]] <= threshold
#Group by age_group and sum the Trues
social_strategy_count = social_deviation_scores_thresh_test.groupby('grade').mean()
risk_strategy_count = risk_deviation_scores_thresh_test.groupby('grade').mean()

#Save to scv
#social_strategy_count.loc[:,social_heuristics.columns[2::]].to_csv('social_strategy_count1.csv')
#risk_strategy_count.loc[:,risk_heuristics.columns[2::]].to_csv('risk_strategy_count1.csv')


#%% Plot the main effect removing some heuristic users
all_tasks = goods_treatment_summary.append(social_deviation_scores, ignore_index = True)
all_tasks = all_tasks.append(risk_deviation_scores, ignore_index = True)
measure = 'tv_half'
threshold = 2


#Social
social_plot = sb.factorplot(
    x='age_group',
    y = 'tv_half',
    hue = 'treatment',
    data = all_tasks[
        ((all_tasks['all_social'] >= threshold) |
        (all_tasks['treatment']=='Goods')) &
        (all_tasks['treatment']!='Risk')],
    kind="point",
    x_order = ['0&1', '2&3', '4&5', 'U'])
social_plot.savefig('../Figures/social_remove0and1.svg', format =  'svg')

#Risk
risk_plot = sb.factorplot(
    x='age_group',
    y = 'tv_half',
    hue = 'treatment',
    data = all_tasks[
        ((all_tasks['all_risk'] >= threshold) |
        (all_tasks['treatment']=='Goods')) &
        (all_tasks['treatment']!='Social')],
    kind="point",
    x_order = ['0&1', '2&3', '4&5', 'U'])
risk_plot.axes[0,0].set_ylim(0,6) 

risk_plot.savefig('../Figures/risk_remove0and1.svg', format =  'svg')

#%% fold the dis-scores back in to the trial by trial. 

trial_by_trial_with_disc = pd.merge(trial_by_trial_original, risk_deviation_scores.drop(['ice_half', 'ice_full', 'tv_half', 'tv_full'], axis = 1), on = ['sid', 'treatment', 'grade','age_group', 'gender'], how = 'left')

trial_by_trial_with_disc = pd.merge(trial_by_trial_with_disc, social_deviation_scores.drop(['ice_half', 'ice_full', 'tv_half', 'tv_full'], axis = 1), on = ['sid', 'treatment', 'grade','age_group', 'gender'], how = 'left')
