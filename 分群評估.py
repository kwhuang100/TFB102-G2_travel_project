#!/usr/bin/env python
# coding: utf-8

# 觀察輪廓係數, 誤差平方和

from sklearn.cluster import KMeans
from sklearn import metrics

import matplotlib.pyplot as plt

# 創建模型 輸入資料 儲存數據
silho = []
SSE = []
X = range(4,15)
for k in X: # 群數
    kmeans = KMeans(n_clusters=k, random_state=0) # n_clusters=群數
    result = kmeans.fit(reduced_data)
    silho.append(metrics.silhouette_score(reduced_data, result.labels_))
    SSE.append(result.inertia_)

# 使用群數數據 折線圖
fig, p_sil = plt.subplots()
plt.xlabel('cluster number')
p_sse = p_sil.twinx()

# sil
p_sil.set_ylabel('silhouette', color='tab:blue')
p_sil.plot(X, silho, 'r-o', color='tab:blue', alpha=0.75)
p_sil.tick_params(axis='y', labelcolor='tab:blue')

p_sse.set_ylabel('sse', color='tab:red')
p_sse.plot(X, SSE, 'r-o', color='tab:red', alpha=0.75)
p_sse.tick_params(axis='y', labelcolor='tab:red')

fig.tight_layout()
plt.show()

# 實際數值
for sil,sse,x in zip(silho, SSE, X):
    print(f'{x} : {round(sil,4)}, {int(sse)}') 