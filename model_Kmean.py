from pyspark.sql import SparkSession
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.clustering import LDA
from pyspark.sql.functions import col, concat_ws

# Membuat SparkSession
spark = SparkSession.builder.appName("LDA_Model").getOrCreate()

# Membaca hasil preprocessed data dari output_path yang sudah disimpan
output_path = "hdfs://hadoop-namenode:8020/user/news_data/hasilpreprocessing.csv"
df = spark.read.csv(output_path, header=True, inferSchema=True)

# Menggabungkan kata-kata yang telah difilter dari kolom title dan content
df_filtered = df.withColumn("filtered_words", concat_ws(" ", col("title_filtered"), col("content_filtered")))

# Tokenisasi teks dari kolom filtered_words
tokenizer_filtered = Tokenizer(inputCol="filtered_words", outputCol="words")
df_tokenized_filtered = tokenizer_filtered.transform(df_filtered)

# Menghitung Term Frequency (TF)
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=1000)
featurizedData = hashingTF.transform(df_tokenized_filtered)

# Menghitung Inverse Document Frequency (IDF)
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

# Membangun model LDA
lda = LDA(k=3, maxIter=10, featuresCol="features", seed=42)
lda_model = lda.fit(rescaledData)

# Menampilkan topik-topik yang ditemukan oleh model LDA
topics = lda_model.describeTopics(3)
topics.show(truncate=False)

# Menggunakan model LDA untuk memprediksi topik untuk setiap dokumen
predictions = lda_model.transform(rescaledData)

# Menampilkan beberapa hasil prediksi
predictions.select("filtered_words", "prediction").show(5, truncate=False)

# Menyimpan hasil prediksi ke HDFS
output_lda_path = "hdfs://hadoop-namenode:8020/user/news_data/lda_predictions.csv"
predictions.select("filtered_words", "prediction").write.csv(output_lda_path, header=True, mode="overwrite")
