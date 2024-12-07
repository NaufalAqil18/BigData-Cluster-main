### Modul Praktikum Data Engineering dan Machine Learning dengan Dockerized Hadoop & Spark
 
**Tujuan:** Memahami implementasi ekstraksi data, transformasi data, seleksi fitur, klasifikasi, clustering, dan pemodelan topik menggunakan cluster Hadoop dan Spark yang diatur dalam Docker Compose.

### 1. **Ekstraksi, Transformasi Data, dan Seleksi Fitur (TF-IDF dan Word2Vec) - Pertemuan 7**

#### **Pengertian**
- **TF-IDF (Term Frequency-Inverse Document Frequency)**: Metode untuk mengukur pentingnya kata dalam dokumen dan kumpulan dokumen. 
- **Word2Vec**: Teknik pembelajaran representasi kata yang menghasilkan embedding dari kata-kata yang mempertimbangkan hubungan semantik antar kata.

#### **Kegunaan**
- TF-IDF: Digunakan untuk analisis teks, seperti klasifikasi, clustering, atau model prediktif lainnya.
- Word2Vec: Membuat embedding kata yang berguna untuk banyak tugas NLP, seperti analisis sentimen atau rekomendasi.

#### **Setup Docker**
Pada konfigurasi Docker Compose sebelumnya, layanan Spark Master dan Spark Worker sudah diatur untuk pemrosesan terdistribusi. Kita akan menggunakan Spark MLlib untuk implementasi TF-IDF dan Word2Vec.

#### **Contoh Penggunaan Sederhana: TF-IDF**

1. Siapkan session Spark di container `spark-master`.
   
2. Jalankan skrip berikut di `spark-master` untuk mengimplementasikan TF-IDF:
   ```python
   from pyspark.sql import SparkSession
   from pyspark.ml.feature import Tokenizer, HashingTF, IDF

   spark = SparkSession.builder.appName("TF-IDF Example").getOrCreate()

   # Data sampel
   data = [("Dokumen pertama berisi data.",),
           ("Dokumen kedua memiliki informasi lain.",),
           ("Ini adalah dokumen ketiga.",)]
   df = spark.createDataFrame(data, ["text"])

   # Tokenisasi
   tokenizer = Tokenizer(inputCol="text", outputCol="words")
   wordsData = tokenizer.transform(df)

   # Term Frequency
   hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=20)
   featurizedData = hashingTF.transform(wordsData)

   # Inverse Document Frequency (IDF)
   idf = IDF(inputCol="rawFeatures", outputCol="features")
   idfModel = idf.fit(featurizedData)
   rescaledData = idfModel.transform(featurizedData)

   rescaledData.select("features").show(truncate=False)
   ```

#### **Contoh Penggunaan Word2Vec**

1. Jalankan model Word2Vec di `spark-master` untuk mendapatkan embedding kata:
   ```python
   from pyspark.ml.feature import Word2Vec

   # Menggunakan data yang sudah di-tokenisasi
   word2Vec = Word2Vec(vectorSize=3, minCount=0, inputCol="words", outputCol="result")
   model = word2Vec.fit(wordsData)
   result = model.transform(wordsData)

   result.select("result").show(truncate=False)
   ```

---

### 2. **Klasifikasi Data Teks Sosial Media (Logistic Regression, Naive Bayes, Linear SVM) - Pertemuan 8**

#### **Pengertian**
- **Logistic Regression**: Algoritma klasifikasi biner yang digunakan untuk memprediksi probabilitas suatu kelas.
- **Naive Bayes**: Model probabilistik yang berdasarkan teorema Bayes dengan asumsi independensi antar fitur.
- **Linear SVM (Support Vector Machine)**: Algoritma klasifikasi yang memisahkan data berdasarkan hyperplane.

#### **Kegunaan**
- Logistic Regression: Berguna untuk klasifikasi teks sosial media, misalnya analisis spam.
- Naive Bayes: Cocok untuk klasifikasi teks berdasarkan frekuensi kata.
- Linear SVM: Digunakan dalam masalah klasifikasi yang melibatkan banyak fitur.

#### **Setup Docker**
Layanan Spark pada container `spark-master` dan `spark-worker` akan digunakan untuk menjalankan model klasifikasi teks.

#### **Contoh Penggunaan Logistic Regression**

1. Siapkan Spark session di `spark-master` dan lakukan klasifikasi menggunakan Logistic Regression.
   ```python
   from pyspark.ml.classification import LogisticRegression
   from pyspark.ml.feature import CountVectorizer

   # Contoh data teks
   training = spark.createDataFrame([
       (0, "pesan ini bagus", 1.0),
       (1, "pesan ini buruk", 0.0),
       (2, "pesan netral", 1.0),
   ], ["id", "text", "label"])

   # Tokenisasi dan Vectorization
   tokenizer = Tokenizer(inputCol="text", outputCol="words")
   wordsData = tokenizer.transform(training)
   vectorizer = CountVectorizer(inputCol="words", outputCol="features")
   featurizedData = vectorizer.fit(wordsData).transform(wordsData)

   # Logistic Regression
   lr = LogisticRegression(featuresCol="features", labelCol="label")
   lrModel = lr.fit(featurizedData)
   predictions = lrModel.transform(featurizedData)

   predictions.select("text", "prediction").show()
   ```

#### **Contoh Penggunaan Naive Bayes**

1. Ubah pipeline untuk Naive Bayes.
   ```python
   from pyspark.ml.classification import NaiveBayes

   nb = NaiveBayes(featuresCol="features", labelCol="label")
   nbModel = nb.fit(featurizedData)
   predictions = nbModel.transform(featurizedData)

   predictions.select("text", "prediction").show()
   ```

---

### 3. **Klasifikasi dengan Decision Tree dan Random Forest (Pertemuan 9)**

#### **Pengertian**
- **Decision Tree**: Model klasifikasi berbasis pohon yang memecah data ke dalam subset.
- **Random Forest**: Ensemble dari beberapa decision tree untuk menghasilkan klasifikasi yang lebih akurat.

#### **Kegunaan**
- Decision Tree: Mudah diinterpretasi, digunakan untuk klasifikasi sederhana.
- Random Forest: Memberikan akurasi yang lebih tinggi dan mencegah overfitting.

#### **Contoh Penggunaan Decision Tree**

1. Implementasi sederhana Decision Tree di `spark-master`:
   ```python
   from pyspark.ml.classification import DecisionTreeClassifier

   dt = DecisionTreeClassifier(featuresCol="features", labelCol="label")
   dtModel = dt.fit(featurizedData)
   predictions = dtModel.transform(featurizedData)

   predictions.select("text", "prediction").show()
   ```

#### **Contoh Penggunaan Random Forest**

1. Implementasi sederhana Random Forest di `spark-master`:
   ```python
   from pyspark.ml.classification import RandomForestClassifier

   rf = RandomForestClassifier(featuresCol="features", labelCol="label")
   rfModel = rf.fit(featurizedData)
   predictions = rfModel.transform(featurizedData)

   predictions.select("text", "prediction").show()
   ```

---

### 4. **Clustering menggunakan K-Means (Pertemuan 11)**

#### **Pengertian**
- **K-Means**: Algoritma clustering yang membagi data ke dalam k kelompok berdasarkan kemiripan.

#### **Kegunaan**
- Mengelompokkan data tanpa label untuk menemukan pola atau struktur dalam dataset.

#### **Contoh Penggunaan K-Means**

1. Implementasi K-Means clustering:
   ```python
   from pyspark.ml.clustering import KMeans

   kmeans = KMeans(k=3, seed=1)
   model = kmeans.fit(featurizedData)
   predictions = model.transform(featurizedData)

   predictions.select("text", "prediction").show()
   ```

---

### 5. **Pemodelan Topik dengan Latent Dirichlet Allocation (LDA) - Pertemuan 13**

#### **Pengertian**
- **LDA (Latent Dirichlet Allocation)**: Algoritma untuk menemukan topik-topik dalam dokumen teks.

#### **Kegunaan**
- Menggunakan LDA untuk menemukan tema dalam dokumen besar tanpa label.

#### **Contoh Penggunaan LDA**

1. Implementasi LDA di Spark:
   ```python
   from pyspark.ml.clustering import LDA

   lda = LDA(k=3, maxIter=10)
   ldaModel = lda.fit(featurizedData)

   topics = ldaModel.describeTopics()
   topics.show(truncate=False)
   ```

---

### 6. **Membangun Fitur dan Visualisasi (Matplotlib) - Pertemuan 14**

#### **Pengertian**
- **Feature Engineering**: Proses transformasi data mentah menjadi fitur yang dapat dimanfaatkan oleh algoritma machine learning.
- **Visualisasi**: Menggunakan grafik untuk memahami pola dalam data.

#### **Contoh Penggunaan Visualisasi**

1. Gunakan Matplotlib untuk memvisualisasikan data hasil dari pipeline Spark:
   ```python
   import matplotlib.pyplot as plt

   # Contoh visualisasi distribusi prediksi
   predictions_pd = predictions.select("prediction").toPandas()
   predictions_pd['prediction'].value_counts().plot(kind='bar')
   plt.show()
   ```

---

Dengan menjalankan modul ini di atas Dockerized Spark-Hadoop Cluster, Anda dapat mempelajari workflow skala besar menggunakan Spark MLlib, serta memahami bagaimana data teks diolah, diklasifikasikan, dan diprediksi secara terdistribusi.