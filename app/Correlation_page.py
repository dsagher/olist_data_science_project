import streamlit as st
import data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import charts
import logging
import importlib
importlib.reload(data)
logging.basicConfig(level=logging.DEBUG)


st.title("Correlation Analysis")

(df_geo, df_order, df_order_item, df_order_payment, 
 df_order_review, df_product, df_seller, df_customer, 
 df_product_category) = data.load_processed_data()

# Merge key metrics
analysis_df = data.order_merge(df_order, df_order_item, df_order_payment, df_order_review)

st.pyplot(charts.orders_correlation_heatmap(analysis_df))

st.markdown("""
## Observations:
- **Delivery time is negatively correlated with review score**
- **Freight value is positively correlated with payment value and price**   
- **Payment installments is positively correlated with payment value and price**
""")

st.markdown("""
## Next Steps:
- **Analyze the relationship between delivery time and review score**
- **Analyze the relationship between freight value and payment value and price**
- **Analyze the relationship between payment installments and payment value and price**
""")