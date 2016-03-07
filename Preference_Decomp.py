# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 16:10:23 2016

@author: Dalton
"""

import numpy as np
import scipy as sp
import seaborn as sb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from sklearn import linear_model 
#%%
# Import the choices
dataDir = '/Users/Dalton/Documents/Projects/LILA1/dataFrames/'
trial_by_trial = pd.DataFrame.from_csv(dataDir + 'choices5.csv', index_col=False)
norms = pd.DataFrame.from_csv(dataDir + 'moral_norms.csv', index_col=['option1', 'option2'])
## Recode Choice LR so that 1 is higher rank, -1 is lower rank and 0 is indiff if you're visualizing preferences and chocies
trial_by_trial.loc[trial_by_trial['choice_LR'] == 2, 'choice_LR'] = -1
# magic strings for treatments
treatments = {1:'Goods', 2:'Risk', 3:'Social'}
age_groups = {0:'0&1', 1:'0&1', 2:'2&3', 3:'2&3', 4:'4&5', 5:'4&5', 14:'U'}
trial_by_trial['age_group'] = [age_groups[x] for x in trial_by_trial.grade]

#%%Linear decomposition of preferences. 

def linear_decomp(group, x = norms):
    # Hypothetical linear components
    usegroup = group.copy()
    x = norms[['greedy', 'equality', 'socialmax']]
    # Data I want to predict
    usegroup['opt_min'] = usegroup[['option2', 'option1']].min(axis = 1)
    usegroup['opt_max'] = usegroup[['option2', 'option1']].max(axis = 1)
    averaged = usegroup.groupby(['opt_min', 'opt_max']).mean()
    y = averaged['choice_LR'].copy()
#    demean the y vector
#    y = y - y.mean()
    regr = linear_model.LinearRegression(fit_intercept = False, normalize = True)
    regr.fit(x, y)
    norm_names = np.array(x.columns)
    zipped = dict(zip(norm_names, regr.coef_))
    zipped['intercept'] = regr.intercept_
    response = pd.DataFrame(data = zipped, index = [group['age_group'].iloc[0]])
#    response.set_index('norm', inplace = True)
#    new = response.unstack('norm')
    return response
    
social_trial_by_trial = trial_by_trial[trial_by_trial['treatment']==3]
results = social_trial_by_trial.groupby('sid').apply(linear_decomp)

normaized = results.apply(lambda row: row/np.sum(row), axis = 1)
normaized.reset_index(inplace = True)
sb.factorplot(x='level_1', y = 'greedy', data = normaized, kind="point")
sb.factorplot(x='level_1', y = 'equality', data = normaized, kind="point")
sb.factorplot(x='level_1', y = 'socialmax', data = normaized, kind="point")
sb.factorplot(x='level_1', y = 'other', data = normaized, kind="point")
