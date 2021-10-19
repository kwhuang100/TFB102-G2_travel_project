#!/usr/bin/env python
# coding: utf-8

# In[19]:


from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, FollowEvent, UnfollowEvent,ImageMessage,
    TextMessage, TextSendMessage, FlexSendMessage,ImageSendMessage,
    TemplateSendMessage,BaseSize,ImagemapArea,
    PostbackTemplateAction, MessageTemplateAction, PostbackAction,
    ImagemapSendMessage, MessageImagemapAction,ButtonsTemplate, QuickReply, QuickReplyButton
)
from random import choice, sample
from numpy import expand_dims
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from keras.models import load_model
from heapq import nlargest
import pymysql
from os import getcwd
from os import remove as OSremove
import requests

# 捷運 快選訊息
def Get_MRT_quick_button():
    message=TextSendMessage(
        text = '~選擇捷運線~',
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    image_url = 'https://i.kfs.io/playlist/global/64010205v2/fit/500x500.png',
                    action=PostbackAction(label="淡水信義線",data="淡水信義線",display_text="❤淡水信義線")
                    ),
                QuickReplyButton(
                    image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Taipei_Metro_Line_BL.svg/1200px-Taipei_Metro_Line_BL.svg.png',
                    action=PostbackAction(label="板南線",data="板南線",display_text="💙板南線")
                    ),
                QuickReplyButton(
                    image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Taipei_Metro_Line_G.svg/330px-Taipei_Metro_Line_G.svg.png',
                    action=PostbackAction(label="松山新店線",data="松山新店線",display_text="💚松山新店線")
                    ),
                QuickReplyButton(
                    image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Taipei_Metro_Line_O.svg/1200px-Taipei_Metro_Line_O.svg.png',
                    action=PostbackAction(label="中和新蘆線",data="中和新蘆線",display_text="🧡中和新蘆線")
                    ),
                QuickReplyButton(
                    image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Taipei_Metro_Line_BR.svg/1036px-Taipei_Metro_Line_BR.svg.png',
                    action=PostbackAction(label="文湖線",data="文湖線", display_text="🤎文湖線")
                    ),
                QuickReplyButton(
                    image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Taipei_Metro_Line_Y.svg/777px-Taipei_Metro_Line_Y.svg.png',
                    action=PostbackAction(label="環狀線",data="環狀線",display_text="💛環狀線")
                    )
                ]
            )
        )
    return message

# ImagemapSendMessage 圖片組圖訊息
def Get_ImageMap_Message1():
    message = ImagemapSendMessage(
        base_url= "https://tfb102g2main.herokuapp.com"+r'/tmp/new_st1',
        alt_text='選一個您最喜歡的景點吧!',
        base_size=BaseSize(height=1040, width=1040),
        actions=[
            MessageImagemapAction(
                text='士林官邸',
                area=ImagemapArea(
                    x=0, y=0, width=520, height=520
                )
            ),
            MessageImagemapAction(
                text='信義商圈',
                area=ImagemapArea(
                    x=520, y=0, width=520, height=520
                )
            ),
            MessageImagemapAction(
                text='天母夢想公園',
                area=ImagemapArea(
                    x=0, y=520, width=520, height=520
                )
            ),
            MessageImagemapAction(
                text='華山文創',
                area=ImagemapArea(
                    x=520, y=520, width=520, height=520
                )
            ),
        ]
    )
    return message

# ImagemapSendMessage 圖片組圖訊息
def Get_ImageMap_Message2():
    message = ImagemapSendMessage(
        base_url= "https://tfb102g2main.herokuapp.com"+r'/tmp/new_st2',
        alt_text='再選一個您最喜歡的景點唷!',
        base_size=BaseSize(height=1040, width=1040),
        actions=[
            MessageImagemapAction(
                text='城隍廟',
                area=ImagemapArea(
                    x=0, y=0, width=520, height=520
                )
            ),
            MessageImagemapAction(
                text='大湖公園',
                area=ImagemapArea(
                    x=520, y=0, width=520, height=520
                )
            ),
            MessageImagemapAction(
                text='虎山溪步道',
                area=ImagemapArea(
                    x=0, y=520, width=520, height=520
                )
            ),
            MessageImagemapAction(
                text='迪化街',
                area=ImagemapArea(
                    x=520, y=520, width=520, height=520
                )
            ),
        ]
    )
    return message

# check_status
def check_status(user_ID):
    sql_str = 'select user_status from user_table where user_id = "{}"'.format(user_ID)
    cursor_user.execute(sql_str)
    return cursor_user.fetchone()[0]

# 計算 使用者座標
def calculate_and_save_user_point(user_ID):
    sql_str = f'select X, Y from Attraction_styles where group_id = (select user_label_1 from user_table where user_id="{user_ID}")'
    cursor_user.execute(sql_str)
    point1 = cursor_user.fetchone()
    sql_str = f'select X, Y from Attraction_styles where group_id = (select user_label_2 from user_table where user_id="{user_ID}")'
    cursor_user.execute(sql_str)
    point2 = cursor_user.fetchone()
    user_X = round((point1[0]+point2[0])/2,6)
    user_Y = round((point1[1]+point2[1])/2,6)
    cursor_user.execute(f"update group2_mysql.user_table set user_X={user_X}, user_Y={user_Y}, user_status=1 where user_id='{user_ID}'")
    db.commit()
    return None

# 冷啟動
def cold_start(user_ID, resp_text, event):
    if resp_text == '雙北同玩捷🚃出遊趣':
        message1 = TextSendMessage(text='請選擇一個最感興趣的景點😍')
        message2 = Get_ImageMap_Message1()
        line_bot_api.reply_message(event.reply_token,[message1,message2])
    elif resp_text == '士林官邸' or resp_text == '信義商圈' or resp_text == '天母夢想公園' or resp_text == '華山文創':
    # 接收第一個回答 儲存進資料庫 回傳第二個問卷圖片
        sql_str = f'update group2_mysql.user_table set user_label_1={test_dict[resp_text]} where user_id="{user_ID}"'
        cursor_restart.execute(sql_str)
        db.commit()
    # SQL 存資料庫
        message1 = TextSendMessage(text=f'它是 {resp_text}😚再選一個就好囉😍')
        message2 = Get_ImageMap_Message2()
        line_bot_api.reply_message(event.reply_token,[message1,message2])
    elif resp_text == '迪化街' or resp_text == '虎山溪步道' or resp_text == '大湖公園' or resp_text == '城隍廟':
    # 接收第二個回答 儲存進資料庫 回傳可以開始使用訊息!
        sql_str = f'update group2_mysql.user_table set user_label_2={test_dict[resp_text]} where user_id="{user_ID}"'
        cursor_restart.execute(sql_str)
        db.commit()
        message1 = TextSendMessage(text=f'它是 {resp_text}😚')
        message2 = TextSendMessage(text='完成😍 可以開始使用選單功能囉，或是輸入 "查看使用說明" 先了解使用說明唷~GO~出遊趣🚃')
        line_bot_api.reply_message(event.reply_token,[message1,message2])
    # SQL 存資料庫 user_X, user_Y, user_status
        calculate_and_save_user_point(user_ID)
    else:
    # 回答失敗 回傳第一個問卷圖片...
        message1 = TextSendMessage(text='請重新再選一次吧🥺')
        message2 = Get_ImageMap_Message1()
        #message2 = TextSendMessage(text=f'{getcwd()}')
        line_bot_api.reply_message(event.reply_token,[message1,message2])
    return None

# 獲得使用者座標
def get_user_point(user_ID):
    cursor_user.execute(f"select user_X, user_Y from user_table where user_id = '{user_ID}'")
    return cursor_user.fetchone()

# 計算使用者推薦順序
def get_Attractions_order(user_ID, user_X, user_Y):
    cursor_recom.execute(f"select place_id, group_id, X, Y from Attractions where     group_id = (select user_label_1 from user_table where user_id = '{user_ID}') or     group_id = (select user_label_2 from user_table where user_id = '{user_ID}')")
    Attractions_tuple = cursor_recom.fetchall()
    Att_dict = {}
    for i in Attractions_tuple:
        Att_dict[str(i[0])] = ((user_X-i[2])**2+(user_Y-i[3])**2)**0.5,i[1]
    return sorted(Att_dict.items(), key=lambda x:x[1][0])

# 取得 W2V景點推薦
def Get_place_info_W2V(place):

    # 儲存第一個景點資訊
    cursor_recom.execute("select place, pic_url, web_url, group_id from Attractions where place_id = {}".format(place[0]))
    p = cursor_recom.fetchall()[0]
    pic_url = [p[1]]
    place_name = [p[0]]
    Taipei_url = [p[2]]
    p_label = [p[3]]
    cursor_recom.execute('select station from Attractions_to_stations where place_id={}'.format(place[0]))
    s = ''
    for i in cursor_recom.fetchall():
        s = s + i[0] + ' '
    station = [s]

    # 儲存 W2V 景點資訊
    sql=f"select w.simi_place_id, a.group_id, a.place, a.pic_url, a.web_url      from W2V_similarity w       join Attractions a on (w.simi_place_id = a.place_id)       join Attraction_styles g on (a.group_id = g.group_id)       where w.place_id = {place[0]}       order by w.w2v_id"

    cursor_recom.execute(sql)
    data = cursor_recom.fetchall()
    for i in data:
        pic_url.append(i[3])
        place_name.append(i[2])
        Taipei_url.append(i[4])
        p_label.append(i[1])
        cursor_recom.execute(f"select station from Attractions_to_stations where place_id = {i[0]}")
        s = ''
        for i in cursor_recom.fetchall():
            s = s + i[0] + ' '
        station.append(s)
    return pic_url, place_name, station, Taipei_url, p_label

# 餐廳評分
def star_point(point):
    if point == 4.0:
    # 4.0
        star_p = [{'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png'},
             {'type': 'text','text': '4.0','size': 'sm','color': '#999999','margin': 'md','flex': 0}]
    elif point < 5.0:
    # 4.1~4.9
        star_p = [{'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://uxwing.com/wp-content/themes/uxwing/download/36-arts-graphic-shapes/star-half-yellow.png'},
             {'type': 'text','text': str(point),'size': 'sm','color': '#999999','margin': 'md','flex': 0}]
    elif point == 5.0:
    # 5.0
        star_p = [{'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'icon','size': 'sm','url': 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'},
             {'type': 'text','text': '5.0','size': 'sm','color': '#999999','margin': 'md','flex': 0}]
    return star_p

# 餐廳單格訊息
def Create_Res_bubble(R_image,R_name,R_tag,star_point,R_address):
    Restaurant =  {'type': 'bubble',
     'hero': {'type': 'image',
      'url': R_image, # 圖片連結
      'size': 'full','aspectRatio': '20:13','aspectMode': 'cover'},
                   'body': {'type': 'box','layout': 'vertical',
                            'contents': [{'type': 'text',
        'text': R_name,
        'weight': 'bold','size': 'xl','margin': 'none'},
       {'type': 'text', 'text': R_tag,'size': 'sm', 'margin': 'sm'},
       {'type': 'box','layout': 'baseline','margin': 'md',
        'contents': star_point},
       {'type': 'box','layout': 'vertical','margin': 'lg','spacing': 'sm','contents': [{'type': 'box','layout': 'baseline','spacing': 'sm',
          'contents': [{'type': 'text','text': 'Place','color': '#aaaaaa','size': 'sm','flex': 1},
           {'type': 'text',
            'text': R_address,
            'wrap': True,'color': '#666666','size': 'sm','flex': 5}]}]}]}}
    return Restaurant

# 餐廳回復訊息
def Get_Flex_message(station):
    try:
        cursor_food.execute(f"select res_id from Restaurants_to_Stations where station = '{station}' order by rand() limit 1")
        R1 = cursor_food.fetchone()[0]

        cursor_food.execute(f"SELECT restaurant, res_rank, res_loc, res_tag FROM Restaurants where res_id = {R1}")
        R1_info = cursor_food.fetchone()

        cursor_food.execute(f'SELECT rpic_url FROM Restaurant_pics where res_id = {R1}')
        R_image = [cursor_food.fetchone()[0]]

        R_name = [R1_info[0]]
        R_tag = [R1_info[3]]
        point = [R1_info[1]]
        R_address = [R1_info[2]]

        cursor_food.execute(f"SELECT cf_res_id FROM cf_recommend where res_id = {R1}")
        try:
            cf_recommend_1 = cursor_food.fetchone()[0]
            try:
                cf_recommend_2 = cursor_food.fetchone()[0]
                k = (cf_recommend_1, cf_recommend_2)
            except:
                k = cf_recommend_1
        except:
            pass

        try:
            for i in k:
                cursor_food.execute(f"SELECT restaurant, res_rank, res_loc, res_tag FROM Restaurants where res_id = {i}")
                R_info = cursor_food.fetchone()
                cursor_food.execute(f'SELECT rpic_url FROM Restaurant_pics where res_id = {i}')
                R_image.append(cursor_food.fetchone()[0])
                R_name.append(R_info[0])
                R_tag.append(R_info[3])
                point.append(R_info[1])
                R_address.append(R_info[2])
        except:
            pass
        # Flex_dict
        Flex_message = {'type': 'carousel', 'contents': []}
        for i in range(len(R_name)):
            Flex_message['contents'].append(Create_Res_bubble(R_image[i],R_name[i],R_tag[i],star_point(point[i]),R_address[i]))
    except:
        Flex_message = '附近沒有必吃😢'
    return Flex_message

# 捷運選線功能
def Select_one_line(s_line, user_ID):

    user_X, user_Y = get_user_point(user_ID)
    # SQL 抓出對應風格的景點 計算排序
    Att_order = get_Attractions_order(user_ID, user_X, user_Y)

    message = []
    cursor_select.execute(f'SELECT station FROM MRT_line where line="{s_line}"')
    All_station = [x[0] for x in cursor_select.fetchall()]

    place_id = []
    St = []
    for i in Att_order:
        cursor_select.execute(f"SELECT station FROM Attractions_to_stations where place_id = {i[0]}")
        place_station = cursor_select.fetchall()
        for j in place_station:
            if j[0] in All_station:
                if i[0] not in place_id or j[0] not in St:
                    place_id.append(i[0])
                    St.append(j[0])
                    break
                else:
                    continue
        if len(place_id)==2:
            break

    for i in range(2):
        # "假設"使用者選擇 中和新蘆線 計算出最相近景點 <79:空軍三重一村>
        sql="select ats.station, a.place, a.pic_url, l.line_id, a.web_url, a.group_id             from Attractions_to_stations ats               join Attractions a on (ats.place_id = a.place_id)               join MRT_line l on (ats.station = l.station)               where ats.place_id = {} and l.line = '{}'              order by ats.place_id".format(place_id[i], s_line)
        cursor_select.execute(sql)
        data = cursor_select.fetchall()

        for d in data:
            if d[0] == place_id[i]:
                break

        sql2 = "select ats.station, a.place, a.pic_url, l.line_id, a.web_url, a.group_id                  from MRT_line l                   join Attractions_to_stations ats on (ats.station = l.station)                   join Attractions a on (ats.place_id = a.place_id)                   where line_id = {} and line = '{}'"

        # 尾站id
        if d[3] in (23,37,49,54,63,67,83,107,135):
            cursor_select.execute(sql2.format(d[3]-1, s_line))
        else:
            cursor_select.execute(sql2.format(d[3]+1, s_line))
        try:
            next_place = choice(cursor_select.fetchall()) # random pick one place
        except:
            cursor_select.execute(sql2.format(d[3]-2, s_line))
            next_place = choice(cursor_select.fetchall()) # random pick one place

        sql2 = "select ats.station, a.place, a.pic_url, l.line_id, a.web_url, a.group_id          from MRT_line l           join Attractions_to_stations ats on (ats.station = l.station)           join Attractions a on (ats.place_id = a.place_id)           where line_id = {} and line = '{}'"

        # 尾站id
        if d[3] in (23,37,49,54,63,67,83,107,135) or next_place[3] in (23,37,49,54,63,67,83,107,135):
            cursor_select.execute(sql2.format(next_place[3]-1, s_line))
        else:
            cursor_select.execute(sql2.format(next_place[3]+1, s_line))

        try:
            next_next_place = choice(cursor_select.fetchall())
        except:
            cursor_select.execute(sql2.format(next_place[3]-2, s_line))
            next_next_place = choice(cursor_select.fetchall())

        pic_url = [d[2],next_place[2],next_next_place[2]]
        place_name = [d[1],next_place[1],next_next_place[1]]
        station = [d[0],next_place[0],next_next_place[0]]
        Taipei_url = [d[4],next_place[4],next_next_place[4]]
        p_label = [d[5],next_place[5],next_next_place[5]]

        Flex_place = {'type': 'carousel', 'contents': []}
        for i in range(3):
            Flex_place['contents'].append(Create_place_bubble(pic_url[i],place_name[i],station[i],Taipei_url[i],p_label[i]))

        Flex_mess = FlexSendMessage('捷遊趣',Flex_place)

        message.append(Flex_mess)
    return message

# 景點風格 icon
def Get_label_icon(p_label):
     # 1登山健行 2文化古蹟 3親子共遊 4主題商圈 5戶外踏青 6宗教祈福 7藝文館所
    place_label_icon = [{"type": "icon","size": "lg",
    "url": "https://static.liontech.com.tw/ConsoleAPData/PublicationStatic/lion_tw_b2c_travel/zh-tw/theme/_ModelFile/PictureAndText/4243/dc61f24f3c90455e898980b476101cd0.png"}
     ,{"type": "text","size": "md","margin": "lg","flex": 0,"text": r' \ '.join(sample(["步道","健行","登山"], k=3))}
     ,{"type": "icon","size": "lg","url": "https://image.flaticon.com/icons/png/512/1330/1330837.png"}
     ,{"type": "text","size": "md","margin": "lg","flex": 0,"text": r' \ '.join(sample(["文化","歷史","建築"], k=3))}
     ,{"type": "icon","size": "lg","url": "https://www.twinklesplayschool.co.za/wp-content/uploads/2018/03/img-1.png"}
     ,{"type": "text","size": "md","margin": "lg","flex": 0,"text": r' \ '.join(sample(["遊憩","同樂","親子"], k=3))}
     ,{"type": "icon","size": "lg","url": "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/shop-icon.png"}
     ,{"type": "text","size": "md","margin": "lg","flex": 0,"text": r' \ '.join(sample(["購物","商圈","美食"], k=3))}
     ,{"type": "icon","size": "lg","url": "https://image.flaticon.com/icons/png/512/1330/1330837.png"}
     ,{"type": "text","size": "md","margin": "lg","flex": 0,"text": r' \ '.join(sample(["戶外","踏青","休閒"], k=3))}
     ,{"type": "icon","size": "lg","url": "https://cdn.iconscout.com/icon/free/png-512/surat-155248.png"}
     ,{"type": "text","size": "md","margin": "lg","flex": 0,"text": r' \ '.join(sample(["信仰","祈福","宗教"], k=3))}
     ,{"type": "icon","size": "lg","url": "https://image.flaticon.com/icons/png/512/806/806652.png"}
     ,{"type": "text","size": "md","margin": "lg","flex": 0,"text": r' \ '.join(sample(["文物","藝文","展覽"], k=3))}]
    return place_label_icon[int(p_label*2-2):int(p_label*2)]

# 景點 訊息創建
def Create_place_bubble(pic_url,place_name,station,Taipei_url,p_label):
    # small json
    ss = choice(station.split())
    bubble = {"type": "bubble","hero": {"type": "image",
        "url": pic_url,
        "size": "full","aspectRatio": "20:13","aspectMode": "cover","action": {"type": "uri",
          "uri": Taipei_url
        }},"body": {"type": "box","layout": "vertical","contents": [{"type": "text",
            "text": place_name,
            "weight": "bold","size": "xl"},{"type": "box","layout": "baseline","margin": "none",
            "contents": Get_label_icon(p_label) # 風格
          },{"type": "box","layout": "baseline","margin": "none","contents": [{"type": "icon","size": "lg",
                "url": "https://lh3.googleusercontent.com/dDbnrdTcZMmnSqQ9splj3N1krbBKVIGCe4tsGLKqtntSCfeAxze6en9yImFJlRax_ZQr",
                "margin": "none"},{"type": "text",
                "text": station,
                "size": "md","margin": "lg","flex": 0,"color": "#999999"}]},{"type": "button","action": {"type": "postback",
              "label": "美食懶人包🍝🍠🍤🍜🍛",
              "data": f'FOOD_{ss}',"displayText":f"查看 {ss} 美食懶人包"
            },"margin": "lg","height": "sm","style": "primary","position": "relative","color": "#FFC0CB"}]}}
    return bubble

# 確認捷運線 > 取得使用者資訊 > 取得行程景點資訊(景點名稱、捷運站、圖片url、附近必吃資訊) > 輸入message
def Choice_Single_Line(s_line, user_ID, event):
    try:
        if s_line == '淡水信義線':
            messageT = TextSendMessage(text='專屬於您的❤淡水信義線行程🚇')
            message1, message2 = Select_one_line(s_line, user_ID)
            line_bot_api.reply_message(event.reply_token, [messageT,message1,message2])
        elif s_line == '板南線':
            messageT = TextSendMessage(text='專屬於您的💙板南線行程🚇')
            message1, message2 = Select_one_line(s_line, user_ID)
            line_bot_api.reply_message(event.reply_token, [messageT,message1,message2])
        elif s_line == '環狀線':
            messageT = TextSendMessage(text='專屬於您的💛環狀線行程🚇')
            message1, message2 = Select_one_line(s_line, user_ID)
            line_bot_api.reply_message(event.reply_token, [messageT,message1,message2])
        elif s_line == '中和新蘆線':
            messageT = TextSendMessage(text='專屬於您的🧡中和新蘆線行程🚇')
            message1, message2 = Select_one_line(s_line, user_ID)
            line_bot_api.reply_message(event.reply_token, [messageT,message1,message2])
        elif s_line == '松山新店線':
            messageT = TextSendMessage(text='專屬於您的💚松山新店線行程🚇')
            message1, message2 = Select_one_line(s_line, user_ID)
            line_bot_api.reply_message(event.reply_token, [messageT,message1,message2])
        elif s_line == '文湖線':
            messageT = TextSendMessage(text='專屬於您的🤎文湖線行程🚇')
            message1, message2 = Select_one_line(s_line, user_ID)
            line_bot_api.reply_message(event.reply_token, [messageT,message1,message2])
        print(f'{s_line} 景點推薦成功!')
    except:
        message = TextSendMessage(text="我卡住了😢請再試一次")
        line_bot_api.reply_message(event.reply_token, message)
    return None

# 圖像辨識
def picture_predict_and_Create_Flex_message(message_id):
    file_path = f'./{message_id}.jpg'
    model = load_model(r'./model_V4.h5')
    test_image = expand_dims(img_to_array(load_img(file_path, target_size = (128, 128))) /255.0, axis = 0) #變成numpy array
    predict_lists = model.predict(test_image).tolist()
    Top2_index_list = list(map(predict_lists[0].index, nlargest(2, predict_lists[0])))
    total_text = ["旅行對您而言，就像是參與一場場的長途征討一般，每趟旅程的完成，都像是成功的佔領了屬於自己的一片土地，能讓您內心獲得滿滿的成就感，也因此您立志將全世界納入自己的旅行版圖，並樂於與朋友分享自己的光榮冒險過程。",
           "您喜歡不受拘束的自在之旅，會花很多時間細細地品味旅行地點的大小事。對您而言，旅行不一定要很豪華、很享受、去很多地方，但一定是要有深度！所以一旦發現符合您喜好的景點，通常要把您拉走會需要花點時間心力。",
           "您的個性內斂、隨和，所以通常對於旅程的安排不太會有太多意見，是很好相處的旅伴，只要規劃出來的地點，能讓您無拘無束地放鬆度假，不需要思考太多就好。對您而言，只有享受一趟悠閒的旅程，才能滿足自己內心深處對旅行的期待。",
           "您會在自己喜歡的地方悠閒的多待一段時間，盡情地享受旅行帶來的樂趣，雖然在別人看來您對於度假的要求有些過高，但這就是您對於品質的堅持！對您而言，既然都要花錢旅行，那就一定要好好享受，讓這趟旅行不虛此行才行。",
           "您喜歡在旅途中結交朋友，不論是陌生旅伴還是當地人，都會是您打開話匣子的對象，也因此常常帶給旅伴們像似陽光般的活力。您也喜歡嘗試新鮮的事物，只要有沒嘗試過的道地體驗，一定都會毫不猶豫的手刀參與！",
           "看起來無欲無求，卻有著一顆積極拓展視野的心。對您來說，旅行是一種拋開生活煩惱，並釋放心靈的方式。雖然您也會希望將旅行花費用在拓展自己的視野上，而非單純的享樂，但不同的是，比起與陌生人交流，您更重視與自己內心的對話。",
           "您擁有無比的好奇心，但通常您探索世界的步調非常獨特，因為旅行對您來說就像是一場舞蹈，尋找適合自己的旋律及節奏是很重要的。因此，你有時候喜歡自己一個人旅行，如此才能夠更好的滿足自己的獨特品味。"]
# 1	登山健行4、2	文化古蹟3、親子共遊6、4	主題商圈0、5	戶外踏青2、6	宗教祈福1、7	藝文館所5
    label_text = ""
    pic_url, place_name, web_url, p_label, station = [],[],[],[],[]
    for i in Top2_index_list:
        if i == 0:
            a = 4
        elif i == 1:
            a = 6
        elif i == 2:
            a = 5
        elif i == 3:
            a = 2
        elif i == 4:
            a = 1
        elif i == 5:
            a = 7
        elif i == 6:
            a = 3

        if not label_text:
            label_text = total_text[a-1]

        cursor_picture.execute("select place_id from Attractions where group_id = {} order by rand() limit 2".format(a))
        for k in cursor_picture.fetchall():
            cursor_picture.execute("select place, pic_url, web_url, group_id, place_id \
                           from Attractions where place_id = {}".format(k[0]))

            p = cursor_picture.fetchone()
            place_name.append(p[0])
            pic_url.append(p[1])
            web_url.append(p[2])
            p_label.append(p[3])
            cursor_picture.execute('select station from Attractions_to_stations where place_id={}'.format(p[4]))
            s = ''
            for j in cursor_picture.fetchall():
                s = s + j[0] + ' '
            station.append(s)

    Flex_place = {'type': 'carousel', 'contents': []}
    for i in range(len(place_name)):
        Flex_place['contents'].append(Create_place_bubble(pic_url[i],place_name[i],station[i],web_url[i],p_label[i]))

    Flex_mess = FlexSendMessage('捷遊趣',Flex_place)
    return Flex_mess, label_text


def Delete(message_id):
    file_path = f'./{message_id}.jpg'
    try:
        OSremove(file_path)
    except OSError as e:
        print(e)
    else:
        print("File is deleted successfully")
    return None

db = pymysql.connect(host='group2mysql.*********.rds.amazonaws.com',
                     user='group2',
                     passwd='*********',
                     db='group2_mysql', port=3306, charset='utf8')
cursor = db.cursor()
cursor_follow = db.cursor()
cursor_unfollow = db.cursor()
cursor_restart = db.cursor()
cursor_recom = db.cursor()
cursor_select = db.cursor()
cursor_food = db.cursor()
cursor_user = db.cursor()
cursor_picture = db.cursor()

    # 冷啟動用
test_dict = {'士林官邸':5,
            '信義商圈':4,
            '天母夢想公園':3,
            '華山文創':7,
            '城隍廟':6,
            '虎山溪步道':1,
            '迪化街':2,
            '大湖公園':5}



# create flask server
app = Flask(__name__,
           static_url_path=r'/tmp/',
           static_folder=r'tmp/')

# YOUR_CHANNEL_ACCESS_TOKEN
line_bot_api = LineBotApi('*********')

# YOUR_CHANNEL_SECRET
handler = WebhookHandler('*********')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# 定義加入好友事件 儲存 user_id, user_name, user_status > 回復測驗開始按鈕訊息
@handler.add(FollowEvent)
def handle_follow(event):
    userID = event.source.user_id
    profile = line_bot_api.get_profile(userID)
    user_name = profile.display_name

    sql_str = 'insert into user_table(user_id, user_name, user_status) value ("{}", "{}", 0)'.format(userID, user_name)
    cursor_follow.execute(sql_str)
    db.commit()

    # TemplateSendMessage - ButtonsTemplate 按鈕訊息
    message = TemplateSendMessage(
        alt_text='測驗開始',
        template=ButtonsTemplate(
            text='隨著北捷走透透(ʕ•ᴥ•ʔ)💙',
            actions=[
                MessageTemplateAction(
                    label='♡測驗開始♡',
                    text='雙北同玩捷🚃出遊趣'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

# 定義封鎖 刪除好友事件 使用 user_id刪除使用者資料
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    userID = event.source.user_id
    cursor_unfollow.execute(f"Delete from user_table where user_id = '{userID}'")
    db.commit()

@handler.add(PostbackEvent)
def handle_postback(event):

    user_ID = event.source.user_id
    if 'FOOD' in event.postback.data:
        station = event.postback.data.replace('FOOD_','')
        Flex_message = Get_Flex_message(station)
        if Flex_message == '附近沒有必吃😢':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Flex_message))
        else:
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('Food',Flex_message))

    else:
        s_line = event.postback.data
        Choice_Single_Line(s_line, user_ID, event)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 確認使用者資訊(已啟動,未啟動)
    user_ID = event.source.user_id
    resp_text = event.message.text
    user_status = check_status(user_ID)

    # 未完成冷啟動 > 觸發冷啟動
    if not user_status:
        cold_start(user_ID, resp_text, event)

    # 已完成冷啟動 > 觸發其他功能
    else:
        # 一鍵推薦
        if resp_text == '線在玩什麼🚇':
            user_X, user_Y = get_user_point(user_ID)
            # SQL 抓出對應風格的景點 計算排序
            Att_order = get_Attractions_order(user_ID, user_X, user_Y)
            place_1 = choice(Att_order[:20])
            p2 = []
            for i in range(1,len(Att_order)):
                if Att_order[i][1][1] != place_1[1]:
                    p2.append(Att_order[i])
                    if len(p2)==20:
                        place_2 = choice(p2)
                        break
            pic_url, place_name, station, Taipei_url, p_label = Get_place_info_W2V(place_1)
            # Flex_dict
            Flex_place1 = {'type': 'carousel', 'contents': []}
            for i in range(4):
                Flex_place1['contents'].append(Create_place_bubble(pic_url[i],place_name[i],station[i],Taipei_url[i],p_label[i]))
            messageT1 = TextSendMessage(text='專屬於您的景點系列1️⃣')
            messageF1 = FlexSendMessage('專屬出遊趣',Flex_place1)

            pic_url, place_name, station, Taipei_url, p_label = Get_place_info_W2V(place_2)
            # Flex_dict
            Flex_place2 = {'type': 'carousel', 'contents': []}
            for i in range(4):
                Flex_place2['contents'].append(Create_place_bubble(pic_url[i],place_name[i],station[i],Taipei_url[i],p_label[i]))
            messageT2 = TextSendMessage(text='專屬於您的景點系列2️⃣')
            messageF2 = FlexSendMessage('專屬出遊趣',Flex_place2)
            try:
                line_bot_api.reply_message(event.reply_token,[messageT1,messageF1,messageT2,messageF2])
            except:
                message = TextSendMessage(text="我卡住了😢請再試一次")
                line_bot_api.reply_message(event.reply_token, message)

        # 捷運選線
        elif resp_text == '指想線給您🌸':
            message = Get_MRT_quick_button()
            line_bot_api.reply_message(event.reply_token, message)

        # 重新測驗
        elif resp_text == '重新再出發🚃':
            cursor_restart.execute(f'update group2_mysql.user_table set user_status=0 where user_id = "{user_ID}"')
            db.commit()
            cold_start(user_ID, resp_text, event)

        elif resp_text == '看圖說故事📸':
            message = TextSendMessage(text='直接上傳照片就可以囉📸')
            line_bot_api.reply_message(event.reply_token, message)

        elif resp_text == '查看使用說明':
            message1 = TextSendMessage(text='線在玩什麼🚇 : 直接推薦專屬捷運周邊景點🚇')
            message2 = TextSendMessage(text='指想線給您🌸 : 選擇一條捷運線，推薦專屬捷運周邊景點🌸')
            message3 = TextSendMessage(text="重新再出發🚃 : 想換換旅遊風格嗎?點我就對了🚃")
            message4 = TextSendMessage(text='看圖說故事📸 : 上傳一張景點照片，推薦您相似的捷運周邊景點📸還有個人心理測驗😚')
            line_bot_api.reply_message(event.reply_token, [message1,message2,message3,message4])

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    message_id = event.message.id
    file_path = f'./{message_id}.jpg'
    message_content = line_bot_api.get_message_content(event.message.id)
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
           fd.write(chunk)
    try:
        Flex_message, label_text = picture_predict_and_Create_Flex_message(message_id)
        messageT = TextSendMessage(text=label_text)
        line_bot_api.reply_message(event.reply_token, [Flex_message,messageT])
    except Exception as e:
        try:
            messageT = TextSendMessage(text=str(e))
            line_bot_api.reply_message(event.reply_token, messageT)
        except:
            messageT = TextSendMessage(text="我卡住了 請再試一次")
            line_bot_api.reply_message(event.reply_token, messageT)
    finally:
        Delete(message_id)

if __name__ == "__main__":
    app.run()
