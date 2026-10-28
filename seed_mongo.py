"""
seed_mongo.py
-------------
CLI utility to upload/seed the retail sales dataset into MongoDB.
Usage:
    python seed_mongo.py [--uri "mongodb+srv://..."] [--file "data/retail_sales.csv"] [--drop]
"""

import argparse
import os
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import data_generator
import analysis
import db


def main():
    parser = argparse.ArgumentParser(description="Seed retail sales dataset into MongoDB.")
    parser.add_argument("--uri", type=str, default="", help="MongoDB connection URI (overrides .env / secrets)")
    parser.add_argument("--file", type=str, default="data/retail_sales.csv", help="Path to CSV dataset")
    parser.add_argument("--db", type=str, default=db.DEFAULT_DB_NAME, help="Target MongoDB database name")
    parser.add_argument("--collection", type=str, default=db.DEFAULT_COLLECTION_NAME, help="Target collection name")
    parser.add_argument("--drop", action="store_true", help="Drop existing collection before seeding")
    parser.add_argument("--records", type=int, default=2500, help="Number of records to generate if file missing")
    args = parser.parse_args()

    mongo_uri = args.uri or db.get_connection_uri()
    if not mongo_uri:
        print("[ERROR] MongoDB connection URI is required.")
        print("Please provide --uri or define MONGODB_URI in your .env or .streamlit/secrets.toml file.")
        sys.exit(1)

    print("[INFO] Testing connection to MongoDB Atlas...")
    ok, msg = db.test_connection(uri=mongo_uri)
    if not ok:
        print(f"[ERROR] Connection failed: {msg}")
        sys.exit(1)
    print("[SUCCESS] Connection successful!")

    # Check or generate CSV
    if not os.path.exists(args.file):
        print(f"[INFO] File '{args.file}' not found. Generating {args.records} sample records...")
        os.makedirs(os.path.dirname(args.file) or ".", exist_ok=True)
        raw_df = data_generator.generate_retail_data(num_records=args.records)
        raw_df.to_csv(args.file, index=False)
    else:
        print(f"[INFO] Reading transactions from '{args.file}'...")
        raw_df = pd.read_csv(args.file)

    clean_df, warnings = analysis.validate_and_clean_data(raw_df)
    if warnings:
        print("[WARNING] Validation notices:")
        for w in warnings:
            print(f"   - {w}")

    print(f"[INFO] Inserting {len(clean_df)} documents into '{args.db}.{args.collection}' (drop_existing={args.drop})...")
    inserted_count = db.insert_transactions(
        clean_df,
        uri=mongo_uri,
        db_name=args.db,
        collection_name=args.collection,
        drop_existing=args.drop,
    )
    print(f"[SUCCESS] Successfully inserted {inserted_count} transactions into MongoDB Atlas!")

    stats = db.get_collection_stats(uri=mongo_uri, db_name=args.db, collection_name=args.collection)
    print(f"[STATUS] Current Collection Status: {stats}")


if __name__ == "__main__":
    main()
