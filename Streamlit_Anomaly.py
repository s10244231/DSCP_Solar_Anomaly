import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the data
df = pd.read_csv('EstateSolarWeather.csv')

# Data processing
df.drop(columns=['Unnamed: 0.1', 'Unnamed: 0'], inplace=True)

# Convert 'Date and Time' column to datetime format
df['Date and Time'] = pd.to_datetime(df['Date and Time'])

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
st.sidebar.title("Filters")
start_date = st.sidebar.date_input("Start Date", value=df['Date and Time'].min())
end_date = st.sidebar.date_input("End Date", value=df['Date and Time'].max())

# Location Code selection
location_codes = st.sidebar.multiselect("Location Code", ['Select All'] + df['Location Code'].unique().tolist(), default=['Select All'])

# If 'Select All' is chosen, select all location codes
if 'Select All' in location_codes:
    location_codes = df['Location Code'].unique()

# Convert start_date and end_date to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data based on user input
filtered_df = df[(df['Date and Time'] >= start_date) & (df['Date and Time'] <= end_date) & (df['Location Code'].isin(location_codes))]

# Button to trigger the analysis
if st.sidebar.button('Enter'):
    # Group the DataFrame by 'Status' and count the size of each group
    status_counts = filtered_df.groupby('Status').size().reset_index(name='counts')
    
    # Create the pie chart using Plotly
    fig_pie = px.pie(status_counts, values='counts', names='Status', title='Distribution of Status',
                     color_discrete_sequence=['rgb(0,128,0)', 'rgb(255,215,0)', 'rgb(220,20,60)'])
    
    # Create a column layout for the table and pie chart
    col1, col2 = st.columns([1, 1])
    
    # Display the pie chart in the first column and the table in the second column
    with col1:
        st.plotly_chart(fig_pie)
    with col2:
        st.subheader("Anomaly Readings and Underperforming Data")
        st.write(filtered_df[filtered_df['Status'].isin(['Anomaly Reading', 'Underperforming'])])
    
    # Create the line chart using Plotly
    fig_line = go.Figure()
    for status, color in zip(['Anomaly Reading', 'Normal', 'Underperforming'], ['rgb(220,20,60)', 'rgb(0,128,0)', 'rgb(255,215,0)']):
        df_status = filtered_df[filtered_df['Status'] == status]
        fig_line.add_trace(go.Scatter(x=df_status['Date and Time'], y=df_status['Energy kWh'], mode='lines+markers', name=status, line=dict(color=color)))
    
    fig_line.update_layout(
        title='Energy kWh Over Time',
        xaxis_title='Date',
        yaxis_title='Energy kWh',
        plot_bgcolor='white'
    )
    
    # Display the line chart below the pie chart and table
    st.plotly_chart(fig_line)

# Explanations
st.sidebar.markdown("""
**Underperforming** - Performance Ratio (PR%) is below 80%  
**Anomaly Reading** - Energy generated is more than expected value
""")
