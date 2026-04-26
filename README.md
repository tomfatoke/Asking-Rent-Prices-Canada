# Asking Rent Price Prediction

## Project Overview
This project analyzes and predicts Canadian asking rent prices using
experimental estimates published by Statistics Canada. The data covers
average asking rent by rental unit type, number of bedrooms, and
geography across major Canadian cities from 2019 onwards.

The pipeline is built entirely on Databricks using the Medallion
Architecture pattern, with analysis and natural language querying
powered by Databricks Genie.

---

## Data Source
- **Publisher:** Statistics Canada
- **Dataset:** Asking rent prices, by rental unit type and number
  of bedrooms, experimental estimates
- **Format:** CSV
- **Last Updated:** March 11, 2026
- **URL:** https://www150.statcan.gc.ca/n1/tbl/csv/46100092-eng.zip

---

## Tech Stack
| Tool | Purpose |
|---|---|
| **Databricks** | Primary data platform |
| **Apache Spark** | Distributed data processing |
| **Delta Lake** | Storage layer for all tables |
| **Unity Catalog** | Data governance and table management |
| **Databricks Genie** | Natural language querying and analysis |
| **GitHub** | Version control |

---

## Architecture — Medallion Pattern  

---

## Bronze Layer — Complete ✅
The bronze layer is responsible for ingesting the raw Statistics Canada
CSV file exactly as received, with no transformations or cleaning applied.

### What was done:
- Connected Databricks to a Unity Catalog Volume containing the raw CSV
- Read the CSV into a Spark DataFrame using spark.read with header
  and inferSchema options
- Inspected the raw schema to identify all 16 original StatCan columns
  and their data types
- Added ingestion metadata columns:
  - ingestion_timestamp: records when the data was loaded
  - source_file: records the file path the data came from
- Wrote all 8,188 rows as-is to a Delta table with no columns dropped
  or modified

### Bronze Delta Table
`rent_project.rent_raw_data.bronze_rent_raw`

### Raw Schema
| Column | Data Type | Description |
|---|---|---|
| REF_DATE | date | Reference period |
| GEO | string | City and province |
| DGUID | string | StatCan geographic ID |
| Rental unit type | string | Unit type and bedroom count |
| Estimates | string | Estimate type |
| UOM | string | Unit of measure |
| UOM_ID | integer | Unit of measure ID |
| SCALAR_FACTOR | string | Scaling metadata |
| SCALAR_ID | integer | Scalar ID |
| VECTOR | string | StatCan series ID |
| COORDINATE | string | StatCan coordinate |
| VALUE | integer | Average asking rent |
| STATUS | string | Data quality flag |
| SYMBOL | string | Symbol field |
| TERMINATED | string | Series termination flag |
| DECIMALS | integer | Decimal places metadata |

---
Silver Layer 
The silver layer reads from the bronze Delta table and applies all
cleaning and transformation logic to produce a structured, analysis
ready dataset.

### What Was Done

**1. Read from Bronze**
- Read directly from the bronze Delta table
- Never touched the original CSV again

**2. Column Selection**
- Selected only the 4 relevant columns from the original 16:
  - REF_DATE, GEO, Rental_unit_type, VALUE
- Dropped all StatCan metadata columns that added no analytical value

**3. NULL Removal**
- Dropped all rows where VALUE (asking rent) was NULL
- These represented city and unit type combinations where
  StatCan had no data for that period
- Row count reduced from 8,188 to a smaller clean dataset

**4. GEO Column Cleaning**
- Stripped the Census Metropolitan Area descriptor from city names
  - e.g. "St. John's, Census metropolitan area (CMA)" → "St. John's"
- Used split() on the comma and took only the first part
- Applied trim() to remove leftover whitespace
- Renamed column from GEO to City

**5. Rental Unit Type Splitting**
- Split the Rental_unit_type column into two separate columns
  on the " - " delimiter:
  - Unit_type → e.g. Apartment, House, Room
  - Bedrooms  → e.g. 1 bedroom, 2 bedrooms, N/A
- Handled the "Room" exception using when/otherwise:
  - Room has no bedroom count so Bedrooms was set to "N/A"
- Dropped the original Rental_unit_type column

**6. Column Renaming and Casting**
- Renamed REF_DATE → Reference_Date
- Renamed VALUE → Asking_rent
- Cast Asking_rent from integer to float to support
  decimal precision in gold layer averages

### Final Silver Schema
| Column | Data Type | Description |
|---|---|---|
| Reference_Date | date | Reference period |
| City | string | Cleaned city name |
| Unit_type | string | Type of rental unit |
| Bedrooms | string | Number of bedrooms |
| Asking_rent | float | Average asking rent in dollars |

### Silver Delta Table
`projects.rent_project.silver_rent_clea
## Current Status
- [x] GitHub repository created
- [x] Databricks Git folder connected
- [x] Raw CSV uploaded to Databricks Volume
- [x] Bronze layer complete — 8,188 rows ingested
- [x] Silver layer in progress
- [ ] Gold layer pending
- [ ] ML prediction model pending
- [ ] Genie setup pending

---

## Author
GitHub: your-github-tomfatoke
