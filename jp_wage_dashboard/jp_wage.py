from altair.vegalite.v4.schema.channels import Y
import pandas as pd
from pydeck.bindings import layer
import streamlit as st
import pydeck as pdk

import plotly.express as px

st.title('日本の賃金データのダッシュボード')

df_jp_ind = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv',encoding='shift_jis')
df_jp_cate = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv',encoding='shift_jis')
df_pref_ind = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv',encoding='shift_jis')

st.header('2019年：一人当たり平均賃金のヒートマップ')

jp_lat_lon = pd.read_csv('./pref_lat_lon.csv')
jp_lat_lon = jp_lat_lon.rename(columns={'pref_name':'都道府県名'})

df_pref_map = df_pref_ind[(df_pref_ind['年齢']== '年齢計')&(df_pref_ind['集計年']== 2019)]
df_pref_map = pd.merge(df_pref_map,jp_lat_lon, on='都道府県名')
df_pref_map['一人当たり賃金（相対値）']= ((df_pref_map['一人当たり賃金（万円）']-df_pref_map['一人当たり賃金（万円）'].min())/(df_pref_map['一人当たり賃金（万円）'].max()-df_pref_map['一人当たり賃金（万円）'].min()))
df_pref_map

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=35.689185,
        longitude=139.691648,
        zoom=10.5,
        pitch=40.5,
    ),
    layers=[
        pdk.Layer(
            'HeatmapLayer',
            data=df_pref_map,
            get_position='[lon, lat]',
            opacity=0.4,
            threshold=0.3,
            get_weight = '一人当たり賃金（相対値）'
        )
    ],
))

st.header('◆集計年別の一人当たり賃金万円の推移')

df_ts_mean = df_jp_ind[(df_jp_ind['年齢']== '年齢計')]
df_ts_mean = df_ts_mean.rename(columns={'一人当たり賃金（万円）':'全国一人当たり賃金（万円）'})

df_pref_mean = df_pref_ind[(df_pref_ind['年齢']== '年齢計')]
pref_list = df_pref_mean['都道府県名'].unique()
option_pref = st.selectbox(
    '都道府県',
    (pref_list)
)
df_pref_mean = df_pref_mean[df_pref_mean['都道府県名'] == option_pref]

df_mean_line = pd.merge(df_ts_mean, df_pref_mean, on='集計年')
df_mean_line = df_mean_line[['集計年','全国一人当たり賃金（万円）','一人当たり賃金（万円）']]
df_mean_line = df_mean_line.set_index('集計年')

st.line_chart(df_mean_line)


st.header('◆年齢階級別の全国一人当たり平均賃金（万円）')

df_mean_bb = df_jp_ind[(df_jp_ind['年齢'] != '年齢計')]

fig = px.scatter(df_mean_bb,
    x = '一人当たり賃金（万円）',
    y = '年間賞与その他特別給与額（万円）',
    range_x = [150,700],
    range_y = [0,150],
    size = '所定内給与額（万円）',
    size_max = 38,
    color='年齢',
    animation_frame='集計年',
    animation_group='年齢')

st.plotly_chart(fig)


st.header('◆産業別の賃金推移')

year_list = df_jp_cate['集計年'].unique()
option_year= st.selectbox(
    '集計年',
    (year_list)
)

w_list =['一人当たり賃金（万円）','所定内給与額（万円）','年間賞与その他特別給与額（万円）']
option_w= st.selectbox(
    '賃金の種類',
    (w_list)
)
df_mean_cate =df_jp_cate[(df_jp_cate['集計年']== option_year )]
max_x = df_mean_cate[option_w].max()+ 50

fig = px.bar(
    df_mean_cate,
    x = option_w,
    y = '産業大分類名',
    color='産業大分類名',
    animation_frame='年齢',
    range_x=[0,max_x],
    orientation='h',
    width=800,
    height=500
)

st.plotly_chart(fig)

st.text('出典:RESAS (地域経済分析システム)')
st.text('本結果はRESAS (地域経済分析システム)を加工して作成')
