from pyspark.sql.functions import col, regexp_replace, to_date, concat_ws
from pyspark.ml.feature import Tokenizer, StopWordsRemover

# Membuat SparkSession
spark = SparkSession.builder.appName("PreprocessingNewsData").getOrCreate()

# Membaca data dari file CSV
df = spark.read.csv("hdfs://hadoop-namenode:8020/user/news_data/articles_data.csv", header=True, inferSchema=True)

# Membersihkan teks dengan menghapus karakter khusus dari kolom title, reporter, editor, dan content
df_clean = df.withColumn("title", regexp_replace(col("title"), "[^a-zA-Z0-9\\s]", "")) \
             .withColumn("reporter", regexp_replace(col("reporter"), "[^a-zA-Z0-9\\s]", "")) \
             .withColumn("editor", regexp_replace(col("editor"), "[^a-zA-Z0-9\\s]", "")) \
             .withColumn("content", regexp_replace(col("content"), "[^a-zA-Z0-9\\s]", ""))

# Konversi kolom date_time ke format tanggal
df_clean = df_clean.withColumn("date_time", to_date(col("date_time"), "yyyy-MM-dd"))

# Tokenisasi teks pada kolom title dan content
tokenizer_title = Tokenizer(inputCol="title", outputCol="title_words")
tokenizer_content = Tokenizer(inputCol="content", outputCol="content_words")

df_tokenized = tokenizer_title.transform(df_clean)
df_tokenized = tokenizer_content.transform(df_tokenized)

# Menghapus stopwords dari kolom title dan content
remover_title = StopWordsRemover(inputCol="title_words", outputCol="title_filtered")
remover_content = StopWordsRemover(inputCol="content_words", outputCol="content_filtered")

df_preprocessed = remover_title.transform(df_tokenized)
df_preprocessed = remover_content.transform(df_preprocessed)

# Mengonversi kolom array menjadi string menggunakan concat_ws
df_result = df_preprocessed.withColumn("title_filtered", concat_ws(" ", col("title_filtered"))) \
                           .withColumn("content_filtered", concat_ws(" ", col("content_filtered")))

# Menampilkan hasil akhir preprocessing
df_result.select("title_filtered", "reporter", "editor", "date_time", "content_filtered").show(5, truncate=False)

# Menyimpan hasil preprocessing ke HDFS sebagai CSV
output_path = "hdfs://hadoop-namenode:8020/user/news_data/hasilpreprocessing.csv"

df_result.select("title_filtered", "reporter", "editor", "date_time", "content_filtered") \
         .write.csv(output_path, header=True, mode="overwrite")

#df = spark.read.csv("hdfs://hadoop-namenode:8020/user/news_data/articles_data.csv", header=True, inferSchema=True)
