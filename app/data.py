import pandas as pd

def load_raw_data():
    df_geo = pd.read_csv('./data/raw/olist_geolocation_dataset.csv')
    df_order = pd.read_csv('./data/raw/olist_orders_dataset.csv')
    df_order_item = pd.read_csv('./data/raw/olist_order_items_dataset.csv')
    df_order_payment = pd.read_csv('./data/raw/olist_order_payments_dataset.csv')
    df_order_review = pd.read_csv('./data/raw/olist_order_reviews_dataset.csv')
    df_product = pd.read_csv('./data/raw/olist_products_dataset.csv')
    df_seller = pd.read_csv('./data/raw/olist_sellers_dataset.csv')
    df_product_category = pd.read_csv('./data/raw/product_category_name_translation.csv')
    df_customer = pd.read_csv('./data/raw/olist_customers_dataset.csv')

    return df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_product_category, df_customer


def load_processed_data():
    df_order = pd.read_csv('./data/processed/orders_processed.csv')
    df_customer = pd.read_csv('./data/processed/customers_processed.csv')
    df_geo = pd.read_csv('./data/processed/geolocation.csv')
    df_order_item = pd.read_csv('./data/processed/order_items.csv')
    df_order_payment = pd.read_csv('./data/processed/order_payments.csv')
    df_order_review = pd.read_csv('./data/processed/order_reviews.csv')
    df_product = pd.read_csv('./data/processed/products.csv')
    df_seller = pd.read_csv('./data/processed/sellers.csv')
    df_product_category = pd.read_csv('./data/processed/product_category.csv')

    return df_order, df_customer, df_geo, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_product_category

def convert_to_datetime(df):
    df = df.copy()
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    df['order_delivered_carrier_date'] = pd.to_datetime(df['order_delivered_carrier_date'])
    return df

def impute_delivery_dates(df):
    df = df.copy()
    mask = df['order_delivered_customer_date'].isna()
    df['delivery_time'] = (pd.to_datetime(df['order_delivered_customer_date']) - pd.to_datetime(df['order_purchase_timestamp'])).dt.days
    delivery_mean = df['delivery_time'].mean()
    
    df.loc[mask, 'delivery_time'] = delivery_mean
    df.loc[mask, 'order_delivered_carrier_date'] = df.loc[mask, 'order_purchase_timestamp'] + pd.to_timedelta(delivery_mean, unit='d')
    df.loc[mask, 'order_delivered_customer_date'] = df.loc[mask, 'order_purchase_timestamp'] + pd.to_timedelta(delivery_mean, unit='d')
    
    return df

def map_states_to_regions(df):
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
    if 'customer_state' in df.columns:
        df['customer_region'] = df['customer_state'].map(state_to_region)
    if 'geolocation_state' in df.columns:
        df['geolocation_region'] = df['geolocation_state'].map(state_to_region)
    return df


def get_sales_by_region(df_customer, df_orders, df_geo, df_order_item, df_product):
    df_customer = df_customer.copy()
    df_orders = df_orders.copy()
    df_geo = df_geo.copy()
    df_order_item = df_order_item.copy()
    df_product = df_product.copy()
    print(df_geo.columns)
    # Get unique zips with city, state, lat, lng, and region
    unique_zips = (df_geo[['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state','geolocation_lat','geolocation_lng', 'geolocation_region']]
                    .groupby('geolocation_zip_code_prefix')
                    .first())

    # Merge order and customer data to get zips
    customer_order = pd.merge(df_orders, df_customer, on='customer_id', how='inner')

    # Merge zips and geo location with customer order data
    customer_order_geo = pd.merge(unique_zips, customer_order, left_on='geolocation_zip_code_prefix', right_on='customer_zip_code_prefix', how='inner')

    # Calculate sales by region and product category
    sales_by_region = (customer_order_geo
            .merge(df_order_item, on='order_id', how='inner')
            .merge(df_product, on='product_id', how='inner')
            .groupby(["product_category_name", "geolocation_region"])
            .agg({"price": "sum", "order_id": "count"})
            .reset_index()
            .rename(columns={"product_category_name": "Product Category", "price": "Sales", "order_id": "Orders"}))

    # Calculate ARPU
    sales_by_region = (sales_by_region
            .assign(ARPU=lambda x: round(x["Sales"] / x["Orders"], 2))
            .sort_values(by="ARPU", ascending=False))
    
    return sales_by_region

def get_sales_over_time(df_order):
    import calendar
    df_order = df_order.copy()

    #Convert timestamp to month, year, and day
    df_order['order_purchase_month'] = pd.to_datetime(df_order['order_purchase_timestamp']).dt.month
    df_order['order_purchase_year'] = pd.to_datetime(df_order['order_purchase_timestamp']).dt.year
    df_order['order_purchase_day'] = pd.to_datetime(df_order['order_purchase_timestamp']).dt.day

    # Group by year and month and count the number of orders
    sales_over_time = df_order.groupby(['order_purchase_year', 'order_purchase_month'])['order_id'].count().reset_index()

    # Convert month number to month name
    sales_over_time['order_purchase_month_word'] = sales_over_time['order_purchase_month'].apply(lambda x: calendar.month_name[x])
    return sales_over_time  

def get_top_categories(df_order_item, df_product):
    df_order_item = df_order_item.copy()
    df_product = df_product.copy()
    top_cats = (
    df_order_item
            .merge(df_product[['product_id', 'product_category_name']], on='product_id', how='inner')
            .groupby('product_category_name')['price']
            .sum()
            .reset_index()
            .sort_values(by='price', ascending=False)
            .head(10)
    )
    top_cats['price_pct'] = 100 * top_cats['price'] / top_cats['price'].sum()
    return top_cats