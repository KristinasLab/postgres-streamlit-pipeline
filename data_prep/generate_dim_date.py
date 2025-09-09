import pandas as pd

# Generate monthly date dimension for 2 years (or any range)
start_date = "2024-01-01"
end_date = "2025-12-01"

dates = pd.date_range(start=start_date, end=end_date, freq="MS")  # Month Start

# Build dim_date DataFrame
df_date = pd.DataFrame({
    "month_num": dates.month,
    "year": dates.year,
    "quarter": dates.quarter,
    "month_name": dates.strftime("%B"),
    "month": dates.strftime("%Y-%m-%d")
})

# To make 'month' unique (primary key), you can use year*100 + month
df_date["month_id"] = df_date["year"] * 100 + df_date["month_num"]
df_date = df_date[["month_id","month_num","year","quarter","month_name","month"]]

# Save to CSV
df_date.to_csv("dim_date.csv", index=False)
print("dim_date.csv generated successfully!")
