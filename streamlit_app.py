import streamlit as st
import pandas as pd
import numpy as np
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#テキスト表示
st.title("Youtubeチャンネル分析")
st.write("データをアップロードして気になるチャンネルを分析してみましょう")

#データをアップロード
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    #アップロードしたCSVをデータフレームにする
    video_data = pd.read_csv(uploaded_file,encoding="Shift-JIS")
    video_data['Post_Date'] = pd.to_datetime(video_data['Post_Date']).dt.date
    video_data['month'] = pd.to_datetime(video_data['Post_Date']).dt.to_period('M').dt.start_time

    #サイドメニュー＆フィルターの設定
    st.sidebar.write('フィルター設定')
    date_start = st.sidebar.date_input('開始日',value=video_data['Post_Date'].min(), min_value=video_data['Post_Date'].min())
    date_end = st.sidebar.date_input('終了日')
    view_min = st.sidebar.number_input('再生数下限',step=10000)
    like_min = 0

    #設定に合わせてデータをフィルター
    data = video_data.query('@date_end >= Post_Date >= @date_start & Views > @view_min & Likes > @like_min')

    #基本データの表示
    st.subheader('動画の再生数')
    col1, col2, col3 = st.columns(3)
    col1.metric("最大", data['Views'].max())
    col2.metric("最小", data['Views'].min())
    col3.metric("平均", data['Views'].mean())

    #月別のグラフの表示
    st.subheader('月別の再生数')
    chart_data = data[['Post_Date', 'month', 'Video_Title','Views','Likes','Comments']]
    st.bar_chart(chart_data, x="month", y=['Views','Likes'])

    #テキスト分析（ワードクラウド作成の準備）
    title_text = ''.join(data['Video_Title'])

    docs=[]
    t = Tokenizer()
    tokens = t.tokenize(title_text)
    for token in tokens:
        if len(token.base_form) > 2:
            docs.append(token.surface)
    
    #ワードクラウドの表示
    c_word = ' '.join(docs)
    wordcloud = WordCloud(background_color='white',
                        font_path='Corporate-Logo-Rounded-Bold-ver3.otf',
                        width=800, height=400).generate(c_word)

    fig = plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud)
    plt.axis('off')

    st.pyplot(fig)

    #一覧の表示
    st.subheader('動画別のデータ')
    st.dataframe(data[['thumbnails','Video_Title','Views','Likes','Comments']],
        column_config={
            'thumbnails':st.column_config.ImageColumn('thumbnails'),
            'Video_Title':'title',
            'Views':'views',
            'Likes':'likes',
            'Comments':'comments'
        }
    )
