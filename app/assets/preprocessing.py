import pandas as pd
from scipy.stats import lognorm
import numpy as np
import datetime as dt
from pathlib import Path
import streamlit as st
from sklearn.preprocessing import KBinsDiscretizer

# Get the project root directory
# preprocessing.py -> assets/ -> app/ -> project_root/
PROJECT_ROOT = Path(__file__).parent.parent.parent
print(f"📁 Project root: {PROJECT_ROOT}")
DATA_RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
print(f"📁 Data directories:")
print(f"   Raw: {DATA_RAW_DIR}")
print(f"   Processed: {DATA_PROCESSED_DIR}")



state_to_region = {
'SP': 'Southeast',
'MG': 'Southeast',
'RJ': 'Southeast',
'ES': 'Southeast',
'PR': 'South',
'SC': 'South',
'RS': 'South',
'DF': 'Central-West',
'GO': 'Central-West',
'MS': 'Central-West',
'MT': 'Central-West',
'BA': 'Northeast',
'SE': 'Northeast',
'AL': 'Northeast',
'PE': 'Northeast',
'PB': 'Northeast',
'RN': 'Northeast',
'CE': 'Northeast',
'PI': 'Northeast',
'MA': 'Northeast',
'PA': 'North',
'AM': 'North',
'AP': 'North',
'RO': 'North',
'AC': 'North',
'RR': 'North',
'TO': 'North'
}

@st.cache_data
def load_raw_data():
    df_geo = pd.read_csv(DATA_RAW_DIR / 'olist_geolocation_dataset.csv')
    df_order = pd.read_csv(DATA_RAW_DIR / 'olist_orders_dataset.csv')
    df_order_item = pd.read_csv(DATA_RAW_DIR / 'olist_order_items_dataset.csv')
    df_order_payment = pd.read_csv(DATA_RAW_DIR / 'olist_order_payments_dataset.csv')
    df_order_review = pd.read_csv(DATA_RAW_DIR / 'olist_order_reviews_dataset.csv')
    df_product = pd.read_csv(DATA_RAW_DIR / 'olist_products_dataset.csv')
    df_seller = pd.read_csv(DATA_RAW_DIR / 'olist_sellers_dataset.csv')
    df_customer = pd.read_csv(DATA_RAW_DIR / 'olist_customers_dataset.csv')
    df_product_category = pd.read_csv(DATA_RAW_DIR / 'product_category_name_translation.csv')

    return df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_customer, df_product_category

@st.cache_data
def load_processed_data():
    df_order = pd.read_csv(DATA_PROCESSED_DIR / 'orders.csv')
    df_customer = pd.read_csv(DATA_PROCESSED_DIR / 'customers.csv')
    df_geo = pd.read_csv(DATA_PROCESSED_DIR / 'geolocation.csv')
    df_order_item = pd.read_csv(DATA_PROCESSED_DIR / 'order_items.csv')
    df_order_payment = pd.read_csv(DATA_PROCESSED_DIR / 'order_payments.csv')
    df_order_review = pd.read_csv(DATA_PROCESSED_DIR / 'order_reviews.csv')
    df_product = pd.read_csv(DATA_PROCESSED_DIR / 'products.csv')
    df_seller = pd.read_csv(DATA_PROCESSED_DIR / 'sellers.csv')
    df_product_category = pd.read_csv(DATA_PROCESSED_DIR / 'product_category.csv')

    return df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_customer, df_product_category

def convert_to_datetime(df_order: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the timestamp columns to datetime
    """
    df_order = df_order.copy()
    df_order['order_purchase_timestamp'] = pd.to_datetime(df_order['order_purchase_timestamp'])
    df_order['order_approved_at'] = pd.to_datetime(df_order['order_approved_at'])
    df_order['order_delivered_customer_date'] = pd.to_datetime(df_order['order_delivered_customer_date'])
    df_order['order_delivered_carrier_date'] = pd.to_datetime(df_order['order_delivered_carrier_date'])
    return df_order

def add_date_features(df_order: pd.DataFrame) -> pd.DataFrame:
    """
    Add the date features
    """

    df_order = df_order.copy()
    df_order['order_purchase_month'] = df_order['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()
    df_order['order_purchase_year'] = df_order['order_purchase_timestamp'].dt.year
    df_order['order_purchase_quarter'] = df_order['order_purchase_timestamp'].dt.quarter
    df_order['order_purchase_day'] = df_order['order_purchase_timestamp'].dt.day
    df_order['order_purchase_dayofweek'] = df_order['order_purchase_timestamp'].dt.dayofweek
    df_order['order_purchase_dayofyear'] = df_order['order_purchase_timestamp'].dt.dayofyear
    df_order['order_purchase_weekday'] = df_order['order_purchase_timestamp'].dt.weekday
    return df_order

def impute_delivery_dates(df_order: pd.DataFrame) -> pd.DataFrame:
    """
    Impute the delivery dates
    """
    df_order = df_order.copy()
    customer_missing_mask = df_order['order_delivered_customer_date'].isna()
    carrier_missing_mask = df_order['order_delivered_carrier_date'].isna()

    #! Move to add Date Features
    df_order['delivery_time'] = df_order['order_delivered_customer_date'] - df_order['order_purchase_timestamp']  
    df_order['delivery_time'] = df_order['delivery_time'].dt.days

    # Calculate mean and std of delivery time
    mask = df_order['delivery_time'].isna()

    # Impute missing delivery times 
    delivery_mean = df_order['delivery_time'].mean()
    delivery_std = df_order['delivery_time'].std()
    df_order.loc[mask, 'delivery_time'] = lognorm.rvs(s=delivery_std, scale=np.exp(delivery_mean))

    # Impute customer and carrier date with purchase date plus average delivery time
    df_order.loc[customer_missing_mask, 'order_delivered_customer_date'] = df_order.loc[customer_missing_mask, 'order_purchase_timestamp']+ dt.timedelta(days=delivery_mean)
    df_order.loc[carrier_missing_mask, 'order_delivered_carrier_date'] = df_order.loc[carrier_missing_mask, 'order_purchase_timestamp']+ dt.timedelta(days=delivery_mean)
    
    return df_order

def merge_product_category(df_product: pd.DataFrame, df_product_category: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the product category data
    """
    df_product = df_product.copy()
    df_product_category = df_product_category.copy()
    df_product = df_product.merge(df_product_category, on='product_category_name', how='inner')
    df_product = df_product.drop(columns=['product_category_name'])
    df_product = df_product.rename(columns={'product_category_name_english': 'product_category_name'})
    return df_product

def order_merge(df_order: pd.DataFrame, df_order_item: pd.DataFrame, df_order_payment: pd.DataFrame, df_order_review: pd.DataFrame) -> pd.DataFrame:

    df_order = df_order.copy()
    df_order_item = df_order_item.copy()
    df_order_payment = df_order_payment.copy()
    df_order_review = df_order_review.copy()
    df_order = df_order.merge(df_order_item, on='order_id', how='inner')
    df_order = df_order.merge(df_order_payment, on='order_id', how='inner')
    df_order = df_order.merge(df_order_review, on='order_id', how='left')
    return df_order

def add_product_volume(df_order_item: pd.DataFrame) -> pd.DataFrame:

    """
    Add the product volume
    """
    df_order_item = df_order_item.copy()
    df_order_item['product_volume'] = df_order_item['product_length_cm'] * df_order_item['product_height_cm'] * df_order_item['product_width_cm']
    return df_order_item

def add_customer_spending(df_customer: pd.DataFrame, df_order: pd.DataFrame, df_order_payment: pd.DataFrame) -> pd.DataFrame:

    """
    Add the customer spending
    """
    df_customer = df_customer.copy()
    df_order = df_order.copy()
    df_order_payment = df_order_payment.copy()

    merged = pd.merge(df_customer, df_order, on='customer_id', how='inner')
    merged = pd.merge(merged, df_order_payment, on='order_id', how='inner')
    customer_spending = merged.groupby('customer_id')['payment_value'].sum().to_frame()

    # Discretize spending
    kbd = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='quantile')

    # Fit and transform
    kbd.fit(customer_spending)
    customer_spending['customer_spending'] = kbd.transform(customer_spending)

    # Merge with customer dataset
    df_customer = pd.merge(df_customer, customer_spending, on='customer_id', how='inner')
    return df_customer

def preprocess_data():
    df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_customer, df_product_category = load_raw_data()
    df_order = convert_to_datetime(df_order)
    df_order = add_date_features(df_order)
    df_order = impute_delivery_dates(df_order)
    # df_customer = map_states_to_regions(df_customer)
    # df_geo = map_states_to_regions(df_geo)
    df_product = merge_product_category(df_product, df_product_category)
    df_order_item = add_product_volume(df_order_item)
    return df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_customer, df_product_category

def save_processed_data():
    df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_customer, df_product_category = preprocess_data()
    df_order.to_csv(DATA_PROCESSED_DIR / 'orders.csv', index=False)
    df_customer.to_csv(DATA_PROCESSED_DIR / 'customers.csv', index=False)
    df_geo.to_csv(DATA_PROCESSED_DIR / 'geolocation.csv', index=False)
    df_order_item.to_csv(DATA_PROCESSED_DIR / 'order_items.csv', index=False)    
    df_order_payment.to_csv(DATA_PROCESSED_DIR / 'order_payments.csv', index=False)
    df_order_review.to_csv(DATA_PROCESSED_DIR / 'order_reviews.csv', index=False)
    df_product.to_csv(DATA_PROCESSED_DIR / 'products.csv', index=False) 
    df_seller.to_csv(DATA_PROCESSED_DIR / 'sellers.csv', index=False)
    df_product_category.to_csv(DATA_PROCESSED_DIR / 'product_category.csv', index=False)
    print("Processed data saved to data/processed/")
if __name__ == "__main__":
    save_processed_data()
    print("Done")