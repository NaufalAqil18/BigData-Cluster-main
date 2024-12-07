### Modul Praktikum: Deploy Big Data Cluster dengan Docker-Compose (Hadoop, Spark, Hive, YARN)
 
**Tujuan:** Memahami konsep, kegunaan, serta implementasi sederhana dan kompleks dari Hadoop, Spark, Hive, dan YARN dalam lingkungan terdistribusi menggunakan Docker-Compose.

---

### 1. **Pendahuluan**

Dalam dunia big data, data biasanya sangat besar dan tersebar di berbagai lokasi. Untuk menangani data dalam jumlah besar ini, sistem terdistribusi diperlukan. Praktikum ini akan fokus pada penggunaan komponen utama berikut:

- **Hadoop HDFS (Hadoop Distributed File System)**: Sistem file terdistribusi yang memungkinkan penyimpanan dan manajemen data dalam skala besar. HDFS membagi data ke dalam blok-blok dan menyimpannya di beberapa node, yang memberikan redundansi dan kecepatan akses yang tinggi.
  
- **YARN (Yet Another Resource Negotiator)**: Framework yang mengelola dan mengalokasikan sumber daya komputasi (CPU, memori) dalam cluster untuk berbagai aplikasi yang berjalan di atas Hadoop, seperti MapReduce atau Spark.

- **Spark**: Framework komputasi yang dirancang untuk pemrosesan cepat data skala besar. Spark mendukung komputasi batch dan real-time serta memiliki API yang mendukung banyak bahasa (Scala, Python, Java). Spark dikenal lebih cepat dari MapReduce karena eksekusi in-memory.

- **Hive**: Hive adalah alat data warehouse yang menyediakan antarmuka query seperti SQL untuk data yang disimpan di HDFS. Hive memungkinkan pengguna non-programmer untuk mengakses dan menganalisis data besar melalui sintaks SQL yang familiar.

#### **Kegunaan Komponen:**
- **HDFS** digunakan untuk menyimpan data terdistribusi dengan aman dan redundansi yang tinggi.
- **YARN** mengelola job eksekusi dalam cluster, memastikan penggunaan sumber daya secara efisien.
- **Spark** digunakan untuk pemrosesan data skala besar baik secara batch maupun real-time, dengan performa lebih cepat dari MapReduce.
- **Hive** memungkinkan query SQL-like untuk pengguna bisnis atau analis yang tidak terbiasa dengan bahasa pemrograman.

---

### 2. **Contoh Penggunaan Sederhana**

Berikut adalah contoh sederhana yang menunjukkan bagaimana setiap komponen dapat digunakan dalam proses pemrosesan data. Cluster ini dapat dibangun menggunakan Docker, dan contoh-contoh berikut akan menggambarkan tugas umum yang dijalankan dalam big data environments.

#### **2.1. Mengupload Data ke HDFS**
Langkah pertama dalam proses data adalah mengunggah data ke sistem file terdistribusi, yaitu HDFS. Data dalam HDFS tersedia untuk diproses oleh Spark, Hive, atau aplikasi lain yang berjalan di atas Hadoop.

**Langkah:**
1. Buka terminal untuk mengakses container `hadoop-namenode`.
2. Buat direktori input di HDFS dan upload file contoh ke HDFS:
   ```bash
   docker exec -it hadoop-namenode bash
   hdfs dfs -mkdir -p /user/hadoop/input
   hdfs dfs -put /data/sample.txt /user/hadoop/input
   ```

**Penjelasan:**
- Perintah ini membuat direktori baru `/user/hadoop/input` di HDFS.
- File `sample.txt` di-upload ke HDFS agar tersedia untuk pemrosesan selanjutnya oleh Spark atau Hive.

#### **2.2. Membaca Data dan Menghitung Baris dengan Spark**
Setelah data diunggah ke HDFS, kita bisa menggunakan Spark untuk melakukan komputasi paralel pada data ini. Contoh sederhana adalah menghitung jumlah baris dalam file menggunakan `spark-shell`.

**Langkah:**
1. Buka `spark-shell` di dalam container `spark-master`:
   ```bash
   docker exec -it spark-master bash
   spark-shell
   ```

2. Baca file dari HDFS dan hitung jumlah baris:
   ```scala
   val data = sc.textFile("hdfs://hadoop-namenode:8020/user/hadoop/input/sample.txt")
   val lineCount = data.count()
   println(s"Jumlah baris: $lineCount")
   ```

**Penjelasan:**
- `sc.textFile` adalah fungsi Spark untuk membaca file teks dari HDFS. File tersebut dipecah menjadi beberapa partisi dan diproses secara paralel.
- `count()` menghitung jumlah baris dalam file tersebut.

#### **2.3. Query SQL dengan Hive**
Hive memungkinkan kita menjalankan query SQL-like di atas data yang disimpan di HDFS. Misalnya, kita bisa membuat tabel di Hive yang menunjuk ke file yang sudah kita upload ke HDFS, lalu menjalankan query untuk melihat data tersebut.

**Langkah:**
1. Masuk ke container `hive-server` dan buka Hive CLI:
   ```bash
   docker exec -it hive-server bash
   hive
   ```

2. Buat tabel Hive yang menunjuk ke file di HDFS dan jalankan query:
   ```sql
   CREATE EXTERNAL TABLE sample_data(line STRING)
   ROW FORMAT DELIMITED
   FIELDS TERMINATED BY '\n'
   LOCATION 'hdfs://hadoop-namenode:8020/user/hadoop/input/';
   
   SELECT * FROM sample_data LIMIT 10;
   ```

**Penjelasan:**
- Tabel eksternal Hive dibuat untuk membaca data dari lokasi tertentu di HDFS.
- Query SQL sederhana dijalankan untuk mengambil 10 baris pertama dari file yang telah di-upload.

---

### 3. **Contoh Penggunaan Kompleks**

Penggunaan kompleks melibatkan pemrosesan data dalam jumlah besar, query analitik yang lebih mendalam, serta penggunaan Spark untuk menjalankan algoritma yang lebih berat.

#### **3.1. Job Spark: Word Count pada File di HDFS**
Spark memungkinkan kita menjalankan job komputasi paralel. Contoh klasik adalah Word Count, di mana kita menghitung jumlah kemunculan setiap kata dalam sebuah file.

**Langkah:**
1. Buka `spark-shell` di `spark-master`:
   ```bash
   docker exec -it spark-master bash
   spark-shell
   ```

2. Jalankan job Word Count:
   ```scala
   val textFile = sc.textFile("hdfs://hadoop-namenode:8020/user/hadoop/input/sample.txt")
   val counts = textFile.flatMap(line => line.split(" "))
                        .map(word => (word, 1))
                        .reduceByKey(_ + _)
   counts.saveAsTextFile("hdfs://hadoop-namenode:8020/user/hadoop/output/wordcount")
   ```

3. Verifikasi hasil Word Count di HDFS:
   ```bash
   docker exec -it hadoop-namenode bash
   hdfs dfs -ls /user/hadoop/output/wordcount
   hdfs dfs -cat /user/hadoop/output/wordcount/part-00000
   ```

**Penjelasan:**
- `flatMap` digunakan untuk memecah setiap baris menjadi kata-kata.
- `map` membuat pasangan (key-value) di mana setiap kata diberi nilai 1.
- `reduceByKey` mengumpulkan nilai untuk setiap kata dan menghitung total kemunculannya.
- Hasilnya disimpan kembali ke HDFS di direktori `wordcount`.

#### **3.2. Query Analitik dengan Hive**
Dalam skenario kompleks, Hive bisa digunakan untuk query analitik yang lebih mendalam seperti agregasi, join, atau filter berdasarkan kondisi tertentu.

**Langkah:**
1. Di Hive CLI, buat tabel baru untuk data transaksi:
   ```sql
   CREATE EXTERNAL TABLE transactions (
     id INT,
     amount FLOAT,
     date STRING
   )
   ROW FORMAT DELIMITED
   FIELDS TERMINATED BY ','
   LOCATION 'hdfs://hadoop-namenode:8020/user/hadoop/transactions/';
   ```

2. Jalankan query untuk menghitung total nilai transaksi:
   ```sql
   SELECT SUM(amount) FROM transactions;
   ```

**Penjelasan:**
- Tabel `transactions` dibuat untuk mewakili data transaksi yang ada di HDFS.
- Query di atas menghitung total nilai transaksi, yang dapat digunakan untuk analisis keuangan atau bisnis.

---

### 4. **Kesimpulan**

Dengan kombinasi Hadoop HDFS, YARN, Spark, dan Hive, kita dapat melakukan berbagai jenis pemrosesan data, dari yang sederhana seperti menghitung baris file, hingga yang kompleks seperti Word Count atau query analitik pada data transaksi. Cluster ini memberikan fleksibilitas dan skalabilitas dalam pemrosesan data skala besar, mendukung berbagai jenis aplikasi dari analitik data hingga machine learning.