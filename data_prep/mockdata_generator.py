import pandas as pd
import numpy as np

# Setup
companies = [
    (1, "Alpha GmbH", "Berlin", "Arbeitsschutz"),
    (2, "Beta AG", "München", "Arbeitssicherheit"),
    (3, "Gamma SE", "Hamburg", "Arbeitspsychologie"),
    (4, "Delta Ltd", "Frankfurt", "Umweltschutz"),
    (5, "Epsilon GmbH", "Stuttgart", "Arbeitsschutz")
]

# Zeitachse (24 Monate)
months = pd.date_range("2024-01-01", "2025-12-01", freq="MS").strftime("%Y-%m-%d").tolist()

# companies.csv
df_companies = pd.DataFrame(companies, columns=["company_id","company_name","location","industry"])
df_companies.to_csv("companies.csv", index=False)

# revenue.csv & headcount.csv
revenue_records, headcount_records = [], []
rng = np.random.default_rng(seed=42)

row_id = 1  # Initialize row_id before loops

for cid, _, _, _ in companies:
    base_revenue = rng.integers(200000, 600000)  # Grundumsatz
    base_employees = rng.integers(5, 50)       # Grundbelegschaft
    for m in months:
        rev = int(base_revenue * rng.uniform(0.9, 1.1))  # leichte Schwankung
        emp = int(base_employees * rng.uniform(0.95, 1.05))
        revenue_records.append([row_id, cid, m, rev])
        headcount_records.append([row_id, cid, m, emp])
        row_id += 1  # Increment ID

pd.DataFrame(revenue_records, columns=["id", "company_id","month","revenue_eur"]).to_csv("revenue.csv", index=False)
pd.DataFrame(headcount_records, columns=["id", "company_id","month","employee_count"]).to_csv("headcount.csv", index=False)
