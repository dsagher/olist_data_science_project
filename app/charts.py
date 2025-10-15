import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import altair as alt
import logging
logging.basicConfig(level=logging.INFO)

# Use relative import when imported as a module, absolute when run directly
try:
    from . import views
except ImportError:
    import views

def product_categories_by_sales(df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> alt.Chart:
    """
    Features: Product Category, Total Sales, Percentage of Top 10
    """
    top_categories = views.get_top_categories(df_order_item, df_product)

    bar_chart = alt.Chart(top_categories).mark_bar(opacity=0.85).encode(
        x=alt.X('product_category_name:N', sort='-y', title='Product Category', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('price:Q', title='Total Sales (BRL)'),
        color=alt.Color(field="product_category_name", type="nominal")
    ).properties(
        title='Top 10 Product Categories by Sales',
        width=500
    )

    return bar_chart

def percentage_of_sales_by_product_category(df_order_item: pd.DataFrame, df_product: pd.DataFrame) -> alt.Chart:
    """
    Features: Product Category, Percentage of Top 10
    """

    top_categories = views.get_top_categories(df_order_item, df_product)
    pie_chart = alt.Chart(top_categories).mark_arc(opacity=0.85).encode(
        theta=alt.Theta(field="price", type="quantitative"),
        color=alt.Color(field="product_category_name", type="nominal"),
    ).properties(
        title="Top 10 Categories as Percentage of Sales",
        width=350,
        height=350
    )
    return pie_chart

def sales_vs_arpu_by_product_category_and_region(sales_by_region: pd.DataFrame) -> alt.Chart:
    """
    Features: Sales, ARPU, Order Count, Region, Product Category
    """
    bubble_chart = alt.Chart(sales_by_region).mark_circle(opacity=0.7).encode(
    x=alt.X('Sales:Q', title='Total Sales (BRL)'),
    y=alt.Y('ARPU:Q', title='Average Revenue per Order (ARPU)'),
    size=alt.Size('Orders:Q', title='Order Count', scale=alt.Scale(range=[30, 1000])),
    color=alt.Color('geolocation_region:N', title='Region'),
    tooltip=['Product Category', 'geolocation_region', 'Sales', 'ARPU', 'Orders']
).properties(
    title='Sales vs ARPU by Product Category and Region',
    width=800,
    height=500
).interactive()

    return bubble_chart

def sales_over_time_chart(sales_over_time: pd.DataFrame) -> alt.Chart:
    """
    Features: Month, Order Count
    """


    seventeen_eighteen_chart = alt.Chart(sales_over_time
    ).mark_area(opacity=0.6).encode(
        x=alt.X(
            "order_purchase_month_word:O",
            title="Month",
            sort=[
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ]
        ),
        y=alt.Y("order_id", title="Sales"),
        color=alt.Color(
            "order_purchase_year:O",
            title="Year",
            scale=alt.Scale(domain=[2017, 2018], range=['darkgreen', 'orange'])
        )
    ).properties(
        title='2017–2018 Sales by Month',
        width=1250,
        height=500
    )

    return seventeen_eighteen_chart

def delivery_nulls_by_date_chart(df_order: pd.DataFrame) -> alt.Chart:
    """
    Features: Order Purchase Date, Delivery Null Count
    """
    # Count missing carrier and customer delivery dates by purchase date (binned by month)
    df_order['order_purchase_timestamp'] = pd.to_datetime(df_order['order_purchase_timestamp'])
    df_order['order_purchase_month'] = df_order['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()
    
    # Deliveries with missing carrier dates
    carrier_missing = df_order['order_delivered_carrier_date'].isna()
    carrier_nulls = df_order[carrier_missing].groupby('order_purchase_month').size().reset_index(name='Carrier Delivery Nulls')
    
    # Deliveries with missing customer dates
    customer_missing = df_order['order_delivered_customer_date'].isna()
    customer_nulls = df_order[customer_missing].groupby('order_purchase_month').size().reset_index(name='Customer Delivery Nulls')
    
    # Melt to long format for combined plot
    carrier_nulls['Type'] = 'Carrier Delivery Nulls'
    customer_nulls['Type'] = 'Customer Delivery Nulls'
    carrier_nulls = carrier_nulls.rename(columns={'Carrier Delivery Nulls': 'Null Count'})
    customer_nulls = customer_nulls.rename(columns={'Customer Delivery Nulls': 'Null Count'})
    nulls_all = pd.concat([carrier_nulls, customer_nulls], ignore_index=True)
    
    chart = alt.Chart(nulls_all).mark_bar(size=40, opacity=0.8, color='steelblue').encode(
        x=alt.X('order_purchase_month:T', title='Order Purchase Month', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('Null Count:Q', title='Number of Nulls'),
        color=alt.Color('Type:N', title='Null Type'),
        tooltip=['order_purchase_month:T', 'Null Count:Q', 'Type:N']
    ).properties(
        width=800,
        height=400,
        title='Delivery Nulls by Order Purchase Month'
    )
    return chart

def cancelled_orders_by_date_chart(df_order: pd.DataFrame) -> alt.Chart:
    # Use Altair to visualize cancelled orders by date
    df_order['order_purchase_timestamp'] = pd.to_datetime(df_order['order_purchase_timestamp'])
    canceled_mask = df_order['order_status'] == 'canceled'
    canceled_df = df_order.loc[canceled_mask].copy()
    # Bin by month for visualization
    canceled_df['month'] = canceled_df['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()
    cancelled_counts = canceled_df.groupby('month').size().reset_index(name='count')
    
    chart = alt.Chart(cancelled_counts).mark_bar(color='tomato', size=40, opacity=0.8).encode(
        x=alt.X('month:T', title='Purchase Month', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('count:Q', title='Number of Cancelled Orders')
    ).properties(
        width=750,
        height=400,
        title='Cancelled Orders by Month'
    )
    return chart

def delivery_nulls_chart(df_order: pd.DataFrame) -> alt.Chart:
    """
    Features: Order Purchase Date, Delivery Null Count
    """
    logging.debug(df_order.columns)
    
    # Convert timestamp to datetime if it's not already
    if 'order_purchase_month' not in df_order.columns:
        df_order['order_purchase_timestamp'] = pd.to_datetime(df_order['order_purchase_timestamp'])
        df_order['order_purchase_month'] = df_order['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()
    
    carrier_all, customer_all = views.get_delivery_nulls(df_order)
    chart_customer = alt.Chart(customer_all).mark_bar(size=40, opacity=0.8, color='orange').encode(
        x=alt.X('order_purchase_month:T', title='Order Purchase Month', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('Null Count:Q', title='Number of Nulls'),
        color=alt.Color('Type:N', title='Null Type'),
        tooltip=['order_purchase_month:T', 'Null Count:Q', 'Type:N']
    ).properties(
        width=800,
        height=400,
        title='Delivery Nulls by Order Purchase Month (Customer)'
    )

    chart_carrier = alt.Chart(carrier_all).mark_bar(size=40, opacity=0.8, color='steelblue').encode(
        x=alt.X('order_purchase_month:T', title='Order Purchase Month', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('Null Count:Q', title='Number of Nulls'),
        color=alt.Color('Type:N', title='Null Type'),
        tooltip=['order_purchase_month:T', 'Null Count:Q', 'Type:N']
    ).properties(
        width=800,
        height=400,
        title='Delivery Nulls by Order Purchase Month (Carrier)'
    )
    return chart_customer, chart_carrier

def missingness_heatmap(df: pd.DataFrame) -> plt.Figure:
    """
    Features: Missingness Heatmap
    """
    fig, ax = plt.subplots(figsize=(10,10))
    ax = sns.heatmap(df.isna().transpose(), cbar=False, cmap='viridis', ax=ax)
    return fig

def cancellation_chart(df_order: pd.DataFrame) -> alt.Chart:
    """
    Features: Order Purchase Date, Cancellation Count
    """    
    # Convert timestamp to datetime if it's not already
    if 'order_purchase_month' not in df_order.columns:
        logging.debug('Adding order purchase month')
        df_order['order_purchase_timestamp'] = pd.to_datetime(df_order['order_purchase_timestamp'])
        df_order['order_purchase_month'] = df_order['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()

    canceled_mask = df_order['order_status'] == 'canceled'
    canceled_df = df_order.loc[canceled_mask, 'order_purchase_month'].copy().reset_index(drop=True).to_frame()
    grouped = canceled_df.groupby('order_purchase_month').size().reset_index(name='count')
    grouped
    chart = alt.Chart(grouped).mark_bar(color='tomato', size=40, opacity=0.8).encode(
        x=alt.X('order_purchase_month:T', title='Purchase Month', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('count:Q', title='Number of Cancelled Orders')
    ).properties(
        width=750,
        height=400,
        title='Cancelled Orders by Month'
    )
    return chart

def orders_correlation_heatmap(df_order: pd.DataFrame) -> plt.Figure:

    numeric_cols = ['price', 'freight_value', 'payment_value', 
                    'payment_installments', 'delivery_time', 'review_score']
    corr_data = df_order[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, ax=ax, square=True)
    return fig

def revenue_ARPU_by_region_and_product_category_chart(sales_by_region: pd.DataFrame) -> alt.Chart:

    """
    Features: Sales, ARPU, Order Count, Region, Product Category
    """
    bubble_chart = alt.Chart(sales_by_region).mark_circle(opacity=0.7).encode(
        x=alt.X('Sales:Q', title='Total Sales (BRL)'),
        y=alt.Y('ARPU:Q', title='Average Revenue per Order (ARPU)'),
        size=alt.Size('Orders:Q', title='Order Count', scale=alt.Scale(range=[30, 1000])),
        color=alt.Color('geolocation_region:N', title='Region'),
        tooltip=['Product Category', 'geolocation_region', 'Sales', 'ARPU', 'Orders']
    ).properties(
        title='Sales vs ARPU by Product Category and Region',
        width=800,
        height=500
    ).interactive()

    return bubble_chart

def product_delivery_time_chart(order_item_product: pd.DataFrame) -> alt.Chart:
    numeric_cols = ['product_weight_g', 'price','freight_value', 'delivery_time', 'product_volume']
    for_analysis = order_item_product[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 10))
    ax = sns.heatmap(for_analysis[numeric_cols].corr(), annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Correlation Heatmap of Product Dimensions and Delivery Time')

    return fig