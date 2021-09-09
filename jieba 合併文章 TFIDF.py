
import jieba
import jieba.analyse
jieba.set_dictionary("./dict.txt") # 設定繁體中文字典
jieba.analyse.set_stop_words('stop2.txt') # 停用詞字典設定
import pandas as pd
from time import time

raw_df = pd.read_csv('全部文章統整0809.csv')
data = raw_df.groupby('景點').apply(lambda x: '\n'.join(x['文章內文'])).reset_index()
data.columns = ['景點','內文']

# ## n=取幾個字, allowPOS=[詞性篩選]

def merge_article_tfidf(n, filename):
    place_name_list = list(data.景點)
    article_list = list(data.內文)
    # TF/IDF
    place_words = []
    for i, article in enumerate(article_list):
        words = jieba.analyse.extract_tags(article, n, allowPOS=['n','ns','a','v'])
        place_words.append(words)
        print('finish', place_name_list[i])
    
    # DataFrame, CSV
    new_df = pd.DataFrame({'關鍵字':place_words}, index=place_name_list)
    new_df = new_df.關鍵字.apply(pd.Series)
    new_df.to_csv(filename)

if __name__ == "__main__":
    n = int(input('抓前幾個關鍵字:'))
    filename = input('檔案名稱:')
    st = time()
    merge_article_tfidf(n, filename)
    print((time()-st),'seconds')

