# Analisis Redundansi Atribut & Reduksi Data — Olympic Medal Tally History

Dataset: 1.807 baris × 9 atribut (`edition, edition_id, year, country, country_noc, gold, silver, bronze, total`).
Tujuan analisis: **membandingkan perolehan medali antarnegara**.
Kode: `reduksi.py` · Log: `output/log_hasil.txt`

## 1. Metode deteksi redundansi (Kriteria 2)
| Tipe atribut | Metode | Alasan |
|---|---|---|
| Numerik (`edition_id, year, gold, silver, bronze, total`) | Korelasi Pearson (`output/korelasi.png`) | Mengukur kekuatan hubungan linear antar-atribut numerik |
| Kategorikal/identifier (`country, country_noc, edition, edition_id, year`) | Pengecekan pemetaan 1:1 antar-nilai | Atribut teks/ID tidak dapat dikorelasikan; dua atribut membawa informasi yang sama jika setiap nilai yang satu selalu berpasangan dengan tepat satu nilai yang lain, dan sebaliknya |

## 2. Hasil identifikasi redundansi & keputusan (Kriteria 1 & 4)
| Atribut | Hasil deteksi | Tinjauan isi & makna | Keputusan |
|---|---|---|---|
| `total` | r = 0,95–0,97 dengan gold/silver/bronze | Dicek isinya: `total = gold+silver+bronze` di 1807/1807 baris. Informasinya sama persis, hanya hasil penjumlahan | **Hapus** |
| `country_noc` | Pemetaan 1:1 dengan `country` (154 = 154) | Kode NOC hanyalah singkatan nama negara | **Hapus** (pertahankan `country`) |
| `edition_id` | Pemetaan 1:1 dengan `edition` (55 = 55) | Nomor urut dari edisi yang sama | **Hapus** (pertahankan `edition`) |
| `year` | r = 0,80 dengan `edition_id` | Hubungan kuat tetapi **bukan informasi yang sama**: satu tahun bisa memiliki 2–3 edisi (Summer & Winter pada 1924–1992) | **Pertahankan** |
| `gold`, `silver`, `bronze` | r = 0,87–0,92 satu sama lain | Hubungan kuat karena negara kuat cenderung meraih banyak medali semua jenis, tetapi **maknanya berbeda** (tingkat prestasi berbeda) dan semuanya relevan untuk membandingkan negara | **Pertahankan** |

## 3. Metode reduksi: Agregasi (Kriteria 3 & 4)
Data dijumlahkan (`sum`) per `country` untuk `gold`, `silver`, dan `bronze`.

Alasan pemilihan:
- Tujuan analisis berada di tingkat negara, sedangkan data asli tercatat per negara per edisi. Satu negara muncul berulang kali (hingga 53 baris).
- Atribut medali berupa hitungan, jadi agregasi `sum` tidak menghilangkan informasi medali. Total medali sebelum dan sesudah agregasi identik.
- `edition` dan `year` tidak ikut dalam hasil karena tidak relevan untuk perbandingan total antarnegara.

Alasan tidak memilih metode lain:
- **PCA**: hanya ada 3 atribut numerik bermakna (gold, silver, bronze). Komponen hasil PCA sulit diinterpretasikan dan menghilangkan perbedaan makna antar-jenis medali.
- **Sampling**: jumlah datanya kecil, dan sampling bisa membuang negara yang jarang meraih medali sehingga perbandingan menjadi bias.

Dataset hasil reduksi: `output/dataset_hasil_reduksi.csv` (154 baris × 4 atribut: `country, gold, silver, bronze`).

## 4. Perbandingan sebelum dan sesudah reduksi
| | Sebelum | Sesudah |
|---|---|---|
| Jumlah baris | 1.807 | 154 |
| Jumlah atribut | 9 | 4 |
| Jumlah sel | 16.263 | 616 |
| Total emas | 6.753 | 6.753 |
| Total perak | 6.725 | 6.725 |
| Total perunggu | 7.176 | 7.176 |
