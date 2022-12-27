import json
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
import requests

st.set_page_config(page_title="Monitoring System", layout="wide")
st.title("Odisha Monitoring System")

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
    apik = "b568a8791832e5d958e862131d749ebf"

    baseurl = "https://api.openweathermap.org/data/2.5/weather?q="
    cityname = city_name
    if city_name in ['Boudh',"Nuapada","Nabarangpur","Keonjhar","Mayurbhanj","Kandhamal","Kalahandi"]:
        cityname = 'Cuttack'
    complete_url = baseurl + cityname + "&appid=" + apik

    result = requests.get(complete_url)
    data = result.json()

    # print(data)

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

    if winspeed>8:
        wer.append(city_name)
    if temp>30:
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
    # print(df1)


x = json.load(open("odisha_disticts.geojson","r"))
y = pd.read_csv("data.csv")

y.drop("Unnamed: 0",axis = 'columns',inplace=True)
y.drop("Headquarters",axis = 'columns',inplace=True)
y.drop("id",axis = 'columns',inplace=True)

for i in range(30):
    # print(y['District'][i])
    get_data(y['District'][i])

mid_temp /= 60

df['Temp'] = df['Temp'].apply(lambda x: x+5)
df['Temp'] = df['Temp'].apply(lambda x: x-5)

fig = px.choropleth(
    df, geojson=x,
    featureidkey="properties.NAME_2",
    locations="District",
    color="Temp",
    hover_name='District',
    hover_data= ["Temperature","Min_Temperature","Max_Temperature","Pressure","Humidity","Visiblity","WindSpeed"],
    # title = 'Odisha Monitoring System ',
    color_discrete_sequence=None,
    color_discrete_map=None,
    color_continuous_scale=px.colors.diverging.Geyser,
    range_color=(int(min(df['Temp'])),int(max(df['Temp']))),
    color_continuous_midpoint=mid_temp,
    width = 800,
    height = 700,
    labels=df['District']
)
fig.update_geos(fitbounds="locations", visible=False)
# px.scatter_geo(
#     geojson=x,
#     featureidkey="properties.NAME_2",
#     locations=df["District"],
#     text = df["District"]
#     # mode='text'
# )

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
    # st.write("Warnings about Wind Speed")
    for i in range(len(wer)):
        new_title = 'High Wind Speed at '+ wer[i]
        st.error(new_title)
    # wdf = pd.DataFrame(wer,columns=["Wind Speed Warning"])
    # st.dataframe(wdf)


with TempWarning:
    # st.write("Warnings about Temperature")
    for i in range(len(ter)):
        new_title = 'High Temperature at '+ ter[i]
        st.error(new_title)
    # tdf = pd.DataFrame(ter,columns=["Temperature Warning"])
    # st.dataframe(tdf)
