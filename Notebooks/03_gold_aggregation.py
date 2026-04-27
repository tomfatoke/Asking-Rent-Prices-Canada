from pyspark.sql.functions import col, lag, year, month, round, avg, max, min, count 
from pyspark.sql.window import Window 

gold_df = spark.read.format("delta").table("projects.rent_project.silver_rent_layer") 

gold_df.show(5)


gold_df = (gold_df
    .withColumn("Year", year(col("Reference_Date"))) 
    .withColumn("Month", month(col("Reference_Date"))) 
    .drop("Reference_Date") 
) 
gold_df.show(5) 

gold_df =(gold_df
          .groupBy("Year", "Month", "City", "Unit_type", "Bedrooms")
          .agg(round(avg("Asking_rent"), 2).alias("avg_asking_rent"),
               max("Asking_rent").alias("max_asking_rent"),
               min("Asking_rent").alias("min_asking_rent"), 
               count("*").alias("Total_listings") 
          )
) 
gold_df.show(5)
 

window_spec = (Window 
    .partitionBy("City", "Unit_type", "Bedrooms") 
    .orderBy("Year", "Month")
)

gold_df = (gold_df
           .withColumn("prev_year_rent", 
                lag("avg_asking_rent", 4).over(window_spec)) 
           .withColumn("YOY_pct_change", 
                round((col("avg_asking_rent") - col("prev_year_rent")) 
                / col("prev_year_rent") * 100, 2)) 
) 
gold_df.show(5) 


gold_df.write.format("delta").mode("overwrite").saveAsTable("projects.rent_project.gold_rent_aggregated")

print(f"Rows written to gold: {gold_df.count()}")