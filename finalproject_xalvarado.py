"""
Class: CS230
Name: Xander Alvarado
Description: Final Project
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

CRIMES_CSV = "BostonCrime2021_7000_sample.csv"
DISTRICTS_CSV = "BostonPoliceDistricts.csv"
IMAGE = "boston.jpg"

# Read into files
def read_Crimes(file):
    cr_df = pd.read_csv(file)
    return cr_df


def read_Districts(file):
    dis_df = pd.read_csv(file)
    return dis_df

#Include image in application

def web_Image(file):
    st.image(IMAGE, width=700)

# Use Streamlit to create the UI
st.title('Boston Crime Incident Reports 2021 \n Xander Alvarado')

crimes_df = read_Crimes(CRIMES_CSV)
districts_df = read_Districts(DISTRICTS_CSV)
st.write(web_Image(IMAGE))

st.sidebar.header('Filters')

sorted_districts_df = districts_df.sort_values(
    by=["District Name"],
    ascending=True
)

crime = st.sidebar.multiselect(f'Please select a crime:', list(crimes_df["OFFENSE_DESCRIPTION"].unique()))
st.sidebar.write("The crimes selected can be used in a bar chart to show how many times they happened.")

hours = st.sidebar.slider(f'Please select an hour', 0, 24)

day_of_week = st.sidebar.multiselect(f'Please select the days of the week:', list(crimes_df["DAY_OF_WEEK"].unique()))
st.sidebar.write("The days selected can be used to show the percentage of crimes each day weighted against each other.")

district = st.sidebar.multiselect(f'Please select a district:', list(crimes_df["DISTRICT"].unique()))

if st.sidebar.checkbox("Click to the show the sorted districts dataframe."):
    st.write(sorted_districts_df)

# Charts
selected_day_of_week = []
selected_crime = []
crime_counts = []
day_counts = []

crime_bar_chart = crimes_df.loc[crimes_df["OFFENSE_DESCRIPTION"].isin(crime)]
district_bar_chart = crimes_df.loc[crimes_df["DISTRICT"].isin(district)]

for i in day_of_week:
    selected_day_of_week.append(day_of_week)
    day_counts.append(crimes_df["DAY_OF_WEEK"].value_counts()[i])
selected_day_of_week_str = ' '.join([i for i in day_of_week if selected_day_of_week])

selected_chart = st.sidebar.selectbox("Please select a chart:", ['', "Crime Bar Chart", "Pie Chart", "District Bar Chart"])
if selected_chart == "Crime Bar Chart":
    st.title("Count of Crimes")
    if len(crime) == 0:
        st.write("Please select at least one crime.")
    else:
        selected_color = st.sidebar.radio("Please select the color for the bar chart.", ["Red", "Orange"])
        fig, ax = plt.subplots()
        crime_bar_chart["OFFENSE_DESCRIPTION"].value_counts().plot(kind="bar")
        st.pyplot(fig)

if selected_chart == "Pie Chart":
    st.title("Percentage of Crimes Per Day")
    if len(day_of_week) <= 1:
        st.write("Please select at least two days of the week.")
    else:
        st.write('You selected: ', selected_day_of_week_str)
        fig, ax = plt.subplots()
        ax.pie(day_counts, labels=day_of_week, autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
        plt.show()

if selected_chart == "District Bar Chart":
    st.title("Count of Crimes by District")
    selected_color = st.sidebar.radio("Please select the color for the bar chart.", ["Blue", "Green"])
    fig, ax = plt.subplots()
    district_bar_chart["DISTRICT"].value_counts().plot(kind="bar")
    st.pyplot(fig)

# Map
crimes_df.rename(columns={"Lat": "lat", "Long": "long"}, inplace=True)
latlong = crimes_df.drop(
    ['OFFENSE_CODE_GROUP', 'UCR_PART', 'REPORTING_AREA', 'INCIDENT_NUMBER', 'OFFENSE_CODE', 'DISTRICT', 'SHOOTING',
     'OCCURRED_ON_DATE', 'YEAR', 'MONTH', 'DAY_OF_WEEK', 'STREET', 'Location'], inplace=False, axis=1)
latlong = latlong.loc[(latlong["lat"] > 0) & (latlong['long'] < 0)]
latlong = latlong.loc[latlong["HOUR"] == hours]
crimes_map = st.sidebar.radio("Map", ['', "Scatter"])
if crimes_map == "Scatter":
    st.title("Boston Crimes Map")
    st.write("Use the hour slider to see which hour crimes occurred.")

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=pdk.ViewState(
            latitude=latlong["lat"].mean(),
            longitude=latlong["long"].mean(),
            zoom=10,
            pitch=0),
        layers=[pdk.Layer("ScatterplotLayer",
                          data=latlong,
                          get_position='[long, lat]',
                          get_radius=75,
                          get_color=[0, 0, 255])
                ]
    )
    )
