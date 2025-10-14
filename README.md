# Olist Sales Analysis Dashboard

Welcome to the Olist Sales Analysis Dashboard! This project uses the [Olist E-commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), a comprehensive dataset containing information about orders, products, sellers, customers, and geolocations from one of Brazil's largest marketplaces.

---

## Why We Chose This Dataset

We chose the Olist E-commerce dataset because:
- **Richness & Scope**: It offers granular transaction-level data, customer demographics, locations, product categories, payments, and reviews.
- **Real-world Complexity**: The multi-table relational structure provides rich opportunities for analysis and ETL challenges that are typical in business and data science roles.
- **Business Relevance**: Understanding e-commerce dynamics (sales, regional performance, ARPU, product categories) is valuable for business insight and analytics.

---

## What We Learned from IDA/EDA

Through our initial and exploratory data analysis:
- **Regional Trends**: Most orders are concentrated in the Southeast and South regions; the North has the fewest customers and orders.
- **Sales Seasonality**: There are clear sales peaks at certain times, e.g., end-of-year increases.
- **Top Categories**: A small number of product categories drive a large share of revenues.
- **Delivery Issues**: Some orders lack delivery timestamps due to cancellations or system issues.
- **Customer Distribution**: Customers are primarily urban but spread across many Brazilian states and cities.

---

## Preprocessing Steps Completed

To prepare the data for dashboarding and analysis, we:
- **Datetime Conversion & Imputation**: Converted date columns to datetime types and imputed missing delivery times using mean-based approaches.
- **Region Mapping**: Mapped customer and geo states to five macro-regions of Brazil for clearer aggregation.
- **Data Merging**: Merged customer, order, product, and geolocation tables to connect spatial, product, and transaction data.
- **Top Categories Extraction**: Identified the top 10 product categories by sales for focused analysis.
- **Cleaned Dataframes**: Loaded, selected, and grouped relevant columns to reduce redundancy and speed up analysis.

---

## What We Have Tried with Streamlit

So far, we have:
- **Developed an Interactive Dashboard**: Showing sales by region, product categories, and trends over time using Altair charts.
- **Implemented Comparative Visualizations**: 
    - Bubble charts display sales, ARPU, and order counts by region and product.
    - Bar and pie charts highlight top product categories and their sales/percentage shares.
- **Handled Data Loading & Processing**: The Streamlit app loads raw data, performs all processing steps on the fly, and serves interactive visualizations.
- **Enabled Filtered Analysis**: Separated charts for selected years/months to analyze trends.

---

## How to Run

1. Clone this repository.
2. Install requirements (`pip install -r requirements.txt`).
3. Ensure the raw Olist data is present in `./data/raw/` as provided on Kaggle.
4. Run `streamlit run app/streamlit.py`.
5. Explore the dashboard in your browser!

---
