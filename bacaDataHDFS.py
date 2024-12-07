from pyspark.sql import SparkSession

# Membuat SparkSession
spark = SparkSession.builder.appName("TempoNewsProcessing").getOrCreate()

# Membaca file CSV dari HDFS
df = spark.read.csv("hdfs://hadoop-namenode:8020/user/news_data/articles_data.csv", header=True, inferSchema=True)

# Menampilkan lima baris pertama
df.show(5)
