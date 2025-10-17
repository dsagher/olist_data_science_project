import streamlit as st
from pathlib import Path
import sys

st.set_page_config(layout="wide")

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.preprocessing import load_processed_data_streamlit
from app.assets import charts, aggregations, merges

# Load processed data
data = load_processed_data_streamlit()

df_geo = data['geo']
df_order = data['order']
df_order_item = data['order_item']
df_product = data['product']
df_customer = data['customer']
df_product_category = data['product_category']

# Calculate sales by region and ARPU
sales_by_region = merges.get_sales_by_region_category(data)
sales_by_region = aggregations.calculate_ARPU(sales_by_region)

#Get KPIs
total_revenue = aggregations.get_total_revenue(data)
total_orders = aggregations.get_total_orders(data)
total_customers = aggregations.get_total_customers(data)
highest_selling_city = merges.get_highest_selling_cities(data).head(1).index[0].title()
highest_selling_category = merges.get_highest_selling_categories(data).head(1).index[0].title().replace("_", " & ")

VALID_YEARS = [2016, 2017, 2018, 2019]

st.title("Olist EDA Dashboard")

with st.sidebar:
    selected_year = st.selectbox("Select Year", VALID_YEARS)

# KPI Metrics
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        with st.container(border=True):
            st.markdown(f"## **Total Revenue:** \n ### `{total_revenue}`")
    with col2:
        with st.container(border=True):
            st.markdown(f"## **Total Orders:** \n ### `{total_orders}`")
    with col3:
        with st.container(border=True):
            st.markdown(f"## **Total Customers:** \n ### `{total_customers}`")
    with col4:
        with st.container(border=True):
            st.markdown(f"## **Highest Selling City:** \n ### `{highest_selling_city}`")
    with col5:
        with st.container(border=True):
            st.markdown(f"## **Highest Selling Category:** \n ### `{highest_selling_category}`")

# Sales and ARPU by Region and Product Category
with st.container(border=True):
        st.title("Sales by Region")
        st.altair_chart(charts.get_sales_by_region_category_bubble_chart(sales_by_region))
        selected_chart = st.selectbox("Choose a chart to display", ["Above Average Sales and Below Average ARPU", "Below Average Sales and Above Average ARPU"])
        if selected_chart == "Above Average Sales and Below Average ARPU":
            merged_data = merges.get_average_sales_ARPU(sales_by_region, data, sales=True, ARPU=False)
            st.altair_chart(charts.sales_ARPU_time_chart(merged_data, year=selected_year))
        else:
            merged_data = merges.get_average_sales_ARPU(sales_by_region, data, sales=False, ARPU=True)
            st.altair_chart(charts.sales_ARPU_time_chart(merged_data, year=selected_year))


