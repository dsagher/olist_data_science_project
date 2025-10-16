import string
import pandas as pd
import altair as alt
import logging


logging.basicConfig(level=logging.DEBUG)

"""-------------------------Merge Views--------------------------"""

def get_orders_merged():
    pass

def get_sales_by_region(df_customer: pd.DataFrame, df_orders: pd.DataFrame, df_geo: pd.DataFrame, df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> pd.DataFrame:
    df_customer = df_customer.copy()
    df_orders = df_orders.copy()
    df_geo = df_geo.copy()
    df_order_item = df_order_item.copy()
    df_product = df_product.copy()

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

def get_sales_over_time(df_order: pd.DataFrame, df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> pd.DataFrame:
    import calendar
    df_order = df_order.copy()

    #Convert timestamp to month, year, and day
    #! Why isn't this already a datetime column?
    df_order['order_purchase_month'] = pd.to_datetime(df_order['order_purchase_timestamp']).dt.month
    df_order['order_purchase_year'] = pd.to_datetime(df_order['order_purchase_timestamp']).dt.year
    df_order['order_purchase_day'] = pd.to_datetime(df_order['order_purchase_timestamp']).dt.day
    order_item_product = df_order_item.merge(df_product, on='product_id', how='inner')
    order_order_item_product = df_order.merge(order_item_product, on='order_id', how='inner')
    # Group by year and month and count the number of orders
    sales_over_time = order_order_item_product.groupby(['order_purchase_year', 'order_purchase_month', 'product_category_name'])['price'].sum().reset_index()

    # Convert month number to month name
    sales_over_time['order_purchase_month_word'] = sales_over_time['order_purchase_month'].apply(lambda x: calendar.month_name[x])
    return sales_over_time  

def get_top_categories(df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> pd.DataFrame:
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

def get_delivery_nulls(df_order: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
        _order = df_order.copy()
        if 'order_purchase_month' not in df_order.columns:
                df_order['order_purchase_month'] = df_order['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()

        carrier_missing = df_order['order_delivered_carrier_date'].isna()
        customer_missing = df_order['order_delivered_customer_date'].isna()
        carrier_nulls = (
        df_order[carrier_missing]
        .groupby('order_purchase_month')
        .size()
        .reset_index(name='Null Count')
        )
        carrier_nulls['Type'] = 'Carrier Delivery Nulls'

        carrier_not_missing = (
        df_order[~carrier_missing]
        .groupby('order_purchase_month')
        .size()
        .reset_index(name='Null Count')
        )
        carrier_not_missing['Type'] = 'Carrier Delivery Not Missing'
        
        customer_nulls = (
        df_order[customer_missing]
        .groupby('order_purchase_month')
        .size()
        .reset_index(name='Null Count')
        )
        customer_nulls['Type'] = 'Customer Delivery Nulls'

        customer_not_missing = (
        df_order[~customer_missing]
        .groupby('order_purchase_month')
        .size()
        .reset_index(name='Null Count')
        )
        customer_not_missing['Type'] = 'Customer Delivery Not Missing'

        customer_all = pd.concat([customer_nulls, customer_not_missing], ignore_index=True)

        carrier_all = pd.concat([carrier_nulls, carrier_not_missing], ignore_index=True)

        return carrier_all, customer_all


"""--------------------------KPI Views--------------------------"""
def get_total_revenue(df_order_item: pd.DataFrame) -> str:
    return f"${df_order_item['price'].sum().astype(int):,.0f}"

def get_total_orders(df: pd.DataFrame) -> str:
    return f"{df['order_id'].nunique():,.0f}"

def get_total_customers(df: pd.DataFrame) -> str:
    return f"{df['customer_id'].nunique():,.0f}"

def get_total_products(df: pd.DataFrame) -> str:
    return f"{df['product_id'].nunique():,.0f}"

def get_highest_selling_city(df_order: pd.DataFrame, df_order_item: pd.DataFrame, df_customer: pd.DataFrame, df_geo: pd.DataFrame) -> str:
    df_order = df_order.copy()
    df_order_item = df_order_item.copy()
    df_customer = df_customer.copy()
    df_geo = df_geo.copy()

    highest_selling_city = (df_order
        .merge(df_order_item, on='order_id', how='left')
        .merge(df_customer, on='customer_id', how='left')
        .merge(df_geo, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')
        .groupby('geolocation_city')
        .agg({'order_id': 'count'})
        .sort_values(by='order_id', ascending=False).head(1)).index[0]

    return highest_selling_city

def get_revenue_ARPU_by_region(df_customer: pd.DataFrame, df_order: pd.DataFrame, df_geo: pd.DataFrame, df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> pd.DataFrame:


    df_customer = df_customer.copy()
    df_order = df_order.copy()
    df_geo = df_geo.copy()
    df_order_item = df_order_item.copy()
    df_product = df_product.copy()

    # Get unique zips with city, state, lat, lng, and region
    unique_zips = (df_geo[['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state','geolocation_lat','geolocation_lng', 'geolocation_region']]
                    .groupby('geolocation_zip_code_prefix')
                    .first())

    # Merge order and customer data to get zips
    customer_order = pd.merge(df_order, df_customer, on='customer_id', how='inner')

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

def get_product_delivery_time(df_order_item: pd.DataFrame, df_product: pd.DataFrame, df_order: pd.DataFrame) -> pd.DataFrame:
    df_order_item = df_order_item.copy()
    df_product = df_product.copy()
    df_order = df_order.copy()
    product_desc_cols = ['product_description_lenght','product_weight_g','product_length_cm','product_height_cm','product_width_cm', 'product_id']
    for_analysis = df_order_item.merge(df_product[product_desc_cols], on='product_id', how='inner')
    for_analysis = for_analysis.merge(df_order, on='order_id', how='inner')
    for_analysis['product_volume'] = for_analysis['product_length_cm'] * for_analysis['product_height_cm'] * for_analysis['product_width_cm']
    return for_analysis

def get_highest_selling_category(df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> str:
    df_order_item = df_order_item.copy()
    df_product = df_product.copy()
    highest_selling_category = (df_order_item
        .merge(df_product[['product_id', 'product_category_name']], on='product_id', how='inner')
        .groupby('product_category_name')
        .agg({'price': 'sum'})
        .sort_values(by='price', ascending=False).head(1)).index[0]
    return highest_selling_category

def get_above_average_sales_and_below_average_arpu(sales_by_region: pd.DataFrame, df_order: pd.DataFrame, df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> pd.DataFrame:
    # Means
    avg_ARPU = sales_by_region["ARPU"].mean()
    avg_sales = sales_by_region['Sales'].mean()

    # Above average sales, below average ARPU
    mask = (sales_by_region['Sales'] > avg_sales) & (sales_by_region['ARPU'] < avg_ARPU)

    # Top 10
    above_avg = sales_by_region.loc[mask].sort_values(by=['Sales']).head(10)

    # Merge order, order_item, product, and above average to grab top sales
    merge = (df_order
            .merge(df_order_item)
            .merge(df_product)
            .merge(above_avg, left_on="product_category_name", right_on="Product Category")
            [['ARPU','geolocation_region','price', "product_category_name", "order_purchase_month"]])

    merge['order_purchase_month'] = pd.to_datetime(merge['order_purchase_month'])
    return merge

def get_below_average_sales_and_above_average_arpu(sales_by_region: pd.DataFrame, df_order: pd.DataFrame, df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> pd.DataFrame:
    # Means
    avg_ARPU = sales_by_region["ARPU"].mean()
    avg_sales = sales_by_region['Sales'].mean()

    # Above average sales, below average ARPU
    mask = (sales_by_region['Sales'] < avg_sales) & (sales_by_region['ARPU'] > avg_ARPU)

    # Top 10
    below_avg = sales_by_region.loc[mask].sort_values(by=['Sales']).head(10)

    # Merge order, order_item, product, and above average to grab top sales
    merge = (df_order
            .merge(df_order_item)
            .merge(df_product)
            .merge(below_avg, left_on="product_category_name", right_on="Product Category")
            [['ARPU','geolocation_region','price', "product_category_name", "order_purchase_month"]])

    merge['order_purchase_month'] = pd.to_datetime(merge['order_purchase_month'])
    return merge

"""--------------------------Aggregate Views--------------------------"""