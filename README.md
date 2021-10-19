# TFB102-G2_雙北同玩捷
## 台北捷運旅遊推薦系統<br>

## 專題引言及架構<br>
<br>
<br>


## 資料蒐集與清洗<br>
<br>
<br>


## 資料庫建置<br>
#### 使用資料庫<br>
關聯式資料庫-MySQL<br>
非關聯式資料庫-MongoDB<br>
#### 建置方式<br>
雲端建置-Aamzon RDS、Atlas服務<br>
使用原因：彈性、協同合作方便、避免硬體設備故障資料遺失<br>
#### 資料儲存規劃<br>
Aamzon RDS->MySQL-儲存經整理後的關聯式table eg.餐廳列表、景點列表等<br>
Atlas->MongoDB-儲存爬取下來、尚未整理之原始資料 eg.景點評論、景點遊記、餐廳食記<br>
<br>
## 演算法及分析<br>
## Part 1-分群<br>
#### 分群使用資料<br>
爬蟲蒐集之各大景點遊記
#### 分群步驟<br>
(1) NLP預處理：Jieba斷詞及詞性篩選、TF/IDF、One-hot編碼<br>
(2) 分群模型<br>
(3) 風格貼標<br>
#### 分群方式<br>
嘗試不同分群演算法<br>
(1) K-means<br>
(2) 階層式分群<br>
(3) DBSCAN<br>
#### 分群結果<br>
(1) PCA+TSNE降維->K-means分群<br>
(2) 經調整得到7個風格群<br>
(3) 風格群貼標：登山健行、戶外踏青、藝文館所、宗教祈福、親子共遊、文化古蹟、主題商圈<br>
<br>
## Part 2-word2vec<br>
<br>
<br>

## Part 3-協同過濾<br>
<br>
<br>

## Part 4-圖片辨識<br>
<br>
<br>



## 作品展示與前後端串接<br>
<br>
<br>



## 未來展望<br>
<br>
<br>


