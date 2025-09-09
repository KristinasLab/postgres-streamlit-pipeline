import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = int(os.environ.get("DB_PORT"))
db_name = os.environ.get("DB_NAME")

# Connect to PostgreSQL
engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# Paths to CSVs
data_dir = os.path.join(os.getcwd(), "data")  # inside container: /app/data

company_file = os.path.join(data_dir, "companies.csv")
headcount_file = os.path.join(data_dir, "headcount.csv")
revenue_file = os.path.join(data_dir, "revenue.csv")
dim_date_file = os.path.join(data_dir, "dim_date.csv")

# Check CSV existence
for file in [company_file, headcount_file, revenue_file, dim_date_file]:
    if not os.path.exists(file):
        print(f"Missing CSV file: {file}. Exiting.")
        exit(1)

# Load CSVs
company_df = pd.read_csv(company_file)
headcount_df = pd.read_csv(headcount_file)
revenue_df = pd.read_csv(revenue_file)
dim_date_df = pd.read_csv(dim_date_file)

# Convert 'month' columns to date format
headcount_df["month"] = pd.to_datetime(headcount_df["month"]).dt.date
revenue_df["month"] = pd.to_datetime(revenue_df["month"]).dt.date
dim_date_df["month"] = pd.to_datetime(dim_date_df["month"]).dt.date

# Create tables if they don't exist
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS fact_revenue"))
    conn.execute(text("DROP TABLE IF EXISTS fact_headcount"))
    conn.execute(text("DROP TABLE IF EXISTS dim_date"))
    conn.execute(text("DROP TABLE IF EXISTS dim_company"))
    
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS dim_company (
        company_id INTEGER PRIMARY KEY,
        company_name TEXT,
        location TEXT,
        industry TEXT
    );
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS dim_date (
        month_id INTEGER, 
        month_num INTEGER,
        year INTEGER,
        quarter INTEGER,
        month_name TEXT,
        month DATE PRIMARY KEY
    );
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS fact_revenue (
        id INTEGER PRIMARY KEY,
        company_id INTEGER REFERENCES dim_company(company_id),
        month DATE REFERENCES dim_date(month),
        revenue_eur NUMERIC
    );
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS fact_headcount (
        id INTEGER PRIMARY KEY,
        company_id INTEGER REFERENCES dim_company(company_id),
        month DATE REFERENCES dim_date(month),
        employee_count INTEGER
    );
    """))

# Load data into tables in correct order
# Load data into tables in correct order
company_df.to_sql("dim_company", engine, if_exists="append", index=False, method="multi") #replace would drop previously definde dataframe and use the one from the csv
dim_date_df.to_sql("dim_date", engine, if_exists="append", index=False, method="multi")

revenue_df.to_sql("fact_revenue", engine, if_exists="append", index=False, method="multi")
headcount_df.to_sql("fact_headcount", engine, if_exists="append", index=False, method="multi")

# Debug
with engine.begin() as conn:
    print("dim_company rows:", conn.execute(text("SELECT COUNT(*) FROM dim_company")).scalar())
    print("fact_headcount rows (attempted):", len(headcount_df))

print("ETL complete!")