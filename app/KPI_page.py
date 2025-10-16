import streamlit as st
from data import load_processed_data
import views
import charts
import importlib
importlib.reload(charts)
importlib.reload(views)

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
# sales_over_time = views.get_sales_over_time(df_order)


st.title("Olist EDA Dashboard")

# KPI Metrics
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.markdown(f"## **Total Revenue:** \n ### {views.get_total_revenue(df_order_payment)}")
    with col2:
        with st.container(border=True):
            st.markdown(f"## **Total Orders:** \n ### {views.get_total_orders(df_order)}")
    with col3:
        with st.container(border=True):
            st.markdown(f"## **Total Customers:** \n ### {views.get_total_customers(df_customer)}")
    with col4:
        with st.container(border=True):
            st.markdown(f"## **Total Products:** \n ### {views.get_total_products(df_product)}")


# Sales by Region and Top Categories
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.title("Sales by Region")
            st.altair_chart(charts.sales_vs_arpu_by_product_category_and_region(sales_by_region))
    with col2:
        with st.container(border=True):
            st.title("Top Categories")
            st.altair_chart(charts.product_categories_by_sales(df_order_item, df_product))
