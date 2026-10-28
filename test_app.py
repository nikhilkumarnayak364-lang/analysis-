"""
test_app.py
-----------
Automated test suite to verify data generation, data cleaning, validation,
KPI calculations, trend aggregations, demographic cross-tabs, and edge cases.
"""

import unittest
import pandas as pd
import numpy as np

import data_generator
import analysis
import db


class TestRetailAnalytics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate small reproducible dataset for test suite
        cls.raw_df = data_generator.generate_retail_data(num_records=1200, random_seed=99)
        cls.clean_df, cls.warnings = analysis.validate_and_clean_data(cls.raw_df)

    def test_data_generation_row_count(self):
        """Test dataset has at least 1000 rows as required."""
        self.assertGreaterEqual(len(self.raw_df), 1000)

    def test_required_columns_exist(self):
        """Test all 12 mandatory columns are present."""
        for col in analysis.REQUIRED_COLUMNS:
            self.assertIn(col, self.clean_df.columns)

    def test_total_amount_consistency(self):
        """Verify Total_Amount == Quantity * Unit_Price (within float precision)."""
        expected = (self.clean_df["Quantity"] * self.clean_df["Unit_Price"]).round(2)
        diff = (self.clean_df["Total_Amount"] - expected).abs()
        self.assertTrue((diff < 0.05).all(), "Total_Amount does not match Quantity * Unit_Price")

    def test_validation_missing_columns(self):
        """Ensure validation raises ValueError when required column is missing."""
        invalid_df = self.raw_df.drop(columns=["Customer_ID"])
        with self.assertRaises(ValueError):
            analysis.validate_and_clean_data(invalid_df)

    def test_validation_corrupted_data_correction(self):
        """Verify cleaning corrects faulty Total_Amount and filters invalid rows."""
        corrupted = self.raw_df.head(50).copy()
        # introduce inconsistent Total_Amount
        corrupted.loc[0, "Total_Amount"] = 9999.99
        # introduce duplicate transaction ID
        corrupted.loc[1, "Transaction_ID"] = corrupted.loc[2, "Transaction_ID"]

        cleaned, warnings = analysis.validate_and_clean_data(corrupted)
        self.assertEqual(len(cleaned), 49)  # one duplicate dropped
        # Total_Amount should be recalculated
        expected_first = round(cleaned.iloc[0]["Quantity"] * cleaned.iloc[0]["Unit_Price"], 2)
        self.assertAlmostEqual(cleaned.iloc[0]["Total_Amount"], expected_first, places=2)

    def test_kpi_calculations_non_empty(self):
        """Verify KPI computations on regular data."""
        kpis = analysis.calculate_kpis(self.clean_df)
        self.assertGreater(kpis["total_revenue"], 0)
        self.assertEqual(kpis["total_transactions"], len(self.clean_df))
        self.assertGreater(kpis["average_order_value"], 0)
        self.assertGreater(kpis["total_units_sold"], 0)
        self.assertGreater(kpis["unique_customers"], 0)

    def test_kpi_empty_dataframe_safety(self):
        """Verify empty DataFrame does not crash or raise ZeroDivisionError."""
        empty_df = pd.DataFrame(columns=self.clean_df.columns)
        kpis = analysis.calculate_kpis(empty_df)
        self.assertEqual(kpis["total_revenue"], 0.0)
        self.assertEqual(kpis["total_transactions"], 0)
        self.assertEqual(kpis["average_order_value"], 0.0)

    def test_monthly_and_daily_trends(self):
        """Verify temporal aggregations."""
        monthly = analysis.get_monthly_sales_trend(self.clean_df)
        self.assertFalse(monthly.empty)
        self.assertIn("YearMonth", monthly.columns)
        self.assertIn("Total_Revenue", monthly.columns)

        daily = analysis.get_daily_sales_trend(self.clean_df)
        self.assertFalse(daily.empty)
        self.assertIn("Date", daily.columns)

        dow = analysis.get_day_of_week_analysis(self.clean_df)
        self.assertEqual(len(dow), 7)

    def test_category_and_product_rankings(self):
        """Verify product category analysis and revenue sum."""
        cat_df = analysis.get_category_performance(self.clean_df)
        self.assertFalse(cat_df.empty)
        # Sum of category revenues should equal total revenue
        self.assertAlmostEqual(cat_df["Total_Revenue"].sum(), self.clean_df["Total_Amount"].sum(), places=1)

        top_by_qty = analysis.get_top_selling_products(self.clean_df, top_n=5, by="Quantity")
        self.assertEqual(len(top_by_qty), 5)
        top_by_rev = analysis.get_top_selling_products(self.clean_df, top_n=5, by="Total_Amount")
        self.assertEqual(len(top_by_rev), 5)

    def test_demographic_analysis(self):
        """Verify customer demographics and cross-tabulation."""
        demo = analysis.get_customer_demographics(self.clean_df)
        self.assertIn("gender_summary", demo)
        self.assertIn("age_summary", demo)
        self.assertIn("cross_tab", demo)
        self.assertFalse(demo["gender_summary"].empty)
        self.assertFalse(demo["age_summary"].empty)
        self.assertFalse(demo["cross_tab"].empty)

    def test_geographic_and_payment_distribution(self):
        """Verify city-wise and payment method aggregations."""
        cities = analysis.get_city_performance(self.clean_df)
        self.assertFalse(cities.empty)
        self.assertIn("City", cities.columns)

        payments = analysis.get_payment_method_distribution(self.clean_df)
        self.assertFalse(payments.empty)
        self.assertAlmostEqual(payments["Txn_Share_Pct"].sum(), 100.0, places=1)

    def test_top_customers(self):
        """Verify high-value customer detection."""
        top_custs = analysis.get_top_customers(self.clean_df, top_n=10)
        self.assertLessEqual(len(top_custs), 10)
        # Check order descending by spend
        spends = top_custs["Total_Spend"].tolist()
        self.assertEqual(spends, sorted(spends, reverse=True))

    def test_dynamic_insights_generation(self):
        """Verify automated business insights generator returns valid English recommendations."""
        insights = analysis.generate_business_insights(self.clean_df)
        self.assertIsInstance(insights, list)
        self.assertGreaterEqual(len(insights), 3)
        for ins in insights:
            self.assertIn("title", ins)
            self.assertIn("insight", ins)
            self.assertIn("badge", ins)
            self.assertGreater(len(ins["insight"]), 20)

    def test_filter_functionality(self):
        """Verify filtering by category, city, and empty results handling."""
        # Filter by single category
        sample_cat = self.clean_df["Product_Category"].iloc[0]
        filtered = analysis.apply_filters(self.clean_df, categories=[sample_cat])
        self.assertTrue((filtered["Product_Category"] == sample_cat).all())

        # Filter resulting in empty DataFrame
        empty_res = analysis.apply_filters(self.clean_df, cities=["NonExistentCity"])
        self.assertTrue(empty_res.empty)
        # Empty result should still safely pass through all analytical functions
        empty_kpi = analysis.calculate_kpis(empty_res)
        self.assertEqual(empty_kpi["total_revenue"], 0.0)
        empty_insights = analysis.generate_business_insights(empty_res)
        self.assertEqual(len(empty_insights), 1)

    def test_db_defaults(self):
        """Verify MongoDB default database and collection names."""
        self.assertEqual(db.DEFAULT_DB_NAME, "retail_db")
        self.assertEqual(db.DEFAULT_COLLECTION_NAME, "sales_transactions")

    def test_db_client_uri_validation(self):
        """Verify client creation raises ValueError when URI is empty."""
        with self.assertRaises(ValueError):
            db.get_mongo_client(uri="")

    def test_db_test_connection_invalid_host(self):
        """Verify test_connection returns (False, msg) gracefully on non-existent cluster."""
        success, msg = db.test_connection(uri="mongodb://invalid.nonexistent.cluster:27017/?connectTimeoutMS=500")
        self.assertFalse(success)
        self.assertIsInstance(msg, str)


if __name__ == "__main__":
    unittest.main()
