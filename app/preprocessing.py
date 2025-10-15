from data import (load_raw_data, 
                convert_to_datetime, 
                impute_delivery_dates, 
                map_states_to_regions, 
                merge_product_category, 
                add_date_features,
                add_product_volume,
                DATA_PROCESSED_DIR)

def preprocess_data():
    df_geo, df_order, df_order_item, df_order_payment, df_order_review, df_product, df_seller, df_customer, df_product_category = load_raw_data()
    df_order = convert_to_datetime(df_order)
    df_order = add_date_features(df_order)
    df_order = impute_delivery_dates(df_order)
    df_customer = map_states_to_regions(df_customer)
    df_geo = map_states_to_regions(df_geo)
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