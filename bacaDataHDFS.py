from pyspark.sql import SparkSession

# Membuat SparkSession
spark = SparkSession.builder.appName("TempoNewsProcessing").getOrCreate()

# Membaca file CSV dari HDFS
df = spark.read.csv("hdfs://localhost:9000/user/username/news_data/tempo_news.csv", header=True, inferSchema=True)

# Menampilkan lima baris pertama
df.show(5)
