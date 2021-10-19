from math import sqrt
import operator
import pandas as pd

def loadData(res_listing):
    data ={}
    for line in res_listing:
        user,score,item = line  
        data.setdefault(user,{})
        data[user][item]=score
    return data


#計算各家餐廳總作者撰寫人數、餐廳兩兩間撰寫人數
def matrix(data):
    N={};#喜歡Ａ餐廳的總人数
    C={};#喜歡Ａ餐廳也喜歡Ｂ餐廳的人數
    for user,item in data.items():
        for i,score in item.items():
            N.setdefault(i,0)
            N[i] += 1
            C.setdefault(i,{})
            for j,scores in item.items():
                if j not in i:
                    C[i].setdefault(j,0)
                    C[i][j] += 1
    return N, C

#計算餐廳相似矩陣
def similarity(data, N , C):
    W={}
    for i,item in C.items():
        W.setdefault(i,{})
        for j,item2 in item.items():
            W[i].setdefault(j,0)
            W[i][j]= C[i][j]/ sqrt(N[i]*N[j])
    return W

W = similarity(data, N , C) 


#依據餐廳捷運站做篩選後，依照相似度排序
res_list_count = W.keys()
res_CF_TOP2Result = {}

for i in res_list:  #針對每家餐廳協同過濾的結果，篩選同樣捷運站並透過協同過濾相似度排序後進行推薦
    station_list_for_i = df_station[df_station['餐廳ID'] == int(i)]['捷運站點'].tolist() 
    
    res_CFlist = []
    save_result = []
    res_CFlist.append(res for res, w in sorted(W[i].items(),key=operator.itemgetter(1),reverse=True)[1:])
    
    for idx in res_CFlist:  #確認捷運站是否有重疊
        station_list_for_j = df_station[df_station['餐廳ID'] == int(idx)]['捷運站點'].tolist()
        check_list = [] 
        for station_j in station_list_for_j:
            if station_j in station_list_for_i:
                check_list.append(station_j)

        if len(check_list) > 0: 
            save_result.append(idx)

    if len(save_result) < 4:
        for c in range(1, 4 - len(save_result) +1):
            save_result.append("None")
                
    save_result = save_result[0:2]
    res_CF_TOP2Result[i] = save_result