import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load the data
df = pd.read_csv('EstateSolarWeather.csv')

# Data processing
df.drop(columns=['Unnamed: 0.1', 'Unnamed: 0'], inplace=True)

# Initialize the Status column based on the new conditions
df['Status'] = df.apply(
    lambda row: (
        'Underperforming' if row['PR %'] < 80 else 
        'Anomaly Reading' if row['Energy kWh'] > row['Expected Value kWh'] else
        'Normal'
    ),
    axis=1
)

# Streamlit app layout
st.title("Solar Weather Data Analysis")

# Date input from user
start_date = st.date_input("Start Date", value=pd.to_datetime(df['Date']).min())
end_date = st.date_input("End Date", value=pd.to_datetime(df['Date']).max())

# Filter data based on user input
filtered_df = df[(pd.to_datetime(df['Date']) >= start_date) & (pd.to_datetime(df['Date']) <= end_date)]

# Button to trigger the analysis
if st.button('Enter'):
    # Group the DataFrame by 'Status' and count the size of each group
    status_counts = filtered_df.groupby('Status').size().reset_index(name='counts')
    
    # Create the horizontal bar plot using Plotly
    fig_bar = px.bar(status_counts, x='counts', y='Status', orientation='h', 
                     color='Status', text='counts', color_discrete_sequence=px.colors.qualitative.Dark2)
    
    # Update the layout to show the legend and hide the top and right spines (axes)
    fig_bar.update_layout(
        showlegend=True,
        xaxis=dict(showline=True, showgrid=False, showticklabels=True, zeroline=False),
        yaxis=dict(showline=True, showgrid=False, showticklabels=True, zeroline=False),
        plot_bgcolor='white'
    )
    
    # Update the trace to format the text position
    fig_bar.update_traces(textposition='auto')
    
    # Display the bar plot
    st.plotly_chart(fig_bar)
    
    # Create the line chart
    fig_line = go.Figure()
    
    for status, color in zip(['Anomaly Reading', 'Normal', 'Underperforming'], ['green', 'orange', 'purple']):
        df_status = filtered_df[filtered_df['Status'] == status]
        fig_line.add_trace(go.Scatter(x=df_status['Date'], y=df_status['Energy kWh'], mode='lines+markers', name=status, line=dict(color=color)))
    
    fig_line.update_layout(
        title='Energy kWh Over Time',
        xaxis_title='Date',
        yaxis_title='Energy kWh',
        plot_bgcolor='white'
    )
    
    # Display the line chart
    st.plotly_chart(fig_line)
    
    # Display anomaly readings and underperforming rows
    st.subheader("Anomaly Readings and Underperforming Data")
    anomaly_and_underperforming = filtered_df[filtered_df['Status'].isin(['Anomaly Reading', 'Underperforming'])]
    st.dataframe(anomaly_and_underperforming)

