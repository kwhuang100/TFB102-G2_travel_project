#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import random

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Source Han Sans TW']
plt.rc('legend', fontsize=16)

# 讀取檔案 CSV
one_df = pd.read_csv('./jieba/OHE_merge_40_n_ns_a_v.csv', index_col=0)
words_df = pd.read_csv('./jieba/jieba合併文章40_地名_名詞_形容詞_動詞.csv', index_col=0)
words_df = words_df.fillna('Null')
try:
    del one_df['台北']
    del one_df['台北市']
    del one_df['北市']
    del one_df['照片']
    del one_df['拍照']
    del one_df['地址']
    del one_df['地方']
except:
    pass
print(one_df.shape)
nd_data = one_df.to_numpy() # df > nd-array

# 降維 可視化
r_data = PCA(n_components=8).fit_transform(nd_data)
T_data  = TSNE(n_components=2,init="pca",random_state=0).fit_transform(r_data)
plt.figure(figsize=(15,8))
for i in random_pick:                        
    plt.annotate(one_df.index[i], xy = (T_data[i,0], T_data[i,1]), 
                 xytext = (T_data[i,0]+0.001,T_data[i,1]+0.001), fontsize=12)
    
plt.scatter(T_data[:,0], T_data[:,1], alpha = 0.5)
plt.show()