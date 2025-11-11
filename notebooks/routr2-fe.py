import streamlit as st
import numpy as np
import pandas as pd

# map_data = pd.DataFrame(
#     np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
#     columns=['lat', 'lon'])

# st.map(map_data)



# x = st.slider('x')  # 👈 this is a widget
# st.write(x, 'squared is', x * x)



# st.text_input("Your city", key="city")

# # You can access the value at any point with:
# st.session_state.city



# if st.checkbox('Show dataframe'):
#     chart_data = pd.DataFrame(
#        np.random.randn(20, 3),
#        columns=['a', 'b', 'c'])

#     chart_data

def class_creator(location):
   return 

city, state = city_collector(st.text_input("Enter your city and state")) 
if city:
    st.write(f"Loading data for {city}, {state}!")