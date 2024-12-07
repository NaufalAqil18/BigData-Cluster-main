from pyspark.ml.feature import Tokenizer, HashingTF, IDF, PCA
from pyspark.ml.clustering import KMeans
from pyspark.sql.functions import col, concat_ws, udf
from pyspark.sql.types import ArrayType, FloatType, StringType
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import ClusteringEvaluator
import matplotlib.pyplot as plt

# Membuat SparkSession
spark = SparkSession.builder.appName("TFIDFClusteringWithVisualization").getOrCreate()

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

# Mengonversi array menjadi string (separated by commas) agar dapat disimpan ke CSV
def array_to_string(arr):
    return ','.join(map(str, arr))

array_to_string_udf = udf(array_to_string, StringType())  # Pastikan StringType diimpor
rescaledData = rescaledData.withColumn("features_string", array_to_string_udf(col("features_array")))

# Menyimpan hasil TF-IDF ke HDFS sebagai CSV
output_tfidf_path = "hdfs://hadoop-namenode:8020/user/news_data/hasil_tfidf.csv"
rescaledData.select("filtered_words", "features_string") \
            .write.csv(output_tfidf_path, header=True, mode="overwrite")

# --- Mulai K-Means Clustering berdasarkan hasil TF-IDF ---
# Menggunakan kolom 'features' yang sudah ada setelah TF-IDF dan menambahkan sebagai input ke K-Means
df_features = rescaledData.select("features")

# Mengatur KMeans dengan jumlah cluster yang diinginkan
kmeans = KMeans(k=3, seed=1, featuresCol="features", predictionCol="cluster")

# Fit model KMeans pada data
model = kmeans.fit(df_features)

# Menambahkan kolom 'cluster' hasil prediksi ke dataframe asli
df_with_cluster = model.transform(df_features)

# Konversi kolom 'features' menjadi array float untuk dapat disimpan
df_with_cluster = df_with_cluster.withColumn("features_array", vector_to_array_udf(col("features")))

# Mengonversi array 'features_array' menjadi string
df_with_cluster = df_with_cluster.withColumn("features_string", array_to_string_udf(col("features_array")))

# Menyimpan hasil clustering ke HDFS setelah konversi kolom features menjadi string
output_cluster_path = "hdfs://hadoop-namenode:8020/user/news_data/hasil_clustering.csv"
df_with_cluster.select("features_string", "cluster").write.csv(output_cluster_path, header=True, mode="overwrite")

# Menampilkan hasil clustering
df_with_cluster.select("features_string", "cluster").show(5, truncate=False)

# Evaluasi model clustering menggunakan ClusteringEvaluator
evaluator = ClusteringEvaluator(predictionCol="cluster", featuresCol="features")

# Menghitung Silhouette Score (nilai evaluasi)
silhouette = evaluator.evaluate(df_with_cluster)
print(f"Silhouette Score: {silhouette}")

# --- PCA untuk Visualisasi Hasil Clustering ---
# Melakukan PCA untuk mengurangi dimensi menjadi 2 komponen utama
pca = PCA(k=2, inputCol="features", outputCol="pca_features")
df_pca = pca.fit(df_with_cluster).transform(df_with_cluster)

# Fungsi untuk mengekstrak nilai PCA
def extract_pca_values(vector):
    return vector.values.tolist()

extract_pca_values_udf = udf(extract_pca_values, ArrayType(FloatType()))

# Terapkan UDF pada kolom 'pca_features' untuk mengekstrak nilai PCA
df_pca = df_pca.withColumn("pca_values", extract_pca_values_udf(col("pca_features")))

# Ambil nilai x dan y dari hasil PCA (komponen pertama dan kedua)
df_pca = df_pca.withColumn("x", col("pca_values")[0])  # Komponen pertama
df_pca = df_pca.withColumn("y", col("pca_values")[1])  # Komponen kedua

# Convert DataFrame ke Pandas untuk visualisasi menggunakan matplotlib
df_pca_pd = df_pca.toPandas()

# Plotting hasil clustering dengan PCA
plt.figure(figsize=(10, 8))

# Membuat scatter plot
plt.scatter(df_pca_pd['x'], df_pca_pd['y'], c=df_pca_pd['cluster'], cmap='viridis', marker='o')

# Menambahkan label dan title
plt.title("Visualisasi Hasil Clustering dengan K-Means (PCA 2D)")
plt.xlabel("PCA Komponen 1")
plt.ylabel("PCA Komponen 2")

# Menambahkan legend untuk cluster
plt.colorbar(label='Cluster')

# Simpan plot ke dalam file PNG
plt.savefig("plot.png")  # Ganti dengan path yang sesuai di container
plt.close()
