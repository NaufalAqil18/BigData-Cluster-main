from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("WordCount") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# Read data from HDFS
text_file = spark.read.text("hdfs://hadoop-namenode:8020/input/test.txt").rdd

# Perform word count
word_counts = text_file.flatMap(lambda line: line.value.split()) \
                       .map(lambda word: (word, 1)) \
                       .reduceByKey(lambda a, b: a + b)

# Save results to HDFS
word_counts.saveAsTextFile("hdfs://hadoop-namenode:8020/output/wordcount")

# Stop the Spark session
spark.stop()