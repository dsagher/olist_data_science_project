import pandas as pd
from scipy.stats import lognorm
import numpy as np
import datetime as dt
from pathlib import Path
from sklearn.preprocessing import KBinsDiscretizer
from streamlit import cache_data

# Get the project root directory
# preprocessing.py -> assets/ -> app/ -> project_root/
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'

def map_states_to_regions(data: dict) -> dict:
    """
    Map the states to the regions

    Args:
        data: dict (data['customer'] or data['geo'])
            Columns: geolocation_state (data['geo']) or customer_state (data['customer'])
    Returns:
        data: dict (data['customer'] or data['geo'])
            Columns: region (data['customer'] or data['geo'])
            Data:
                - Southeast: SP, MG, RJ, ES
                - South: PR, SC, RS
                - Central-West: DF, GO, MS, MT
                - Northeast: BA, SE, AL, PE, PB, RN, CE, PI, MA
                - North: PA, AM, AP, RO, RR, TO
    Raises:
        ValueError: If the state column is not found in the data['geo'] or data['customer'] dataframe
    """    
    STATE_TO_REGION = {
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

    data['geo']['region'] = data['geo']['state'].map(STATE_TO_REGION)
    data['customer']['region'] = data['customer']['state'].map(STATE_TO_REGION)

    return data


def load_raw_data()-> dict:
    return {
        'geo': pd.read_csv(DATA_RAW_DIR / 'olist_geolocation_dataset.csv'),
        'order': pd.read_csv(DATA_RAW_DIR / 'olist_orders_dataset.csv'),
        'order_item': pd.read_csv(DATA_RAW_DIR / 'olist_order_items_dataset.csv'),
        'order_payment': pd.read_csv(DATA_RAW_DIR / 'olist_order_payments_dataset.csv'),
        'order_review': pd.read_csv(DATA_RAW_DIR / 'olist_order_reviews_dataset.csv'),
        'product': pd.read_csv(DATA_RAW_DIR / 'olist_products_dataset.csv'),
        'seller': pd.read_csv(DATA_RAW_DIR / 'olist_sellers_dataset.csv'),
        'customer': pd.read_csv(DATA_RAW_DIR / 'olist_customers_dataset.csv'),
        'product_category': pd.read_csv(DATA_RAW_DIR / 'product_category_name_translation.csv')
        }


def load_processed_data() -> dict:
    return {
        'geo': pd.read_csv(DATA_PROCESSED_DIR / 'geo.csv'),
        'order': pd.read_csv(DATA_PROCESSED_DIR / 'order.csv', parse_dates=['purchase_timestamp', 'approved_timestamp', 'delivered_carrier_date', 'delivered_customer_date', 'purchase_month']),
        'order_item': pd.read_csv(DATA_PROCESSED_DIR / 'order_item.csv'),
        'order_payment': pd.read_csv(DATA_PROCESSED_DIR / 'order_payment.csv'),
        'order_review': pd.read_csv(DATA_PROCESSED_DIR / 'order_review.csv'),
        'product': pd.read_csv(DATA_PROCESSED_DIR / 'product.csv'),
        'seller': pd.read_csv(DATA_PROCESSED_DIR / 'seller.csv'),
        'customer': pd.read_csv(DATA_PROCESSED_DIR / 'customer.csv'),
        'product_category': pd.read_csv(DATA_PROCESSED_DIR / 'product_category.csv')
    }

@cache_data
def load_processed_data_streamlit() -> dict:
    return load_processed_data()

def rename_columns(data: dict) -> dict:
    """
    Rename the columns

    Args:
        data: dict 
    Returns:
        data: dict
            Data:
                - renamed columns
    """
    data['geo'] = data['geo'].rename(columns={
                            "geolocation_zip_code_prefix": "zip_code_prefix", 
                            "geolocation_city": "city", 
                            "geolocation_state": "state",
                            'geolocation_lat': 'latitude',
                            'geolocation_lng': 'longitude'})
    data['customer'] = data['customer'].rename(columns={'customer_id': "customer_id", 
                                            "customer_unique_id": "unique_id", 
                                            "customer_zip_code_prefix": "zip_code_prefix",
                                            "customer_city": "city", 
                                            "customer_state": "state"})
    data['product'] = data['product'].rename(columns={" product_category_name": "category_name",
                                             "product_photos_qty": "photos_qty",
                                             "product_name_lenght": "name_length",
                                             "product_description_length": "description_length",
                                             "product_weight_g": "weight",
                                             "product_length_cm": "length",
                                             "product_height_cm": "height",
                                             "product_width_cm": "width"})
    data['order'] = data['order'].rename(columns={"order_id": "order_id", 
                                        "order_purchase_timestamp": "purchase_timestamp",
                                        "order_approved_at": "approved_timestamp",
                                        "order_delivered_customer_date": "delivered_customer_date",
                                        "order_delivered_carrier_date": "delivered_carrier_date"})
    data['seller'] = data['seller'].rename(columns={"seller_zip_code_prefix": "zip_code_prefix", 
                                            "seller_city": "city", 
                                            "seller_state": "state"})
    return data

def convert_to_datetime(data: dict) -> dict:
    """
    Convert the timestamp columns to datetime
    """
    data['order'] = data['order']
    data['order']['purchase_timestamp'] = pd.to_datetime(data['order']['purchase_timestamp'])
    data['order']['approved_timestamp'] = pd.to_datetime(data['order']['approved_timestamp'])
    data['order']['delivered_customer_date'] = pd.to_datetime(data['order']['delivered_customer_date'])
    data['order']['delivered_carrier_date'] = pd.to_datetime(data['order']['delivered_carrier_date'])
    return data

def add_date_features(data: dict) -> dict:
    """
    Add the date features
    """

    data['order'] = data['order']
    data['order']['purchase_month'] = data['order']['purchase_timestamp'].dt.to_period('M').dt.to_timestamp()
    data['order']['purchase_year'] = data['order']['purchase_timestamp'].dt.year
    data['order']['purchase_quarter'] = data['order']['purchase_timestamp'].dt.quarter
    data['order']['purchase_day'] = data['order']['purchase_timestamp'].dt.day
    data['order']['purchase_dayofweek'] = data['order']['purchase_timestamp'].dt.dayofweek
    data['order']['purchase_dayofyear'] = data['order']['purchase_timestamp'].dt.dayofyear
    data['order']['purchase_weekday'] = data['order']['purchase_timestamp'].dt.weekday
    return data

def impute_delivery_dates(data: dict) -> dict:
    """
    Impute the delivery dates
    """
    data['order'] = data['order']
    customer_missing_mask = data['order']['delivered_customer_date'].isna()
    carrier_missing_mask = data['order']['delivered_carrier_date'].isna()

    #! Move to add Date Features
    data['order']['delivery_time'] = data['order']['delivered_customer_date'] - data['order']['purchase_timestamp']  
    data['order']['delivery_time'] = data['order']['delivery_time'].dt.days

    # Calculate mean and std of delivery time
    mask = data['order']['delivery_time'].isna()

    # Impute missing delivery times 
    delivery_mean = data['order']['delivery_time'].mean()
    delivery_std = data['order']['delivery_time'].std()
    data['order'].loc[mask, 'delivery_time'] = lognorm.rvs(s=delivery_std, scale=np.exp(delivery_mean))

    # Impute customer and carrier date with purchase date plus average delivery time
    data['order'].loc[customer_missing_mask, 'order_delivered_customer_date'] = data['order'].loc[customer_missing_mask, 'purchase_timestamp']+ dt.timedelta(days=delivery_mean)
    data['order'].loc[carrier_missing_mask, 'order_delivered_carrier_date'] = data['order'].loc[carrier_missing_mask, 'purchase_timestamp']+ dt.timedelta(days=delivery_mean)
    
    return data

def merge_product_category(data: dict) -> dict:
    """
    Merge the product category data
    """

    data['product'] = data['product'].merge(data['product_category'], on='product_category_name', how='inner')
    data['product'] = data['product'].drop(columns=['product_category_name'])
    data['product'] = data['product'].rename(columns={'product_category_name_english': 'category_name'})
    return data

def order_merge(data: dict) -> dict:

    data['order'] = data['order'].merge(data['order_item'], on='order_id', how='inner')
    data['order'] = data['order'].merge(data['order_payment'], on='order_id', how='inner')
    data['order'] = data['order'].merge(data['order_review'], on='order_id', how='left')
    return data

def add_product_volume(data: dict) -> dict:

    """
    Add the product volume
    """
    data['order_item'] = data['order_item']
    data['product'] = data['product']
    data['order_item'] = data['order_item'].merge(data['product'], on='product_id', how='inner')
    data['order_item']['product_volume'] = data['order_item']['length'] * data['order_item']['height'] * data['order_item']['width']
    return data

def add_customer_spending(data: dict) -> dict:
    """
    Add the customer spending
    """
    data['customer'] = data['customer']
    data['order'] = data['order']
    data['order_payment'] = data['order_payment']

    merged = pd.merge(data['customer'], data['order'], on='customer_id', how='inner')
    merged = pd.merge(merged, data['order_payment'], on='order_id', how='inner')
    customer_spending = merged.groupby('customer_id')['payment_value'].sum().to_frame()

    # Discretize spending
    kbd = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='quantile')

    # Fit and transform
    kbd.fit(customer_spending)
    customer_spending['customer_spending'] = kbd.transform(customer_spending)

    # Merge with customer dataset
    data['customer'] = pd.merge(data['customer'], customer_spending, on='customer_id', how='inner')
    return data

def preprocess_data() -> dict:
    data = load_raw_data()
    data = rename_columns(data)
    data = convert_to_datetime(data)
    data = add_date_features(data)
    data = impute_delivery_dates(data)
    data = map_states_to_regions(data)
    data = merge_product_category(data)
    data = add_product_volume(data)
    data = add_customer_spending(data)
    return data

def save_processed_data() -> None:
    print("Processing data...")
    data = preprocess_data()

    for key, value in data.items():
        print(f"Saving {key}...")
        value.to_csv(DATA_PROCESSED_DIR / f'{key}.csv', index=False)
        print(f"{key} saved to data/processed/")
    print("All data saved to data/processed/")
    print("Done")
    return

if __name__ == "__main__":
    save_processed_data()
    print("Done")