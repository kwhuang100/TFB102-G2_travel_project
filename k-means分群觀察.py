#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from collections import Counter

from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Source Han Sans TW']
plt.rc('legend', fontsize=16)

import random

# 儲存各群關鍵字
def words_label():
    label_word_dict = {}
    for i in label_name_dict:
        tmp = []
        for j in label_name_dict[i]:
            tmp += words_df.loc[j].tolist()
        while 'Null' in tmp:
            tmp.remove('Null')
        while '台北' in tmp:
            tmp.remove('台北')
        while '台北市' in tmp:
            tmp.remove('台北市')
        while '北市' in tmp:
            tmp.remove('北市')
        while '照片' in tmp:
            tmp.remove('照片')
        while '拍照' in tmp:
            tmp.remove('拍照')
        while '地址' in tmp:
            tmp.remove('地址')
        while '地方' in tmp:
            tmp.remove('地方')

        label_word_dict[i] = {}
        for x,y in Counter(tmp).most_common(30):
            label_word_dict[i][x]=y
    return label_word_dict

# 繪製關鍵字統計圖
def bar_plot(X,label_word_dict):
    plt.figure(figsize=(40,10))
    plt.bar(label_word_dict[X].keys(),label_word_dict[X].values(),width=0.5)

    for a,b in label_word_dict[X].items():
        plt.text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom',fontsize=25)

    plt.xticks(fontsize=25)
    plt.ylim(min(label_word_dict[X].values())-2,max(label_word_dict[X].values())+2)
    plt.yticks(fontsize=25)
    plt.title(f'G{X}')
    plt.show()
    
# 讀取檔案
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
print(len(one_df.columns))
nd_data = one_df.to_numpy() # df > nd-array
    
# 降維
pca_data = PCA(n_components=700).fit_transform(nd_data)
reduced_data  = TSNE(n_components=2,init="pca",random_state=0).fit_transform(pca_data)

    
n_cluster = int(input('請輸入分群數:'))
kmeans = KMeans(n_clusters=n_cluster) # n_clusters=群數
result = kmeans.fit(reduced_data)

# 依據標籤分開數據
label_dict = dict()
label_name_dict = dict()
rl = result.labels_

for n in set(result.labels_): # create key標籤, value=nd.array(), shape=(0,2)
    label_dict[str(n)]=np.empty(shape=(0,2)) #
    label_name_dict[str(n)]=[]

# 依序把對應標籤的二維資料加入該群標籤的list中
for i in range(len(rl)):
    label_dict[str(rl[i])] = np.append(label_dict[str(rl[i])],[reduced_data[i]],axis=0)
    label_name_dict[str(rl[i])].append(list(one_df.index)[i])
    
# ===================================
# 文字分群
label_word_dict = words_label()
# ===================================

# 繪製散點圖
plt.figure(figsize=(15,10))
alpha = 0.5 # 透明度
marker = 'x' # 點樣式
try:
    plt.scatter(label_dict['0'][:,0], label_dict['0'][:,1], alpha = alpha, color='red', marker='X', label = 'G{}，{}個，佔{}%'.format(0, len(label_dict['0']), round(len(label_dict['0'])/len(rl)*100,2)))
    plt.scatter(label_dict['1'][:,0], label_dict['1'][:,1], alpha = alpha, color='orange', marker='H', label = 'G{}，{}個，佔{}%'.format(1, len(label_dict['1']), round(len(label_dict['1'])/len(rl)*100,2)))
    plt.scatter(label_dict['2'][:,0], label_dict['2'][:,1], alpha = alpha, color='darkgoldenrod', marker='s', label = 'G{}，{}個，佔{}%'.format(2, len(label_dict['2']), round(len(label_dict['2'])/len(rl)*100,2)))
    plt.scatter(label_dict['3'][:,0], label_dict['3'][:,1], alpha = alpha, color='green', marker='D', label = 'G{}，{}個，佔{}%'.format(3, len(label_dict['3']), round(len(label_dict['3'])/len(rl)*100,2)))
    plt.scatter(label_dict['4'][:,0], label_dict['4'][:,1], alpha = alpha, color='dodgerblue', marker='^',label = 'G{}，{}個，佔{}%'.format(4, len(label_dict['4']), round(len(label_dict['4'])/len(rl)*100,2)))
    plt.scatter(label_dict['5'][:,0], label_dict['5'][:,1], alpha = alpha, color='darkblue', marker='<', label = 'G{}，{}個，佔{}%'.format(5, len(label_dict['5']), round(len(label_dict['5'])/len(rl)*100,2)))
    plt.scatter(label_dict['6'][:,0], label_dict['6'][:,1], alpha = alpha, color='purple', marker='o', label = 'G{}，{}個，佔{}%'.format(6, len(label_dict['6']), round(len(label_dict['6'])/len(rl)*100,2)))
    plt.scatter(label_dict['7'][:,0], label_dict['7'][:,1], alpha = alpha, color='fuchsia', marker='>', label = 'G{}，{}個，佔{}%'.format(7, len(label_dict['7']), round(len(label_dict['7'])/len(rl)*100,2)))
    plt.scatter(label_dict['8'][:,0], label_dict['8'][:,1], alpha = alpha, color='yellow', marker='P', label = 'G{}，{}個，佔{}%'.format(8, len(label_dict['8']), round(len(label_dict['8'])/len(rl)*100,2)))
except:
    pass

for x in label_dict:
    random_pick = random.sample(range(len(label_name_dict[x])), len(label_name_dict[x])//5)
    for i in random_pick:
        plt.annotate(label_name_dict[x][i], xy = (label_dict[x][i,0], label_dict[x][i,1]),
                     xytext = (label_dict[x][i,0]+0.001,label_dict[x][i,1]+0.001), fontsize=12)
plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')
plt.tight_layout()
plt.show()

# 觀察各群
X = input('選擇群:') # 選擇分群
plt.figure(figsize=(10,7))

color_list = ['red','orange','gold','green','dodgerblue','darkblue','purple','fuchsia','yellow','b','r','green']
marker_list = ['X','H','s','D','^','<','o','>','+','d','X','X','X']
sublabel = '第{}群，{}個，佔{}%'.format(X, len(label_dict[X]), round(len(label_dict[X])/len(rl)*100,2))
plt.scatter(label_dict[X][:,0], label_dict[X][:,1], alpha = alpha, 
            color=color_list[int(X)], marker=marker_list[int(X)], label=sublabel)

for i in range(len(label_dict[X])):
    plt.annotate(label_name_dict[X][i], xy = (label_dict[X][i,0], label_dict[X][i,1]),
                 xytext = (label_dict[X][i,0]+0.001,label_dict[X][i,1]+0.001), fontsize=12)

plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper right')
plt.tight_layout()
plt.title(f'第 {X} 群分布')
plt.xticks(np.arange(reduced_data[:,0].min(), reduced_data[:,0].max()+0.3))
plt.yticks(np.arange(reduced_data[:,1].min(), reduced_data[:,1].max()+0.3))
plt.show()

print(label_name_dict[X])
bar_plot(X,label_word_dict)

