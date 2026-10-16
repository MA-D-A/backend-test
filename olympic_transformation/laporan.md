# Transformasi Data – Olympic Medal Tally History

**Dataset:** 1.807 baris (negara per edisi Olimpiade, 1896–2022), 9 atribut.
**Metode yang dipilih:** Min-Max Normalization ke rentang [0, 1].

---

## Kriteria 1 – Analisis Kebutuhan Transformasi

| Atribut | Jenis | Ditransformasi? | Alasan |
|---|---|---|---|
| edition | kategorikal | Tidak | Nama edisi (teks), bukan besaran numerik. |
| edition_id | numerik (kode) | Tidak | Nomor identitas edisi; tidak memiliki makna besaran. |
| year | numerik (waktu) | Tidak | Penanda waktu; jika diskalakan, makna tahun hilang. |
| country | kategorikal | Tidak | Nama negara (teks). |
| country_noc | kategorikal | Tidak | Kode negara (teks). |
| gold | numerik | **Ya** | Rentang 0–83; skalanya berbeda dari `total`. |
| silver | numerik | **Ya** | Rentang 0–85; skalanya berbeda dari `total`. |
| bronze | numerik | **Ya** | Rentang 0–83; skalanya berbeda dari `total`. |
| total | numerik | **Ya** | Rentang 1–248, sekitar tiga kali lipat atribut medali lain. |

Keempat atribut medali memiliki rentang yang berbeda. Jika dipakai bersama pada analisis berbasis jarak (misalnya clustering atau k-NN), atribut `total` akan paling menentukan hasil hanya karena angkanya lebih besar. Karena itu, keempat atribut ini perlu disamakan skalanya.

---

## Kriteria 2 – Pemilihan Metode Transformasi

Metode yang dipilih adalah **Min-Max Normalization**, dengan alasan:

1. Atribut medali berupa hitungan (count) yang tidak pernah negatif, dan nilai 0 bermakna "tidak mendapat medali". Dengan Min-Max, nilai 0 pada gold, silver, dan bronze tetap 0.
2. Hasilnya berada pada rentang tetap [0, 1], sehingga keempat atribut memiliki skala yang sama.
3. Transformasinya linear, sehingga urutan nilai dan hubungan antaratribut tidak berubah.

---

## Kriteria 3 – Proses Perhitungan

**Rumus:**

x′ = (x − min) / (max − min)

**Langkah 1 – Menentukan nilai min, max, dan range setiap atribut**

| Atribut | min | max | range (max − min) |
|---|---|---|---|
| gold | 0 | 83 | 83 |
| silver | 0 | 85 | 85 |
| bronze | 0 | 83 | 83 |
| total | 1 | 248 | 247 |

**Langkah 2 – Menerapkan rumus pada setiap nilai**

United States 1896 (gold = 11, silver = 7, bronze = 2, total = 20):
- gold′ = (11 − 0) / 83 = **0,1325**
- silver′ = (7 − 0) / 85 = **0,0824**
- bronze′ = (2 − 0) / 83 = **0,0241**
- total′ = (20 − 1) / 247 = **0,0769**

Greece 1896 (gold = 10, silver = 18, bronze = 19, total = 47):
- gold′ = (10 − 0) / 83 = **0,1205**
- silver′ = (18 − 0) / 85 = **0,2118**
- bronze′ = (19 − 0) / 83 = **0,2289**
- total′ = (47 − 1) / 247 = **0,1862**

France 2008 (gold = 7, silver = 16, bronze = 20, total = 43):
- gold′ = (7 − 0) / 83 = **0,0843**
- silver′ = (16 − 0) / 85 = **0,1882**
- bronze′ = (20 − 0) / 83 = **0,2410**
- total′ = (43 − 1) / 247 = **0,1700**

**Langkah 3 – Memeriksa hasil**

Setelah transformasi, nilai minimum setiap atribut menjadi 0 dan nilai maksimumnya menjadi 1.

Seluruh langkah ini diterapkan pada 1.807 baris menggunakan `transform_minmax.py`.

---

## Kriteria 4 – Justifikasi Hasil

- **Karakteristik data:** atribut medali berupa hitungan non-negatif dengan rentang berbeda (maksimum 83, 85, 83, dan 248). Min-Max cocok untuk data seperti ini karena nilai 0 tetap 0 dan semua atribut dibawa ke rentang yang sama.
- **Tujuan analisis:** agar gold, silver, bronze, dan total dapat dibandingkan dan digunakan bersama dengan bobot skala yang setara, tanpa ada satu atribut yang mendominasi karena besar angkanya.
- **Konsekuensi transformasi:**
  1. Min-Max sensitif terhadap nilai ekstrem. Sebagian besar negara hanya meraih sedikit medali (median gold = 1), sementara nilai maksimumnya 83. Akibatnya, sebagian besar nilai hasil transformasi menumpuk di dekat 0 (rata-rata sekitar 0,04).
  2. Bentuk sebaran data tidak berubah karena transformasinya linear; data tetap miring ke kanan.
  3. Normalisasi dihitung dari seluruh edisi sekaligus. Jumlah medali yang tersedia berbeda antaredisi, sehingga nilai yang sama pada edisi yang berbeda tidak selalu menunjukkan tingkat dominasi yang sama.

---

## Output

### a. Dataset hasil transformasi

File `olympic_medal_tally_minmax.csv` berisi semua kolom asli ditambah empat kolom hasil normalisasi: `gold_norm`, `silver_norm`, `bronze_norm`, dan `total_norm`.

### b. Perbandingan sebelum dan sesudah transformasi

**Statistik ringkas**

| Atribut | Min sebelum | Max sebelum | Mean sebelum | Std sebelum | Min sesudah | Max sesudah | Mean sesudah | Std sesudah |
|---|---|---|---|---|---|---|---|---|
| gold | 0 | 83 | 3,737 | 7,554 | 0 | 1 | 0,0450 | 0,0910 |
| silver | 0 | 85 | 3,722 | 6,412 | 0 | 1 | 0,0438 | 0,0754 |
| bronze | 0 | 83 | 3,971 | 6,170 | 0 | 1 | 0,0478 | 0,0743 |
| total | 1 | 248 | 11,430 | 19,423 | 0 | 1 | 0,0422 | 0,0786 |

**Contoh data**

| Edisi | Negara | gold | gold′ | silver | silver′ | bronze | bronze′ | total | total′ |
|---|---|---|---|---|---|---|---|---|---|
| 1896 Summer | United States | 11 | 0,1325 | 7 | 0,0824 | 2 | 0,0241 | 20 | 0,0769 |
| 1896 Summer | Greece | 10 | 0,1205 | 18 | 0,2118 | 19 | 0,2289 | 47 | 0,1862 |
| 1896 Summer | Germany | 6 | 0,0723 | 5 | 0,0588 | 2 | 0,0241 | 13 | 0,0486 |
| 1924 Summer | Finland | 14 | 0,1687 | 13 | 0,1529 | 10 | 0,1205 | 37 | 0,1457 |
| 1972 Summer | Austria | 0 | 0,0000 | 1 | 0,0118 | 2 | 0,0241 | 3 | 0,0081 |
| 2008 Summer | France | 7 | 0,0843 | 16 | 0,1882 | 20 | 0,2410 | 43 | 0,1700 |
| 2014 Winter | United States | 9 | 0,1084 | 9 | 0,1059 | 10 | 0,1205 | 28 | 0,1093 |

### c. Penjelasan perubahan pada setiap atribut

| Atribut | Perubahan |
|---|---|
| edition, edition_id, year, country, country_noc | Tidak diubah. |
| gold | Dibagi 83 (min = 0), sehingga berubah dari rentang 0–83 menjadi 0–1. |
| silver | Dibagi 85 (min = 0), sehingga berubah dari rentang 0–85 menjadi 0–1. |
| bronze | Dibagi 83 (min = 0), sehingga berubah dari rentang 0–83 menjadi 0–1. |
| total | Dikurangi 1 lalu dibagi 247, sehingga berubah dari rentang 1–248 menjadi 0–1. |
