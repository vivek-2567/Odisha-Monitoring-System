import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import requests

st.set_page_config(page_title="Monitoring System", layout="wide")
st.markdown("<h1 style='text-align: center; color: White;'>Odisha Monitoring System</h1>", unsafe_allow_html=True)

global df
df = pd.DataFrame(columns=['District','Temp',"Temperature","Min_Temperature","Max_Temperature","Pressure","Humidity","Visiblity","WindSpeed"])
global mid_temp
mid_temp = 0
global wer
wer=[]
global ter
ter = []
mhum = 0
mpress = 0
max_temp = 0
min_temp = 100

def get_data(city_name):
    global df
    global mid_temp
    global ter
    global wer
    global mhum
    global mpress
    global max_temp
    global min_temp
    apik = st.secrets['apik']

    baseurl = "https://api.openweathermap.org/data/2.5/weather?q="
    cityname = city_name
    if city_name in ['Boudh',"Nuapada","Nabarangpur","Keonjhar","Mayurbhanj","Kandhamal","Kalahandi"]:
        cityname = 'Cuttack'
    complete_url = baseurl + cityname + "&appid=" + apik

    result = requests.get(complete_url)
    data = result.json()

    temp = round(data['main']['temp'] - 273.15,2)
    mid_temp += temp
    if temp>max_temp:
        max_temp = temp
    if temp<min_temp:
        min_temp = temp
    temp_min = round(data['main']['temp_min'] - 273.15,2)
    temp_max = round(data['main']['temp_max'] - 273.15,2)
    pres = data['main']['pressure']
    if pres>mpress:
        mpress = pres
    hum = data['main']['humidity']
    if hum>mhum:
        mhum = hum
    vis = data['visibility']/1000
    winspeed = data['wind']['speed'] * 3.6

    if winspeed>10:
        wer.append(city_name)
    if temp>35:
        ter.append(city_name)

    df1 = pd.DataFrame({
        "District" : [city_name],
        "Temp" : [float(temp)],
        "Temperature" : [str(temp) + chr(176)+"C"],
        "Min_Temperature" : [str(temp_min) + chr(176)+"C"],
        "Max_Temperature" : [str(temp_max) + chr(176)+"C"],
        "Pressure"  :[str(pres) + 'hPa'],
        "Humidity":[str(hum) + "%"],
        "Visiblity":[str(vis) + "km"],
        "WindSpeed":[str(round(winspeed,2)) + "km/hr"]
    })
    
    df = pd.concat([df,df1])


x = json.load(open("odisha_disticts.geojson","r"))
y = pd.read_csv("data.csv")

y.drop("Unnamed: 0",axis = 'columns',inplace=True)
y.drop("Headquarters",axis = 'columns',inplace=True)
y.drop("id",axis = 'columns',inplace=True)

for i in range(30):
    get_data(y['District'][i])

mid_temp /= 60

df['Temp'] = df['Temp'].apply(lambda x: x+5)
df['Temp'] = df['Temp'].apply(lambda x: x-5)

fig = go.Figure(data=go.Choropleth(
    geojson=x,
    featureidkey='properties.NAME_2',
    locations=df['District'],
    z=df['Temp'],
    customdata= df[["District","Temperature","Min_Temperature","Max_Temperature","Pressure","Humidity","Visiblity","WindSpeed"]],
    marker_line_color='black',
    marker_opacity = 1,
    marker_line_width = 1,
    colorscale = 'Geyser',
    hovertemplate =
    "<b>%{customdata[0]}</b><br><br>"+
    "Temperature: %{customdata[1]}<br>"+
    "Min_Temperature: %{customdata[2]}<br>"+
    "Max_Temperature: %{customdata[3]}<br>"+
    "Pressure: %{customdata[4]}<br>"+
    "Humidity: %{customdata[5]}<br>"+
    "Visiblity: %{customdata[6]}<br>"+
    "Wind Speed: %{customdata[7]}<br>"+
    "<extra></extra>"
))

fig.update_geos(visible=False,fitbounds='locations')

fig.add_trace(go.Scattergeo(
    lon=y['lon_c'],
    lat=y['lat_c'],
    mode='text',
    textposition='top center',
    text=[str(x) for x in df["District"]],
    textfont={'color': 'Black'},
    hoverinfo='skip',
))
fig.update_layout(
    font = dict(
        size = 12
    ),
    margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
    height=680,
    width=800
)


chart,metrix = st.columns([3,1])

with chart:
    st.plotly_chart(fig,use_container_width=True)

with metrix:
    st.markdown("")
    st.markdown("")
    st.metric(label = "Max Temperature",value = str(max_temp) +" "+chr(176)+"C")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.metric(label = "Max Pressure",value = str(mpress) + " hPa")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.metric(label = "Max Humidity",value = str(mhum) + " %")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.metric(label = "Min Temperature",value = str(min_temp) +" "+chr(176)+"C")

WindWarning,TempWarning = st.columns(2)

with WindWarning:
    st.write("Warnings about Wind Speed>10")
    wdf = pd.DataFrame(wer,columns=["Wind Speed Warning"])
    st.table(wdf)


with TempWarning:
    st.write("Warnings about Temperature>35")
    tdf = pd.DataFrame(ter,columns=["Temperature Warning"])
    st.dataframe(tdf)
