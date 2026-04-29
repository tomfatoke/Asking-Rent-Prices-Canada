from pyspark.sql.functions import col, split, when, regexp_replace, trim 

silver_df = spark.read.format("delta").table("projects.rent_project.bronze_rent_raw") 

silver_df.show(5)
silver_df = silver_df.select("REF_DATE", "GEO", "Rental_unit_type", "VALUE") 
silver_df = silver_df.dropna(subset=["VALUE"]) 

print(f"rows remaining after cleaning: {silver_df.count()}") 
silver_df.show(5) 

silver_df = silver_df.withColumn("City", 
                                 trim(split(col("GEO"), ",")[0])) \
                                     .drop("GEO") 
silver_df.show(5) 

silver_df = (silver_df 
    .withColumn("Unit_type", 
                split(col("Rental_unit_type"), " - ")[0])  
    .withColumn("Bedrooms", 
                when(col("Rental_unit_type") == "Room", "Room") 
                .when(col("Rental_unit_type").contains("No bedroom"), "Studio") 
                .otherwise(split(col("Rental_unit_type"), " - ")[1])) 
    .drop("Rental_unit_type")  
)
silver_df.show(10) 

silver_df = (silver_df 
    .withColumnRenamed("REF_DATE", "Reference_Date") 
    .withColumnRenamed("VALUE", "Asking_rent") 
    .withColumn("Asking_rent", 
                col("Asking_rent").cast("float"))
) 

silver_df.show(5) 

silver_df.write.format("delta").mode("overwrite").saveAsTable("projects.rent_project.silver_rent_layer")

print(f"Rows written to silver: {silver_df.count()}")