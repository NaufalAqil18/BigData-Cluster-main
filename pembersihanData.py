from pyspark.sql.functions import col, regexp_replace

# Menghapus karakter khusus dari kolom 'title'
df_clean = df.withColumn("title", regexp_replace(col("title"), "[^a-zA-Z0-9\\s]", ""))

# Menampilkan hasil setelah pembersihan
df_clean.show(5)
