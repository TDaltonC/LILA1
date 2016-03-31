# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 13:21:09 2016

@author: Dalton
"""

treatment = "Risk" 
heuro      = "all_risk"
heur_thresh = 2
subset = all_tasks.loc[(all_tasks['treatment'] == treatment) & (all_tasks[heuro] >= heur_thresh),"sid"]

trial_by_trial = trial_by_trial_without_indifferences

trial_by_trial = trial_by_trial[trial_by_trial['sid'].isin(subset)]