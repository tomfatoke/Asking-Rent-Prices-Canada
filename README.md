# Asking Rent Price Analysis

## Project Overview
This project analyzes Canadian asking rent prices using
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
## Silver Layer — Complete ✅
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
`projects.rent_project.silver_rent_layer

---

## Gold Layer — Complete ✅
The gold layer reads from the silver Delta table and produces a fully
aggregated, analysis ready dataset with year over year rent change
calculations. This is the layer that powers SQL analysis and Genie
querying.

### What Was Done

**1. Read from Silver**
- Read directly from the silver Delta table
- Never touched bronze or the original CSV

**2. Date Extraction**
- Extracted Year and Month from Reference_Date
- Dropped the full Reference_Date column after extraction
- Discovered data is published quarterly by Statistics Canada:
  - January, April, July, October each year

**3. Aggregation**
- Grouped by: Year, Month, City, Unit_type, Bedrooms
- Calculated the following aggregations:
  - avg_asking_rent  →  average asking rent rounded to 2 decimals
  - max_asking_rent  →  highest rent in the group
  - min_asking_rent  →  lowest rent in the group
  - Total_listings   →  number of records in the group

**4. Year Over Year Percentage Change**
- Defined a Window partitioned by City, Unit_type, Bedrooms
- Ordered by Year and Month within each partition
- Used lag() with offset of 4 to look back one full year
  (offset of 4 because data is quarterly — 4 quarters = 1 year)
- Calculated YOY_pct_change:
  ((current avg - previous avg) / previous avg) * 100
- First year (2019) shows NULL for YOY — expected and correct
  as there is no previous year to compare against

### Final Gold Schema
| Column | Data Type | Description |
|---|---|---|
| Year | integer | Year of the reference period |
| Month | integer | Quarter month (1, 4, 7, 10) |
| City | string | Cleaned city name |
| Unit_type | string | Type of rental unit |
| Bedrooms | string | Number of bedrooms |
| avg_asking_rent | float | Average asking rent |
| max_asking_rent | float | Maximum asking rent |
| min_asking_rent | float | Minimum asking rent |
| Total_listings | integer | Number of records in group |
| prev_year_rent | float | Same quarter previous year rent |
| YOY_pct_change | float | Year over year % change in rent |

### Gold Delta Table
`projects.rent_project.gold_rent_aggregated`
- Total rows: 6,142

---

## Current Status
- [x] GitHub repository created
- [x] Databricks Git folder connected
- [x] Raw CSV uploaded to Databricks Volume
- [x] Bronze layer complete - 8,188 rows ingested
- [x] Silver layer complete - Cleaned and Transformed
- [x] Gold layer complete - 6142 rows
- [x] Genie setup complete

---
## Dashboard

The dashboard was built in Databricks AI/BI and connects
directly to the gold Delta table. All visualizations were
generated using Databricks Genie natural language querying.

---

### National Average Rent (2025)
![National Average Rent](images/National%20Average%20Rent%20(2025).png)
The national average asking rent in Canada for 2025 is $1,766.

---

### Most Expensive City
![Most Expensive City](images/Most%20Expensive%20City_%20Vancouver.png)
Vancouver has the highest overall average rent among all
Canadian cities in the dataset.

---

### Most Affordable City
![Most Affordable City](images/Most%20Affordable%20City_%20Saguenay.png)
Saguenay is the most affordable city in Canada based on
average asking rent.

---

### Highest Rent Increase Since 2019
![Highest Rent Increase](images/Highest%20Rent%20Increase_%20Trois-Rivières.png)
Trois-Rivières has experienced the largest rent increase
since 2019 among all cities in the dataset.

---

### Cities by Rent Increase Since 2019
![Cities by Rent Increase](images/Cities%20by%20Rent%20Increase%20Since%202019.png)
Trois-Rivières leads all Canadian cities with the most
dramatic rent increase since 2019, with Quebec cities
and Atlantic Canadian markets dominating the top 10.

---

### Rent Price Trends — Top 10 Cities (2019–2025)
![Rent Price Trends](images/Rent%20Price%20Trends_%20Top%2010%20Cities%20(2019-2025).png)
Vancouver consistently shows the highest rent levels
across the entire 2019 to 2025 trend line compared
to all other major Canadian cities.

---

### Top 10 Cities by Average Rent (2025)
![Top 10 Cities by Average Rent](images/Top%2010%20Cities%20by%20Average%20Rent%20(2025).png)
Vancouver has the highest average rent among the top
10 most expensive Canadian cities in 2025.

---

### Average Rent by Number of Bedrooms (2025)
![Average Rent by Bedrooms](images/Average%20Rent%20by%20Number%20of%20Bedrooms%20(2025).png)
Units with 3 or more bedrooms have the highest average
asking rent compared to all other bedroom categories.

---

### Average Rent by Unit Type (2025)
![Average Rent by Unit Type](images/Average%20Rent%20by%20Unit%20Type%20(2025).png)
Houses have the highest average asking rent compared
to apartments and rooms across all Canadian cities.

---

### Average Rent Heatmap — City vs Year
![Average Rent Heatmap](images/Average%20Rent%20Heatmap_%20City%20vs%20Year.png)
Vancouver consistently remains the most expensive city
across all years from 2019 to 2025 in the heatmap.

---
## Author
GitHub: tomfatoke
