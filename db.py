"""
db.py
-----
MongoDB client and data management layer for Retail Analytics.
Supports both MongoDB Atlas (mongodb+srv://) and local MongoDB (mongodb://localhost:27017).
Handles connection configuration via .env, Streamlit secrets, or explicit parameters.
"""

import os
from typing import Optional, Tuple, Dict, Any
import pandas as pd
import certifi
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

DEFAULT_DB_NAME = "retail_db"
DEFAULT_COLLECTION_NAME = "sales_transactions"


def get_connection_uri() -> str:
    """
    Retrieves the MongoDB connection URI from environment or Streamlit secrets.
    Falls back to local MongoDB default if not provided.
    """
    # 1. Check Streamlit secrets if running inside Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "MONGODB_URI" in st.secrets:
            return st.secrets["MONGODB_URI"]
    except Exception:
        pass

    # 2. Check environment variable
    return os.getenv("MONGODB_URI", "")


def get_db_name() -> str:
    """Retrieves target database name."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "MONGODB_DB_NAME" in st.secrets:
            return st.secrets["MONGODB_DB_NAME"]
    except Exception:
        pass
    return os.getenv("MONGODB_DB_NAME", DEFAULT_DB_NAME)


def get_collection_name() -> str:
    """Retrieves target collection name."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "MONGODB_COLLECTION_NAME" in st.secrets:
            return st.secrets["MONGODB_COLLECTION_NAME"]
    except Exception:
        pass
    return os.getenv("MONGODB_COLLECTION_NAME", DEFAULT_COLLECTION_NAME)


def get_mongo_client(uri: Optional[str] = None, timeout_ms: int = 10000):
    """
    Creates and returns a MongoClient instance configured with SSL certificates
    and resilient read preference for replica set clusters.
    """
    from pymongo import MongoClient
    from pymongo.read_preferences import ReadPreference

    connection_uri = get_connection_uri() if uri is None else uri
    if not connection_uri:
        raise ValueError("MongoDB URI is not set. Please specify MONGODB_URI in .env or Streamlit secrets.")

    kwargs: Dict[str, Any] = {
        "serverSelectionTimeoutMS": timeout_ms,
        "connectTimeoutMS": 10000,
        "socketTimeoutMS": 30000,
        "read_preference": ReadPreference.PRIMARY_PREFERRED,
    }

    if "mongodb+srv" in connection_uri or "ssl=true" in connection_uri.lower():
        kwargs["tlsCAFile"] = certifi.where()

    client = MongoClient(connection_uri, **kwargs)
    return client


def test_connection(uri: Optional[str] = None) -> Tuple[bool, str]:
    """
    Pings MongoDB to verify that the credentials and network connection work.
    Returns (success, message).
    """
    try:
        with get_mongo_client(uri=uri, timeout_ms=8000) as client:
            client.admin.command("ping")
        return True, "Successfully connected to MongoDB."
    except Exception as e:
        return False, str(e)


def fetch_transactions(
    uri: Optional[str] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """
    Queries and retrieves retail transactions from MongoDB as a Pandas DataFrame.
    Excludes the MongoDB internal '_id' field from results.
    Optionally limits the number of documents returned.
    """
    target_uri = uri or get_connection_uri()
    target_db = db_name or get_db_name()
    target_col = collection_name or get_collection_name()

    with get_mongo_client(uri=target_uri) as client:
        col = client[target_db][target_col]
        cursor = col.find({}, {"_id": 0}).batch_size(1000)
        if limit and limit > 0:
            cursor = cursor.limit(limit)
        records = list(cursor)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    return df


def insert_transactions(
    df: pd.DataFrame,
    uri: Optional[str] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    drop_existing: bool = False,
) -> int:
    """
    Seeds a DataFrame into the target MongoDB collection.
    Optionally drops the existing collection first.
    Returns count of inserted documents.
    """
    if df.empty:
        return 0

    target_uri = uri or get_connection_uri()
    target_db = db_name or get_db_name()
    target_col = collection_name or get_collection_name()

    with get_mongo_client(uri=target_uri) as client:
        db = client[target_db]
        col = db[target_col]

        if drop_existing:
            col.drop()

        # Convert timestamps/dates to strings and categories to strings for clean BSON storage
        import datetime as dt
        upload_df = df.copy()
        for col_name in upload_df.columns:
            if str(upload_df[col_name].dtype) == "category":
                upload_df[col_name] = upload_df[col_name].astype(str)
            elif pd.api.types.is_datetime64_any_dtype(upload_df[col_name]):
                upload_df[col_name] = upload_df[col_name].dt.strftime("%Y-%m-%d")
            elif upload_df[col_name].dtype == object:
                upload_df[col_name] = upload_df[col_name].apply(
                    lambda v: v.strftime("%Y-%m-%d") if isinstance(v, (dt.date, dt.datetime)) else v
                )

        records = upload_df.to_dict(orient="records")
        result = col.insert_many(records)

        # Create common indexes for analytical query acceleration
        try:
            col.create_index("Transaction_ID", unique=True)
            col.create_index("Transaction_Date")
            col.create_index("Product_Category")
            col.create_index("City")
        except Exception:
            pass

        return len(result.inserted_ids)


def get_collection_stats(
    uri: Optional[str] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns document count and basic metadata from the target collection.
    """
    target_uri = uri or get_connection_uri()
    target_db = db_name or get_db_name()
    target_col = collection_name or get_collection_name()

    try:
        with get_mongo_client(uri=target_uri) as client:
            col = client[target_db][target_col]
            count = col.estimated_document_count()
        return {
            "status": "connected",
            "database": target_db,
            "collection": target_col,
            "document_count": count,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database": target_db,
            "collection": target_col,
            "document_count": 0,
        }
