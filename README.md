# 🛍️ Exploring Customer Purchasing Patterns for Understanding Product Preferences and Sales Trends in Retail Data

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red?logo=streamlit)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-green?logo=pandas)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-purple?logo=plotly)](https://plotly.com)

> **Academic Capstone / College Project** — Retail Data Analytics & Business Intelligence Dashboard

---

## 📌 Project Overview

In modern retail, organizations collect millions of transaction records daily — but raw data alone provides no strategic value without proper analysis. This project delivers an **interactive, end-to-end retail analytics dashboard** that transforms flat transaction CSV data into actionable business intelligence.

The dashboard enables retail managers and academic evaluators to:
- Monitor core business KPIs (Revenue, Orders, Average Order Value)
- Identify top-selling products and most profitable categories
- Discover seasonal sales peaks across months and days of the week
- Understand purchasing behavior across customer age groups and genders
- Compare geographic market performance across cities
- Evaluate customer payment channel preferences

---

## 🎯 Problem Statement

Retail organizations struggle to answer critical operational questions from raw transaction logs:
- *Which product categories drive the most revenue?*
- *How does purchasing behavior differ by customer demographics?*
- *Which months and days see peak sales activity?*
- *Which cities have the highest Average Order Value?*

This project solves these questions through a modular, filterable, and visually rich analytics dashboard.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **5 KPI Cards** | Total Revenue, Total Orders, Average Order Value, Units Sold, Active Customers |
| **Global Sidebar Filters** | Date Range, Product Category, City, Gender, Payment Method |
| **Monthly Sales Trend** | Dual-axis chart (Revenue bars + Transaction count line) |
| **Daily Sales Area Chart** | Day-by-day revenue trajectory |
| **Day-of-Week Analysis** | Both interactive Plotly chart and academic Seaborn visualization |
| **Product Category Performance** | Revenue ranking, share %, avg price, transaction count |
| **Top 10 Products Leaderboard** | Ranked by volume or revenue — switchable |
| **Customer Demographics** | Age group bars, gender pie chart, Age×Gender heatmap |
| **City-wise Comparison** | Revenue, orders, and AOV per metropolitan market |
| **Payment Method Distribution** | Transaction share % across Credit Card, UPI, Debit Card, Net Banking, Cash |
| **Top Customers Table** | Top 10 high-value repeat buyers |
| **Business Insights** | 6 auto-generated English-language strategic recommendations |
| **CSV Upload** | Upload and validate your own retail dataset |
| **Filtered CSV Export** | Download currently filtered data as CSV |
| **Project Information** | Full documentation + College Viva Q&A guide |

---

## 💻 Technology Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core language |
| **MongoDB Atlas / PyMongo** | Cloud NoSQL database for transaction storage and queries |
| **Pandas** | Data manipulation, cleaning, aggregation |
| **NumPy** | Numerical computation |
| **Streamlit** | Interactive web dashboard |
| **Plotly Express & Graph Objects** | Interactive charts with hover, zoom, tooltips |
| **Matplotlib & Seaborn** | Academic-grade static visualizations |
| **CSV** | Offline fallback & dataset upload/export |

---

## 📊 Dataset Description

The project ships with an auto-generated synthetic retail transaction dataset (`data/retail_sales.csv`) containing **2,500 records** spanning 12 months (Jan–Dec 2024), fully synced with MongoDB.

### Schema

| Column | Type | Description |
|--------|------|-------------|
| `Transaction_ID` | String | Unique transaction identifier (e.g. `TXN-100234`) |
| `Transaction_Date` | Date | Date of transaction (`YYYY-MM-DD`) |
| `Customer_ID` | String | Unique customer identifier (e.g. `CUST-1042`) |
| `Gender` | Categorical | `Female`, `Male`, `Other` |
| `Age` | Integer | Customer age (18–72) |
| `Product_Category` | Categorical | `Electronics`, `Clothing & Apparel`, `Home & Kitchen`, `Beauty & Personal Care`, `Books & Stationery`, `Sports & Fitness` |
| `Product_Name` | String | Specific product item name |
| `Quantity` | Integer | Units purchased (1–5) |
| `Unit_Price` | Float | Price per unit ($) |
| `Total_Amount` | Float | `Quantity × Unit_Price` (auto-calculated, validated) |
| `Payment_Method` | Categorical | `Credit Card`, `Debit Card`, `UPI`, `Net Banking`, `Cash` |
| `City` | Categorical | `New York`, `Los Angeles`, `Chicago`, `Houston`, `Seattle`, `Austin`, `Miami`, `San Francisco` |

> **Note on Revenue vs Profit:** The dataset records gross sales revenue. Because wholesale acquisition costs are not tracked, figures represent **Total Revenue**, not net accounting profit.

---

## 📁 Project Structure

```
retail-sales-analytics-dashboard/
│
├── app.py                  # Main Streamlit web dashboard (MongoDB integrated)
├── db.py                   # MongoDB Atlas / local connection & querying module
├── seed_mongo.py           # CLI script to upload/seed CSV data into MongoDB
├── analysis.py             # Data validation, KPIs, aggregations, insights engine
├── data_generator.py       # Synthetic dataset generator (2,500+ records)
├── test_app.py             # Automated unit test suite (17 tests)
├── verify_kpis.py          # KPI and calculation verification script
├── requirements.txt        # Python dependencies (includes pymongo, certifi, python-dotenv)
├── .env.example            # Example MongoDB environment variable configuration
├── README.md               # Project documentation
└── data/
    └── retail_sales.csv    # Default sample dataset (auto-generated on first run)
```

---

## 🚀 Installation & Running Locally

### Prerequisites
- Python 3.10 or higher
- pip package manager
- (Optional) A free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster or local MongoDB instance

### Step 1: Clone the Repository
```bash
git clone https://github.com/nikhilkumarnayak364-lang/analysis-.git
cd analysis-
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure MongoDB (Atlas or Local)
Copy `.env.example` to `.env` and fill in your connection string:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=retail_db
MONGODB_COLLECTION_NAME=sales_transactions
```
*(Alternatively, you can paste your MongoDB Atlas URI directly in the Streamlit sidebar settings).*

### Step 4: Seed Data into MongoDB
```bash
python seed_mongo.py --drop
```

### Step 5: Launch the Dashboard
```bash
python -m streamlit run app.py
```
*(or `streamlit run app.py` if Python Scripts is on your PATH)*

### Step 5: Open in Browser
```
http://localhost:8501
```

---

## 🧪 Running Tests

```bash
python -m unittest test_app.py -v
```

**14 tests covering:**
- Dataset row count (≥ 1,000 rows)
- All 12 required schema columns
- Mathematical consistency: `Total_Amount == Quantity × Unit_Price`
- Duplicate pruning and corrupted data correction
- KPI calculations and zero-division safety
- Monthly, daily, and day-of-week trend aggregations
- Category, product, demographic, geographic, and payment analyses
- Filter functionality and empty result safety
- Automated business insight generation

---

## 📈 Key Analyses Implemented

1. **Revenue & Volume Tracking** — Total Gross Revenue, Transaction Count, Units Sold
2. **Average Order Value (AOV)** — Mean spend per customer transaction
3. **Best-Selling Products** — Top 10 by volume and by revenue
4. **Category Revenue Analysis** — Share %, avg unit price, order count
5. **Temporal Trends** — Monthly trajectory, daily fluctuation, day-of-week patterns
6. **Customer Demographics** — Age bracket bins, gender distribution, cross-tab heatmap
7. **Geographic Comparison** — City-wise revenue, orders, and AOV
8. **Payment Method Preferences** — Transaction share by payment channel
9. **High-Value Customer Profiling** — Top 10 repeat buyers by cumulative spend
10. **Automated Business Insights** — 6 dynamic, context-aware strategic recommendations

---

## ⚠️ Limitations

- Does not calculate net profit (no wholesale COGS data in the transaction log)
- Flat CSV storage is suitable for datasets up to ~500,000 rows
- No user authentication or multi-user session management

---

## 🔮 Future Scope

- **Predictive Forecasting** — Seasonal demand forecasting using Prophet/ARIMA
- **Customer Segmentation** — K-Means clustering on RFM (Recency, Frequency, Monetary)
- **Market Basket Analysis** — Association rule mining (Apriori algorithm)
- **Database Integration** — PostgreSQL or BigQuery for enterprise-scale data
- **Streamlit Cloud Deployment** — One-click public sharing

---

## 👨‍💻 Author

**Nikhil Kumar Nayak**  
📧 nikhilkumarnayak364@gmail.com

---

## 📄 License

This project is created for academic purposes.
