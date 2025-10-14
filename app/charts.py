import altair as alt
from data import get_top_categories

def product_categories_by_sales(df_order_item, df_product):
    top_categories = get_top_categories(df_order_item, df_product)
    """
    Features: Product Category, Total Sales, Percentage of Top 10
    """

    bar_chart = alt.Chart(top_categories).mark_bar(opacity=0.85).encode(
        x=alt.X('product_category_name:N', sort='-y', title='Product Category', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('price:Q', title='Total Sales (BRL)'),
        color=alt.Color(field="product_category_name", type="nominal")
    ).properties(
        title='Top 10 Product Categories by Sales',
        width=500
    )

    return bar_chart

def percentage_of_sales_by_product_category(df_order_item, df_product):
    top_categories = get_top_categories(df_order_item, df_product)
    """
    Features: Product Category, Percentage of Top 10
    """
    pie_chart = alt.Chart(top_categories).mark_arc(opacity=0.85).encode(
        theta=alt.Theta(field="price", type="quantitative"),
        color=alt.Color(field="product_category_name", type="nominal"),
    ).properties(
        title="Top 10 Categories as Percentage of Sales",
        width=350,
        height=350
    )
    return pie_chart

def sales_vs_arpu_by_product_category_and_region(sales_by_region):
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

def sales_over_time_chart(sales_over_time):
    """
    Features: Month, Order Count
    """
    mask = (sales_over_time['order_purchase_year'] == 2018) | (sales_over_time['order_purchase_year'] == 2017)

    seventeen_eighteen_chart = alt.Chart(sales_over_time[mask]
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