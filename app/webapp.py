import streamlit as st

st.set_page_config(layout="wide")
pages = {"Visualizations": [st.Page('KPI_page.py',title="KPI Visualizations"), 
                            st.Page('Correlation_page.py',title="Correlation Analysis"),
                            st.Page('Missingness_page.py', title="Missingness Analysis")],
        "Resources": [st.Page('data.py', title="Data"),
                      st.Page('charts.py', title="Charts")]}

pg = st.navigation(pages)
pg.run()

