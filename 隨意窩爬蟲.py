#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import re
import time
import os
import pandas as pd
import random
import json
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56'

headers = {
    'User-Agent': userAgent
}

timeoutSec = 5
def read_place(filename):
    place = pd.read_csv(filename, index_col=0)
    return list(place.Name_Mapping)[::-1] # 景點 index

def read_right_proxy():
    with open('./right_proxy_list.txt','r',encoding='utf-8') as f:
        raw_list = f.read()
    right_proxy = raw_list.split('\n')
    right_proxy.remove(right_proxy[-1])
    return right_proxy

def change_proxy(right_proxy, proxy):
    try:
        right_proxy.remove(proxy)
    except:
        pass
    proxy = random.choice(right_proxy)
    proxies = {
                "http": "http://"+proxy,
                "https": "http://"+proxy,
            }
    return proxies, proxy


AttractList = read_place('0727clean.csv')

# data save
AllArticleList = []
count = 0

# proxy
right_proxy = read_right_proxy()
proxy = random.choice(right_proxy)
proxies, proxy = change_proxy(right_proxy, proxy)

for Attract in AttractList[581:]:
    title_count = 0
    for page in range(0, 100, 10):
        wrong = 0
        to_next=False

        while True:
            print(wrong)
            if to_next:
                break
            while True:
                pageUrl = "https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=10&hl=zh-TW&source=gcsc&gss=.com&start={}&cselibv=b54a745638da8bbb&cx=016796754892695415736:ajiucjnimri&q={}&safe=off&cse_tok=AJvRUv22jHRGXNlurCSe7ndwAL8v:1628141236565&sort=&exp=csqr,cc&callback=google.search.cse.api{}".format(page
                , Attract, random.randint(1000,9999))
                print(Attract, page, end=' | ')
                try:
                    res = requests.get(pageUrl, proxies=proxies,timeout=timeoutSec)
                    print(res.status_code, end=' ')
                    if res.status_code == 200:
                        break
                    else:
                        wrong += 1
                        if len(right_proxy)<=1:
                            right_proxy = read_right_proxy()
                        print(-1,end=' ')
                        proxies, proxy = change_proxy(right_proxy, proxy)

                except:
                    wrong += 1
                    if len(right_proxy)<=1:
                        right_proxy = read_right_proxy()
                    print(-2,end=' ')
                    proxies, proxy = change_proxy(right_proxy, proxy)

            res.encoding ='utf-8'
            jsondata = json.loads(res.text.strip("/*O_o*/"+"\n"+"google.search.cse.api"+"0123456789"+"("+";"+")"))
            
            try:
                # 解析頁面json
                a = jsondata['results']
                wrong = 0
                to_next=False
                break
            except:
                wrong += 1
                if wrong > 50:
                    to_next = True
                if len(right_proxy)<=1:
                    right_proxy = read_right_proxy()
                print(-3,end=' ')
                proxies, proxy = change_proxy(right_proxy, proxy)
                continue
        
        if to_next:
            break
        
        for i, n in enumerate(jsondata['results']):

            Attract_df = []
            ArticleTitle_df = []
            ArticleAuthor_df = []
            ArticleDate_df = []
            ArticleUrl_df = []
            ArticleContent_df = []

            ArticleTitle = n['titleNoFormatting']
            ArticleUrl = n['unescapedUrl']
            try:
                ArticleAuthor = n['richSnippet']['metatags']['author']
            except:
                ArticleAuthor = "Unknown"
            re_t = re.sub('[\s+\.\!\/_,$%^*(+\"\']+|[+——！:：，。？、~@#￥%……&*（）]+', '', ArticleTitle)

            # 排除文章by標題
            if Attract not in re_t:
                title_count += 1
                continue
            print('=============================')
            print(i, Attract, re_t, ArticleAuthor, end = ' ')

            while True:
                try:
                    resArticle = requests.get(ArticleUrl,proxies=proxies,timeout=timeoutSec)
                    if res.status_code == 200:
                        break
                    else:
                        if len(right_proxy)<=1:
                            right_proxy = read_right_proxy()
                        proxies, proxy = change_proxy(right_proxy, proxy)
                except:
                    if len(right_proxy)<=1:
                        right_proxy = read_right_proxy()
                    proxies, proxy = change_proxy(right_proxy, proxy)

            # 解析文章
            resArticle.encoding ='utf-8'
            ArticleSoup = BeautifulSoup(resArticle.text, 'html.parser')

            #  日期
            try:
                year = ArticleSoup.select_one('span.titledate-year').text
                month = ArticleSoup.select_one('span.titledate-month').text
                day = ArticleSoup.select_one('span.titledate-day').text       
                ArticleDate = year + '-' + month + '-' + day
                print(ArticleDate)

            except: 
                ArticleDate = 'Null'
                print(ArticleDate)

            # 文章內容
            ArticleContentList = ArticleSoup.select('div[id = content_all]')
            for ArticleContent in ArticleContentList:

                ContentList = ArticleContent.select('p')
                Content_text = str()

                for Content in ContentList:
                    Content_text += Content.text

            if not Content_text:
                continue
            # 存入 dataframe & csv
            count += 1

            Attract_df.append(Attract)
            ArticleTitle_df.append(re_t)
            ArticleAuthor_df.append(ArticleAuthor)
            ArticleDate_df.append(ArticleDate)
            ArticleUrl_df.append(ArticleUrl)
            ArticleContent_df.append(Content_text)

            ArticleList = [count, Attract_df, ArticleTitle_df, ArticleUrl_df, ArticleDate_df, ArticleAuthor_df, ArticleContent_df]
            AllArticleList.append(ArticleList)

            col = ['_id', '景點', '文章標題', '文章連結', '日期','作者','內文']
            df_all_attrs = pd.DataFrame(AllArticleList, columns=col)
            df_all_attrs.to_csv('隨意窩_08051421.csv', index=False)
            title_count = 0 
            
        print('=========='+' Page : '+str(int((page+10)/10))+' finish '+'==========')
        if title_count == 30:
            break
    
    print('=========='+' Attraction : '+str(Attract)+' finish '+'==========')

