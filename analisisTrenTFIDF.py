from pyspark.ml.feature import HashingTF, IDF
from pyspark.ml import Pipeline
from pyspark.sql.functions import col

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

# Menampilkan hasil TF-IDF
rescaledData.select("filtered_words", "features").show(5)
