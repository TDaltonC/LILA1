
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 15:27:16 2016

This script transforms the tv files that Niree sent me in to a form that the
rest of this analysis can deal with. 

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
tvs = pd.DataFrame.from_csv(dataDir + 'tvs5.csv', index_col='sid')
## magic strings for treatments
treatments_tv = {'tv1':'Goods', 'tv2':'Risk', 'tv3':'Social'}

long_tvs = tvs.stack()

long_tvs_df = long_tvs.reset_index()

long_tvs_df.rename(columns={'level_1': 'treatment', 0: 'tv'}, inplace=True)
long_tvs_df['treatment'] = [treatments_tv[x] for x in long_tvs_df.treatment]

long_tvs_df.to_csv(dataDir + 'tvs5.csv', index = False)
