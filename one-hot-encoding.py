#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# read file to raw_df
raw_df = pd.read_csv('jieba合併文章40_名詞_地名_形容詞_動詞.csv', index_col=0)
raw_df.columns = ['w' for x in range(40)] # 更改欄位名稱 統一欄位名稱
one_hot_df = pd.get_dummies(raw_df) # one-hot encoding
# create new_df
new_df=pd.DataFrame()
col_list = list(one_hot_df.columns)
for i in col_list:
    new_df[i.strip('w_')] = one_hot_df[[i]].sum(axis=1)
# save to csv
try:
    del new_df['Null']
    print('del Null')
except:
    pass
new_df = new_df.astype('float32')
new_df.to_csv('OHE_merge_40_n_ns_a_v.csv')

