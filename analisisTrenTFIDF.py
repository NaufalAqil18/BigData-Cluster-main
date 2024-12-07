from pyspark.ml.feature import Tokenizer, HashingTF, IDF
from pyspark.sql.functions import col, concat_ws, udf
from pyspark.sql.types import ArrayType, FloatType
from pyspark.sql import SparkSession

# Membuat SparkSession
spark = SparkSession.builder.appName("TFIDFProcessing").getOrCreate()

# Membaca data hasil preprocessing dari file CSV
input_path = "hdfs://hadoop-namenode:8020/user/news_data/hasilpreprocessing.csv"
df_result = spark.read.csv(input_path, header=True, inferSchema=True)

# Menggabungkan kata-kata yang telah difilter dari kolom title dan content
df_filtered = df_result.withColumn("filtered_words", concat_ws(" ", col("title_filtered"), col("content_filtered")))

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

# Konversi kolom features (vektor) menjadi array float
def vector_to_array(v):
    return v.toArray().tolist()

vector_to_array_udf = udf(vector_to_array, ArrayType(FloatType()))
rescaledData = rescaledData.withColumn("features_array", vector_to_array_udf(col("features")))

# Mengonversi array menjadi string (separated by commas)
rescaledData = rescaledData.withColumn("features_string", concat_ws(",", col("features_array")))

# Menampilkan hasil TF-IDF
rescaledData.select("filtered_words", "features_string").show(5)

# Menyimpan hasil TF-IDF ke HDFS sebagai CSV
output_path = "hdfs://hadoop-namenode:8020/user/news_data/hasil_tfidf.csv"
rescaledData.select("filtered_words", "features_string") \
            .write.csv(output_path, header=True, mode="overwrite")
