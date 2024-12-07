from pyspark.ml.feature import Tokenizer, StopWordsRemover

# Tokenisasi
tokenizer = Tokenizer(inputCol="title", outputCol="words")
df_tokenized = tokenizer.transform(df_clean)

# Menghapus stopwords
remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
df_filtered = remover.transform(df_tokenized)

# Menampilkan hasil
df_filtered.select("title", "filtered_words").show(5)
