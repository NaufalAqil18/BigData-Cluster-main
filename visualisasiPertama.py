import pandas as pd
import matplotlib.pyplot as plt

# Membaca data
df = pd.read_csv('~/processed_news/part-00000')

# Visualisasi jumlah kata kunci
df['word_count'] = df['filtered_words'].apply(lambda x: len(x.split()))
df['word_count'].hist(bins=20)
plt.xlabel('Jumlah Kata')
plt.ylabel('Frekuensi')
plt.title('Distribusi Jumlah Kata dalam Judul Berita')
plt.show()
