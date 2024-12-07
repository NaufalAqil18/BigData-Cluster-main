from pyspark.ml.feature import Tokenizer, HashingTF, IDF, PCA
from pyspark.ml.clustering import KMeans
from pyspark.sql.functions import col, concat_ws, udf
from pyspark.sql.types import ArrayType, FloatType, StringType
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import ClusteringEvaluator
import matplotlib.pyplot as plt

# Membuat SparkSession
spark = SparkSession.builder.appName("TFIDFClusteringWithSentiment").getOrCreate()

# --- 1. Membaca Data ---
input_path = "hdfs://hadoop-namenode:8020/user/news_data/hasilpreprocessing.csv"
df_result = spark.read.csv(input_path, header=True, inferSchema=True)

# Menggabungkan kata-kata yang telah difilter dari kolom title dan content
df_filtered = df_result.withColumn("filtered_words", concat_ws(" ", col("title_filtered"), col("content_filtered")))

# Menampilkan 5 baris teratas setelah menggabungkan kata-kata yang difilter
df_filtered.select("filtered_words").show(5, truncate=False)

# --- 2. Tokenisasi dan TF-IDF ---
# Tokenisasi
tokenizer_filtered = Tokenizer(inputCol="filtered_words", outputCol="words")
df_tokenized_filtered = tokenizer_filtered.transform(df_filtered)

# Menampilkan 5 baris teratas setelah tokenisasi
df_tokenized_filtered.select("filtered_words", "words").show(5, truncate=False)

# HashingTF
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=1000)
featurizedData = hashingTF.transform(df_tokenized_filtered)

# Menampilkan 5 baris teratas setelah HashingTF
featurizedData.select("words", "rawFeatures").show(5, truncate=False)

# IDF
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

# Menampilkan 5 baris teratas setelah IDF
rescaledData.select("rawFeatures", "features").show(5, truncate=False)

# Konversi kolom features menjadi array float
def vector_to_array(v):
    return v.toArray().tolist()

vector_to_array_udf = udf(vector_to_array, ArrayType(FloatType()))
rescaledData = rescaledData.withColumn("features_array", vector_to_array_udf(col("features")))

# --- 3. Menentukan Sentimen ---
positive_words = ['baik', 'bagus', 'positif', 'hebat', 'senang', 'puas', 'luar biasa']
negative_words = ['buruk', 'negatif', 'jelek', 'sedih', 'kecewa', 'mengecewakan', 'payah']

def determine_sentiment(text):
    text_lower = text.lower()
    if any(word in text_lower for word in positive_words):
        return 'positive'
    elif any(word in text_lower for word in negative_words):
        return 'negative'
    else:
        return 'neutral'

determine_sentiment_udf = udf(determine_sentiment, StringType())
df_with_sentiment = rescaledData.withColumn("sentiment", determine_sentiment_udf(col("filtered_words")))

# --- 4. K-Means Clustering ---
kmeans = KMeans(k=3, seed=1, featuresCol="features", predictionCol="cluster")
model = kmeans.fit(df_with_sentiment)
df_with_cluster = model.transform(df_with_sentiment)

# Evaluasi clustering
evaluator = ClusteringEvaluator(predictionCol="cluster", featuresCol="features")
silhouette = evaluator.evaluate(df_with_cluster)
print(f"Silhouette Score: {silhouette}")

# --- 5. PCA untuk Visualisasi ---
pca = PCA(k=2, inputCol="features", outputCol="pca_features")
df_pca = pca.fit(df_with_cluster).transform(df_with_cluster)

# Ekstraksi nilai PCA
def extract_pca_values(vector):
    return vector.toArray().tolist()

extract_pca_values_udf = udf(extract_pca_values, ArrayType(FloatType()))
df_pca = df_pca.withColumn("pca_values", extract_pca_values_udf(col("pca_features")))

# Ambil komponen PCA pertama dan kedua
df_pca = df_pca.withColumn("x", col("pca_values")[0])
df_pca = df_pca.withColumn("y", col("pca_values")[1])

# Konversi ke Pandas untuk visualisasi
df_pca_pd = df_pca.select("x", "y", "cluster", "sentiment").toPandas()

# --- 6. Visualisasi Hasil Clustering dengan Sentimen ---
plt.figure(figsize=(10, 8))

# Scatter plot dengan warna berdasarkan cluster
scatter = plt.scatter(df_pca_pd['x'], df_pca_pd['y'], c=df_pca_pd['cluster'], cmap='viridis', marker='o')

# Tambahkan judul dan label sumbu
plt.title("Visualisasi Hasil Clustering dengan K-Means dan Sentimen (PCA 2D)")
plt.xlabel("PCA Komponen 1")
plt.ylabel("PCA Komponen 2")

# Tambahkan colorbar untuk cluster
plt.colorbar(scatter, label='Cluster')

# Simpan plot sebagai file PNG
plt.savefig("clustering_sentiment_plot.png")
plt.close()

# --- 7. Visualisasi Sentimen dalam Bentuk Pie Chart ---

# Hitung jumlah sentimen
sentiment_counts = df_pca_pd['sentiment'].value_counts()

# Membuat pie chart
plt.figure(figsize=(8, 8))
plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140, colors=['#66b3ff', '#ff9999', '#99ff99'])
plt.title("Distribusi Sentimen dalam Clustering")

# Simpan pie chart sebagai file PNG
plt.savefig("sentiment_distribution_pie.png")
plt.close()
