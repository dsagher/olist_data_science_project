import streamlit as st
from data import load_raw_data, load_processed_data, impute_delivery_dates, map_states_to_regions, convert_to_datetime, get_sales_by_region, get_sales_over_time
from charts import product_categories_by_sales, percentage_of_sales_by_product_category, sales_vs_arpu_by_product_category_and_region, sales_over_time_chart
st.set_page_config(layout="wide")
st.title("Olist Sales Analysis")

st.write("This is a web application that allows you to analyze the sales data of Olist.")

df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_product_category, df_customer = load_raw_data()
df_order = convert_to_datetime(df_order)
df_order = impute_delivery_dates(df_order)
df_customer = map_states_to_regions(df_customer)
df_geo = map_states_to_regions(df_geo)

sales_by_region = get_sales_by_region(df_customer, df_order, df_geo, df_order_item, df_product)
sales_over_time = get_sales_over_time(df_order)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.title("Sales by Region")
        st.altair_chart(sales_vs_arpu_by_product_category_and_region(sales_by_region))
    with col2:

        st.title("Sales over Time")
        st.altair_chart(sales_over_time_chart(sales_over_time))
top_categories = product_categories_by_sales(df_order_item, df_product)
percentage_of_sales_by_product_category = percentage_of_sales_by_product_category(df_order_item, df_product)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.title("Top Categories")
        st.altair_chart(top_categories)
    with col2:
        st.title("Percentage of Sales by Product Category")
        st.altair_chart(percentage_of_sales_by_product_category)
