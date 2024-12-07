from pyspark.ml.feature import HashingTF, IDF

# Menghitung Term Frequency (TF)
hashingTF = HashingTF(inputCol="filtered_words", outputCol="rawFeatures", numFeatures=1000)
featurizedData = hashingTF.transform(df_filtered)

# Menghitung Inverse Document Frequency (IDF)
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

# Menampilkan hasil TF-IDF
rescaledData.select("filtered_words", "features").show(5)
