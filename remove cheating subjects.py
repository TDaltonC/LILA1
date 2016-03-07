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
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices1.csv', index_col=False)
tvs = pd.DataFrame.from_csv(dataDir + 'tvs5.csv', index_col=False)
## magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'K&1', 1:'K&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
trial_by_trial['treatment'] = [treatments[x] for x in trial_by_trial['treatment']]
#%% Plot ICE by grade and treatment

treatment_summary = trial_by_trial.groupby(['sid', 'treatment', 'grade']).sum()
treatment_summary.reset_index(inplace = True)
treatment_summary = pd.merge(treatment_summary, tvs, on = ['treatment', 'sid'])
sb.factorplot(x='grade', y = 'tv', hue = 'treatment', data = treatment_summary)

#%% Oraganize things by ranking

def get_complete_ranking(group, ranker = '_exp_rank'):
#    create a duplicate of the group to be extra double sure that nothing form group carries over bwtween loops. 
    temp_group = group.copy()
    # What Rank should I use? _exp_rank or _imp_rank
    ranker = ranker
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
    return str(unique_options['rank'].tolist())


imp_rankings_series = trial_by_trial.groupby(['sid', 'treatment', 'grade']).apply(get_complete_ranking, ranker = '_imp_rank')
imp_rankings = imp_rankings_series.reset_index()
imp_rankings.rename(columns={0: 'imp_ranking'}, inplace=True)

exp_rankings_series = trial_by_trial.groupby(['sid', 'treatment', 'grade']).apply(get_complete_ranking, ranker = '_exp_rank')
exp_rankings = exp_rankings_series.reset_index()
exp_rankings.rename(columns={0: 'exp_ranking'}, inplace=True)

rankings = pd.merge(imp_rankings, exp_rankings, on = ['sid', 'treatment', 'grade'], how = 'left')

#%% 
# Remove any subjects that has [1,2,3,4,5,6,7] for either thier exp and imp ranking
# and replot ICE by grade
cheaters = rankings[
#    (rankings['exp_ranking'] == '[1, 2, 3, 4, 5, 6, 7]') &
    (rankings['imp_ranking'] == '[1, 2, 3, 4, 5, 6, 7]')
    ]

cheaters['cheater'] = 1

error_count = pd.merge(treatment_summary, cheaters, on = ['sid', 'grade', 'treatment'], how = 'left')
# replace nan's wih 0's
error_count.loc[error_count['cheater'] != error_count['cheater'],'cheater'] = 0

sb.factorplot(x='grade', y = 'ice', hue = 'treatment', data = error_count[(error_count['cheater'] == 0)])

#%% Do people that use a simple rule on the pairwise task have a prefered exp rank
