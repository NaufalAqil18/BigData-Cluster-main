from pyspark.sql import SparkSession
from pyspark.ml.feature import PCA
from pyspark.ml.clustering import KMeans
from pyspark.sql.functions import col
import matplotlib.pyplot as plt

# Membuat SparkSession jika belum ada
spark = SparkSession.builder.appName("PCAClusteringVisualization").getOrCreate()

# Anggap df_with_cluster adalah DataFrame yang sudah berisi hasil clustering dan fitur TF-IDF
# Jika df_with_cluster belum ada, buat terlebih dahulu dengan mengikuti proses yang ada

# Menggunakan PCA untuk mereduksi dimensi menjadi 2D
pca = PCA(k=2, inputCol="features", outputCol="pca_features")
pca_model = pca.fit(df_with_cluster)
df_pca = pca_model.transform(df_with_cluster)

# Ambil hasil PCA dan cluster untuk visualisasi
df_pca = df_pca.select("pca_features", "cluster")
df_pca = df_pca.withColumn("x", col("pca_features")[0])
df_pca = df_pca.withColumn("y", col("pca_features")[1])

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

# Tampilkan plot
plt.show()

# Jangan lupa untuk menutup sesi Spark jika sudah selesai
spark.stop()
