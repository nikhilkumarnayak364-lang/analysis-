import pandas as pd
import analysis

df = pd.read_csv('data/retail_sales.csv')
clean, warnings = analysis.validate_and_clean_data(df)
print('Raw rows:', len(df), '| Clean rows:', len(clean))
print('Warnings:', warnings)

kpis = analysis.calculate_kpis(clean)
total_revenue = kpis['total_revenue']
total_txns = kpis['total_transactions']
aov = kpis['average_order_value']
total_units = kpis['total_units_sold']
unique_custs = kpis['unique_customers']

print('---- KPI CHECK ----')
print('Total Revenue:     $' + f'{total_revenue:,.2f}')
print('Total Transactions:', total_txns)
print('Average Order Value: $' + f'{aov:.2f}')
print('Total Units Sold:  ', total_units)
print('Unique Customers:  ', unique_custs)

# Cross-check: sum of Total_Amount == reported revenue
manual_sum = round(float(clean['Total_Amount'].sum()), 2)
print('Manual sum of Total_Amount: $' + f'{manual_sum:,.2f}')
print('Revenue match:', manual_sum == total_revenue)

# Verify Total_Amount = Qty * Unit_Price
expected = (clean['Quantity'] * clean['Unit_Price']).round(2)
diff = (clean['Total_Amount'] - expected).abs()
print('Max discrepancy in Total_Amount:', round(float(diff.max()), 6))
print('Rows with discrepancy > 0.01:', int((diff > 0.01).sum()))

# Check months
print('Months covered:', clean['YearMonth'].nunique())
print('Date range:', str(clean['Transaction_Date'].min().date()), '->', str(clean['Transaction_Date'].max().date()))

# Categories, cities, payments
print('Categories:', sorted(clean['Product_Category'].unique().tolist()))
print('Cities:', sorted(clean['City'].unique().tolist()))
print('Payments:', sorted(clean['Payment_Method'].unique().tolist()))

# Filter test
filtered = analysis.apply_filters(clean, categories=['Electronics'], cities=['New York'])
kpis2 = analysis.calculate_kpis(filtered)
print('---- FILTER TEST (Electronics + New York) ----')
print('Filtered Revenue: $' + f'{kpis2["total_revenue"]:,.2f}')
print('Filtered Txns:', kpis2['total_transactions'])
print('Rows in filter match:', len(filtered))

# Empty filter safety
empty_f = analysis.apply_filters(clean, cities=['NonExistentXYZ'])
kpis3 = analysis.calculate_kpis(empty_f)
print('---- EMPTY FILTER SAFETY ----')
print('Empty filter revenue:', kpis3['total_revenue'], '(expected 0.0)')
print('Empty filter txns:', kpis3['total_transactions'], '(expected 0)')

# Top products
top3 = analysis.get_top_selling_products(clean, top_n=3, by='Quantity')
print('---- TOP 3 PRODUCTS (by Qty) ----')
for _, r in top3.iterrows():
    print(' ', r['Product_Name'], '- Qty:', r['Quantity_Sold'], '- Rev: $' + f'{r["Total_Revenue"]:,.2f}')

# Payment distribution
pay = analysis.get_payment_method_distribution(clean)
print('---- PAYMENT DISTRIBUTION ----')
for _, r in pay.iterrows():
    print(' ', r['Payment_Method'], '-', r['Txn_Share_Pct'], '%')

print('ALL CHECKS PASSED')
