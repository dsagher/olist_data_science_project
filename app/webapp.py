import streamlit as st
from pathlib import Path
import sys

st.set_page_config(layout="wide")

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.assets.preprocessing import load_processed_data
from app.assets import views, charts

(df_geo, 
df_order, 
df_order_item, 
df_order_payment, 
df_order_review, 
df_product, 
df_seller, 
df_customer, 
df_product_category) = load_processed_data()

sales_by_region = views.get_sales_by_region(df_customer, df_order, df_geo, df_order_item, df_product)


st.title("Olist EDA Dashboard")

# KPI Metrics
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        with st.container(border=True):
            st.markdown(f"## **Total Revenue:** \n ### {views.get_total_revenue(df_order_item)}")
    with col2:
        with st.container(border=True):
            st.markdown(f"## **Total Orders:** \n ### {views.get_total_orders(df_order)}")
    with col3:
        with st.container(border=True):
            st.markdown(f"## **Total Customers:** \n ### {views.get_total_customers(df_customer)}")
    with col4:
        with st.container(border=True):
            st.markdown(f"## **Highest Selling City:** \n ### {views.get_highest_selling_city(df_order, df_order_item, df_customer, df_geo)}")
    with col5:
        with st.container(border=True):
            st.markdown(f"## **Highest Selling Category:** \n ### {views.get_highest_selling_category(df_order_item, df_product)}")

# Sales by Region and Top Categories
with st.container(border=True):
        st.title("Sales by Region")
        st.altair_chart(charts.sales_vs_arpu_by_product_category_and_region(sales_by_region))
        selected_chart = st.selectbox("Choose a chart to display", ["Above Average Sales and Below Average ARPU", "Below Average Sales and Above Average ARPU"])
        if selected_chart == "Above Average Sales and Below Average ARPU":
            st.altair_chart(charts.above_average_sales_and_below_average_arpu_chart(sales_by_region, df_order, df_order_item, df_product))
        else:
            st.altair_chart(charts.below_average_sales_and_above_average_arpu_chart(sales_by_region, df_order, df_order_item, df_product))


