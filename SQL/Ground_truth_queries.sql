-- Which are the most affordable cities for a 1 bedroom apartment? 
SELECT
  City,
  ROUND(AVG(avg_asking_rent), 2) AS avg_rent
FROM
  projects.rent_project.gold_rent_aggregated
WHERE
  Unit_type = 'Apartment'
  AND Bedrooms = '1 bedroom'
GROUP BY
  City
ORDER BY
  avg_rent ASC
LIMIT 10 

--What is the rent trend for a specific city? 
SELECT
  Year,
  Month,
  Unit_type,
  Bedrooms,
  avg_asking_rent,
  YOY_pct_change
FROM
  projects.rent_project.gold_rent_aggregated
WHERE
  City = 'Calgary'
ORDER BY
  Year,
  Month 

-- What is the average rent by unit type and bedroom count?
SELECT
  Unit_type,
  Bedrooms,
  ROUND(AVG(avg_asking_rent), 2) AS avg_rent
FROM
  projects.rent_project.gold_rent_aggregated
GROUP BY
  Unit_type,
  Bedrooms
ORDER BY
  avg_rent DESC

--Which cities have seen the highest rent increases year over year? 
SELECT
  City,
  Unit_type,
  Bedrooms,
  Year,
  Month,
  YOY_pct_change
FROM
  projects.rent_project.gold_rent_aggregated
WHERE
  YOY_pct_change IS NOT NULL
ORDER BY
  YOY_pct_change DESC 

--How has the average rent changed over time?  
SELECT
  Year,
  Month,
  ROUND(AVG(avg_asking_rent), 2) AS avg_rent
FROM
  projects.rent_project.gold_rent_aggregated
GROUP BY
  Year,
  Month
ORDER BY
  Year,
  Month

--Which are the top 10 most expensive cities for rent?  
SELECT
  City,
  ROUND(AVG(avg_asking_rent), 2) AS avg_rent
FROM
  projects.rent_project.gold_rent_aggregated
GROUP BY
  City
ORDER BY
  avg_rent DESC
LIMIT 10 

--What is the average asking rent by city?  
SELECT
  City,
  ROUND(AVG(avg_asking_rent), 2) AS avg_rent
FROM
  projects.rent_project.gold_rent_aggregated
GROUP BY
  City
ORDER BY
  avg_rent DESC
