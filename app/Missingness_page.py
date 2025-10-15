import streamlit as st
from data import load_raw_data, load_processed_data
import importlib
import charts
import views
importlib.reload(charts)
importlib.reload(views)


(df_geo_raw,
df_order_raw, 
df_order_item_raw, 
df_order_payment_raw, 
df_order_review_raw, 
df_product_raw, 
df_seller_raw, 
df_customer_raw, 
df_product_category_raw) = load_raw_data()




st.title("Missingness Analysis")

with st.container(border=True):
    st.pyplot(charts.missingness_heatmap(df_order_raw))
    st.write("#### Observation")
    st.write("Missing values cluster around 'order_delivered_customer_date' and 'order_delivered_carrier_date', with some in 'order_approved_at'")
    st.write("#### Next Steps")
    st.write("Determine possible reasons for missing values.")

with st.container(border=True):
    st.markdown("## *Determine if missing values are due to increased orders and cancellations*")
    
    # Get both charts from the function
    chart_customer, chart_carrier = charts.delivery_nulls_chart(df_order_raw)
    
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart_carrier, use_container_width=True)
    with col2:
        st.altair_chart(chart_customer, use_container_width=True)
    
    st.markdown("#### Observation")
    st.markdown("Overall orders and missing values pick up towards the end of 2017.")
    st.markdown("#### Hypothesis")
    st.markdown("This increase in orders could be due to an increase in cancellations, resulting in more missing values.")
    st.markdown("#### Next Steps")
    st.markdown("Check to see if cancellations increase around the same time to support our hypothesis.")


with st.container(border=True):
    st.altair_chart(charts.cancelled_orders_by_date_chart(df_order_raw))
    st.markdown("#### Observation")
    st.markdown("Cancellations spike towards the end of 2017 as well, supporting our claim that the increase nulls at the end of 2017/beginning of 2018 is due to \
                an increase of orders and cancellations.")

