import pandas as pd
import matplotlib.pyplot as plt

# Mengunduh hasil clustering dari HDFS
# hdfs dfs -get /user/news_data/hasil_clustering.csv ~/hasil_clustering

# Membaca data hasil clustering ke Pandas
df = pd.read_csv('hdfs://hadoop-namenode:8020/user/news_data/hasil_clustering.csv/part-00000-9ced3b32-7ce0-48bf-b7ce-6ecb2e5ec63e-c000.csv', names=['features_string', 'cluster'])

# Konversi 'features_string' menjadi list of floats
df['features'] = df['features_string'].apply(lambda x: [float(num) for num in x.split(',')])

# Melakukan PCA manual menggunakan sklearn untuk menyederhanakan dimensi
from sklearn.decomposition import PCA
import numpy as np

# Mengonversi kolom 'features' menjadi array numpy
features_array = np.array(df['features'].tolist())

# Mengurangi dimensi menjadi 2 komponen dengan PCA
pca = PCA(n_components=2)
pca_result = pca.fit_transform(features_array)

# Menambahkan hasil PCA ke dataframe
df['pca_1'] = pca_result[:, 0]
df['pca_2'] = pca_result[:, 1]

# Scatter plot hasil clustering
plt.figure(figsize=(10, 8))
scatter = plt.scatter(df['pca_1'], df['pca_2'], c=df['cluster'], cmap='viridis', marker='o')

plt.title("Visualisasi Hasil Clustering dengan K-Means (PCA 2D)")
plt.xlabel("PCA Komponen 1")
plt.ylabel("PCA Komponen 2")

# Menambahkan legend untuk cluster
plt.legend(*scatter.legend_elements(), title="Cluster")

# Simpan plot ke dalam file PNG
plt.savefig("hasil_clustering.png")
plt.show()

# --- Pie Chart Distribusi Cluster ---
cluster_counts = df['cluster'].value_counts()
cluster_labels = [f"Cluster {i}" for i in cluster_counts.index]

plt.figure(figsize=(8, 6))
plt.pie(cluster_counts, labels=cluster_labels, autopct='%1.1f%%', startangle=140)
plt.title('Distribusi Cluster Hasil K-Means')
plt.show()
