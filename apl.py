import requests
import pandas as pd 
import streamlit as st 
import json
import requests
from collections import Counter
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib

from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("TOKEN")

url = "https://qiita.com/api/v2/items"
headers = {
    "Authorization":f"Bearer {token}"
}

def get_data(url,headers,count,title=None,tag=None):
    if title:
        params = {
        "page":1,
        "per_page":count,
        "query":f"title:{title}"
        }
    elif tag:
        params = {
        "page":1,
        "per_page":count,
        "query":f"tag:{tag}"
        }   
    elif title and tag:
        params = {
        "page":1,
        "per_page":count,
        "query":f"tag:{tag} title:{title}"
        }   
    res = requests.get(url, params=params,headers=headers)
    data = res.json()
    return data


def get_df(data):
    dicts = {}
    title = []
    lists1 = []
    lists2 = []
    lists3 = []
    lists4 = []
    c = []
    url = []
    taglist = []
    for item in data:
        title.append(item["title"])
        lists1.append(item["created_at"].split("T")[0])
        lists2.append(item["created_at"].split("T")[1].split("+")[0])
        lists3.append(item["stocks_count"])
        lists4.append(item["likes_count"])
        c.append(item["comments_count"])
        url.append(item["url"])
        tags = item["tags"]
        t = []
        for tag in tags:
            t.append(tag["name"])
        taglist.append(t)
    dicts["記事タイトル"] = title
    dicts["記事投稿日"] = lists1
    dicts["記事投稿時間"] = lists2
    dicts["ストックされた回数"] = lists3
    dicts["いいね数"] = lists4
    dicts["コメント数"] = c
    dicts["タグ"] = taglist
    dicts["url"] = url
    df = pd.DataFrame(dicts)
    return df

def title_day(df):
    group = df.groupby("記事投稿日")[["記事タイトル"]].count()
    fig,ax = plt.subplots(figsize=(15,8))
    lists = []
    for i in group.values.tolist():
        lists.append(i[0])
    sns.barplot(
        x = group.index,
        y = lists,
        ax = ax
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=60,fontsize=14)
    return st.pyplot(fig)

def count_tag(df):
    lists = []
    for tag in df["タグ"]:
        for word in tag:
            lists.append(word)
    a = dict(Counter(lists))
    dicts = {}
    total = 0
    for k,v in zip(a.keys(),a.values()):
        if v > 1:
            dicts[f"{k}"] = v
        else:
            total += 1
    dicts["その他"] = total
    fig,ax = plt.subplots(figsize=(15,8))
    sns.barplot(
        x = dicts.keys(),
        y = dicts.values(),
        ax = ax
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=60,fontsize=14)
    return st.pyplot(fig)

def good_count(df):
    good = df.loc[df["いいね数"] > 0].sort_values("いいね数",ascending = False)
    fig,ax = plt.subplots(figsize=(15,8))
    sns.barplot(
        x = "記事タイトル",
        y = "いいね数",
        data = good,
        ax = ax
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90,fontsize=14)
    return st.pyplot(fig)

def stock_count(df):
    stock = df.loc[df["ストックされた回数"]>0].sort_values("ストックされた回数",ascending=False)
    fig,ax = plt.subplots(figsize=(15,8))
    sns.barplot(
        x = "記事タイトル",
        y = "ストックされた回数",
        data = stock,
        ax = ax
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90,fontsize=14)
    return st.pyplot(fig)


st.markdown(
    """
    <style>
    .title {
        font-family: 'Century'; /* 変更したいフォントファミリー */
        font-size: 38px; /* フォントサイズを指定 */
        color: #006400; /* フォントカラーを指定 */
        text-align:center;
    }
    .semi-title{
        font-family: 'Century'; /* 変更したいフォントファミリー */
        font-size: 18px; /* フォントサイズを指定 */
        color: #006400; /* フォントカラーを指定 */
        text-align:center;
        font-weight:100;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("検索エンジン")
with st.sidebar.form("search_form"):
    title = st.text_input("タイトルで検索する",placeholder = "pythonの実装方法")
    tag = st.text_input("タグで検索する",placeholder = "Python")
    count = st.text_input("記事の数",placeholder = "10")
    button = st.form_submit_button("検索")
    if button:
        if not title and not tag:
            st.error("タイトルまたはタグを入力してください")
        elif not count:
            st.error("表示する記事の数を入力してください")
        elif count:
            try:
                count = int(count)
            except ValueError:
                st.error("「記事の数」には整数を入力してください")
if not title and not tag:
    img = Image.open("./image/Qiita_Logo.svg.png")
    img_resize = img.resize((700,150))
    st.image(img_resize)
    st.markdown('<h1 class="title">Qiita記事検索アプリ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="semi-title">このアプリでは、Qiitaの記事を効率的に検索できます。タグやタイトルを入力することで、関連する記事を瞬時に見つけ出し、グラフで視覚的に分析できます。また、検索結果をCSVファイル形式でダウンロードすることで、データの整理や分析をさらに便利に行えます</p>',unsafe_allow_html=True)
if title and count:
    data = get_data(url=url,headers=headers,count=count,title=title)
    if data:
        st.header("検索結果")
        tab1, tab2 = st.tabs(["表", "グラフ"])
        with tab1:
            df = get_df(data)
            st.write(df)
        with tab2:
            selectbox = st.selectbox(label="グラフを選択してください",options=["日にち別投稿記事数","使用されたタグ数","記事のいいね順","ストックされた順"])
            if selectbox == "日にち別投稿記事数":
                title_day(df)
            elif selectbox == "使用されたタグ数":
                count_tag(df)
            elif selectbox == "記事のいいね順":
                good_count(df)
            elif selectbox == "ストックされた順":
                stock_count(df)
    else:
        st.error("検索条件に該当する記事がありません。")
elif tag and count:
    data = get_data(url=url,headers=headers,count=count,tag=tag)
    if data:
        st.header("検索結果")
        tab1, tab2 = st.tabs(["表", "グラフ"])
        with tab1:
            df = get_df(data)
            st.write(df)
        with tab2:
            selectbox = st.selectbox(label="グラフを選択してください",options=["日にち別投稿記事数","使用されたタグ数","記事のいいね順","ストックされた順"])
            if selectbox == "日にち別投稿記事数":
                title_day(df)
            elif selectbox == "使用されたタグ数":
                count_tag(df)
            elif selectbox == "記事のいいね順":
                good_count(df)
            elif selectbox == "ストックされた順":
                stock_count(df)
    else:
        st.error("検索条件に該当する記事がありません。")
elif title and tag and count:
    data = get_data(url=url,headers=headers,count=count,title=title,tag=tag)
    if data:
        st.header("検索結果")
        tab1, tab2 = st.tabs(["表", "グラフ"])
        with tab1:
            df = get_df(data)
            st.write(df)
        with tab2:
            selectbox = st.selectbox(label="グラフを選択してください",options=["日にち別投稿記事数","使用されたタグ数","記事のいいね順","ストックされた順"])
            if selectbox == "日にち別投稿記事数":
                title_day(df)
            elif selectbox == "使用されたタグ数":
                count_tag(df)
            elif selectbox == "記事のいいね順":
                good_count(df)
            elif selectbox == "ストックされた順":
                stock_count(df)
    else:
        st.error("検索条件に該当する記事がありません。")
