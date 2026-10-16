# Transformasi Data: Min-Max Normalization pada Olympic Medal Tally History

**Dataset:** 1.807 baris (negara × edisi Olimpiade, 1896–2022), 9 atribut, tanpa missing value.
**Metode yang dipilih (satu metode):** Min-Max Normalization ke rentang [0, 1].

## 1. Analisis kebutuhan transformasi (Kriteria 1)

| Atribut | Tipe | Perlu ditransformasi? | Alasan |
|---|---|---|---|
| edition, country, country_noc | kategorikal/ID | Tidak | Label teks, bukan besaran numerik. |
| edition_id, year | numerik (identitas/waktu) | Tidak | Berfungsi sebagai kode/penanda waktu; menskalakannya menghilangkan makna tahun. |
| **gold** | numerik rasio | **Ya** | Rentang 0–83, skala berbeda dari `total`; perlu disamakan untuk algoritma berbasis jarak. |
| **silver** | numerik rasio | **Ya** | Rentang 0–85; alasan sama dengan gold. |
| **bronze** | numerik rasio | **Ya** | Rentang 0–83; alasan sama dengan gold. |
| **total** | numerik rasio | **Ya** | Rentang 1–248; skalanya ±3× lebih besar daripada gold/silver/bronze sehingga mendominasi jarak (Euclidean) pada clustering/k-NN. |

Pengecekan kualitas: `gold + silver + bronze = total` berlaku di semua baris, dan tidak ada nilai kosong.
Kebutuhan utama: keempat atribut medali memiliki skala berbeda (maks 83 s.d. 248), sehingga perlu disamakan agar kontribusinya seimbang pada algoritma berbasis jarak/gradien.

## 2. Pemilihan metode (Kriteria 2)

**Min-Max** dipilih karena:
1. Atribut berupa *count* non-negatif dengan **nol bermakna** ("tidak ada medali"); Min-Max menjaga 0 tetap 0 (untuk gold/silver/bronze, min = 0) dan hasilnya mudah dibaca sebagai "proporsi terhadap capaian tertinggi sepanjang sejarah".
2. Hasil terbatas pada [0, 1] — cocok untuk k-NN, k-Means, jaringan saraf, dan visualisasi.
3. Transformasi linear: **bentuk distribusi dan korelasi tidak berubah** (korelasi gold–total 0,9684 sebelum dan sesudah).

Mengapa bukan alternatif: Z-score menghasilkan nilai negatif untuk "0 medali" sehingga kurang intuitif pada data count; diskritisasi membuang informasi selisih jumlah medali; feature construction (mis. rasio medali) berada di luar cakupan "satu metode".

## 3. Proses perhitungan (Kriteria 3)

Rumus: **x′ = (x − min) / (max − min)**

Langkah 1 – Cari parameter (`minmax_parameters.csv`):

| Atribut | min | max | range |
|---|---|---|---|
| gold | 0 | 83 | 83 |
| silver | 0 | 85 | 85 |
| bronze | 0 | 83 | 83 |
| total | 1 | 248 | 247 |

Langkah 2 – Terapkan rumus pada setiap baris. Contoh:

- USA 1896, gold: (11 − 0) / 83 = **0,1325**
- Greece 1896, silver: (18 − 0) / 85 = **0,2118**
- Greece 1896, total: (47 − 1) / 247 = **0,1862**
- Bohemia 1906, total: (2 − 1) / 247 = **0,0040**

Langkah 3 – Verifikasi: nilai min = 0 dan max = 1 untuk semua kolom hasil (lihat `summary_after.csv`).

Seluruh langkah dapat dijalankan ulang dengan `python3 -I transform_minmax.py`.

## 4. Perbandingan sebelum & sesudah

| Atribut | Rentang sebelum | Mean sebelum | Std sebelum | Skew sebelum | Rentang sesudah | Mean sesudah | Std sesudah | Skew sesudah |
|---|---|---|---|---|---|---|---|---|
| gold | 0–83 | 3,737 | 7,554 | 4,745 | 0–1 | 0,0450 | 0,0910 | 4,745 |
| silver | 0–85 | 3,722 | 6,412 | 4,562 | 0–1 | 0,0438 | 0,0754 | 4,562 |
| bronze | 0–83 | 3,971 | 6,170 | 3,870 | 0–1 | 0,0478 | 0,0743 | 3,870 |
| total | 1–248 | 11,430 | 19,423 | 4,467 | 0–1 | 0,0422 | 0,0786 | 4,467 |

Contoh baris (lengkap di `sample_before_after.csv`):

| Negara – Edisi | gold | gold′ | total | total′ |
|---|---|---|---|---|
| United States – 1896 | 11 | 0,1325 | 20 | 0,0769 |
| Greece – 1896 | 10 | 0,1205 | 47 | 0,1862 |
| France – 2008 | 7 | 0,0843 | 43 | 0,1700 |
| Bohemia – 1906 | 0 | 0,0000 | 2 | 0,0040 |

## 5. Justifikasi hasil dan konsekuensi (Kriteria 4)

- **Penjelasan per atribut:** gold, silver, bronze, total diubah menjadi kolom `*_norm` (skala 0–1); atribut asli dipertahankan untuk traceability. edition, edition_id, year, country, country_noc tidak diubah karena merupakan identitas/label.
- **Sesuai tujuan analisis:** skala keempat atribut medali kini sebanding, sehingga `total` tidak lagi mendominasi perhitungan jarak.
- **Konsekuensi/keterbatasan (penting):**
  1. Data sangat *right-skewed* (skewness 3,9–4,7; median gold = 1 vs maks 83). Min-Max sensitif outlier: satu nilai ekstrem (mis. AS/Uni Soviet pada edisi tertentu) membuat mayoritas nilai terkumpul di sekitar 0–0,1 (rata-rata ≈ 0,04). Skewness tidak berubah karena transformasi bersifat linear.
  2. Normalisasi bersifat **global** (lintas semua edisi). Jumlah cabang/medali tiap edisi berbeda (Olimpiade modern jauh lebih banyak daripada 1896), sehingga 0,5 pada 1896 dan 0,5 pada 2020 tidak merepresentasikan dominasi relatif yang sama. Jika analisis membandingkan lintas era, pertimbangkan normalisasi per edisi atau log-transform sebagai lanjutan.
  3. Parameter min/max harus disimpan (`minmax_parameters.csv`) dan dipakai ulang pada data baru; nilai di luar rentang akan keluar dari [0, 1].

## File keluaran

| File | Isi |
|---|---|
| `olympic_medal_tally_minmax.csv` | **Dataset hasil transformasi** (kolom asli + `*_norm`) |
| `olympic_medal_tally_original.csv` | Dataset asli |
| `sample_before_after.csv`, `summary_before.csv`, `summary_after.csv` | Perbandingan sebelum/sesudah |
| `minmax_parameters.csv` | Parameter min/max |
| `transform_minmax.py` | Kode transformasi |
