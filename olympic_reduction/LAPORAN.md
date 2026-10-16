# Analisis Redundansi Atribut & Reduksi Data — Olympic Medal Tally History

Dataset: 1.807 baris × 9 atribut (`edition, edition_id, year, country, country_noc, gold, silver, bronze, total`); tidak ada missing value maupun duplikat.
Tujuan analisis yang diasumsikan: **membandingkan prestasi medali antarnegara dari waktu ke waktu**.
Kode: `reduksi.py` · Log lengkap: `output/log_hasil.txt`

## 1. Metode deteksi redundansi (Kriteria 2)
Metode dipilih menurut tipe data, karena korelasi Pearson tidak cocok untuk atribut kategorikal.

| Tipe atribut | Metode | Alasan |
|---|---|---|
| Numerik (`year, gold, silver, bronze, total, edition_id`) | Korelasi Pearson + Spearman, VIF, uji identitas aritmetika | Pearson mengukur hubungan linear; Spearman tahan terhadap distribusi miring (data medali sangat skewed); VIF mendeteksi multikolinearitas; uji identitas membuktikan apakah satu kolom benar-benar turunan dari kolom lain |
| Kategorikal / identifier (`edition, edition_id, country, country_noc`) | Ketergantungan fungsional (apakah A→B dan B→A), jumlah nilai unik, Cramér's V | Kolom bertipe teks/ID tidak bisa dikorelasikan secara numerik |

## 2. Hasil deteksi & keputusan per atribut (Kriteria 1 & 4)
Prinsip: korelasi tinggi **tidak otomatis berarti dihapus**. Setiap pasangan ditinjau isi dan maknanya.

| Pasangan | Bukti | Kesimpulan | Keputusan |
|---|---|---|---|
| `total` vs `gold+silver+bronze` | `total = gold+silver+bronze` benar pada 1807/1807 baris; VIF ≈ 10¹⁵ (kolinearitas sempurna) | **Redundan sejati** (informasi 100% turunan) | Hapus `total` (bisa dihitung ulang kapan saja) |
| `country` vs `country_noc` | 154 nilai unik masing-masing, A→B dan B→A, Cramér's V = 1 | **Redundan sejati** (nama vs kode) | Hapus `country_noc`, pertahankan `country` yang lebih mudah dibaca |
| `edition` vs `edition_id` | 55 vs 55, pemetaan 1:1 | **Redundan sejati** (label vs nomor urut) | Hapus `edition_id` |
| `edition` vs `year` | `edition` = tahun + jenis ajang ("1924 Winter Olympics"); tahun di string selalu = `year` | **Redundan sebagian**: bagian tahun duplikat, bagian jenis ajang unik | Ekstrak jenis ajang menjadi `season`, hapus `edition`, pertahankan `year` |
| `year` vs `edition_id` | r = 0,80 (Pearson), 0,88 (Spearman); 38 tahun vs 55 edisi | **Hubungan kuat, BUKAN informasi sama**: tahun 1924–1992 punya 2–3 edisi (Summer + Winter, bahkan Intercalated/Equestrian). `year` tidak bisa menggantikan `edition` | `year` dipertahankan; yang dihapus `edition_id` (karena 1:1 dengan edition) |
| `gold` vs `silver` vs `bronze` | r = 0,87–0,92 (Pearson), 0,65–0,70 (Spearman), VIF 5,6–8,2 | **Hubungan kuat, BUKAN redundan**: korelasi muncul karena negara besar menang banyak di semua jenis medali (efek ukuran), tapi maknanya berbeda (emas ≠ perak ≠ perunggu) dan rasionya penting | Dipertahankan semua |

Catatan temuan: korelasi Pearson gold–silver (0,92) jauh lebih tinggi dari Spearman (0,70) → korelasi didorong oleh sedikit negara dengan medali sangat banyak (AS, Uni Soviet), bukan oleh hubungan yang merata di seluruh data. Ini alasan tambahan tidak menghapus salah satunya.

Visual: `output/01_korelasi.png`.

## 3. Metode reduksi (Kriteria 3 & 4)
**Metode utama: Agregasi** (didahului reduksi atribut).

1. **Reduksi atribut** (hapus `total`, `country_noc`, `edition_id`, `edition`; tambah `season`) → 1807 × 6. Dataset: `output/olympic_tahap1_atribut_tereduksi.csv`.
2. **Agregasi per negara** (`groupby country`): jumlah gold/silver/bronze, `n_edisi`, `tahun_pertama`, `tahun_terakhir`, `n_summer`, `n_winter`, serta fitur turunan `gold_share` (gold/total medali) dan `medali_per_edisi`. → **154 × 11**. Dataset: `output/olympic_tahap2_agregasi_per_negara.csv`.

**Mengapa agregasi?**
- Tujuan analisis adalah level negara, sementara data aslinya berbentuk *negara × edisi* sehingga satu negara muncul belasan–puluhan kali.
- Atribut sudah bersifat penjumlahan (count), jadi agregasi dengan `sum` tidak menghilangkan informasi medali. Validasi: total emas/perak/perunggu sebelum dan sesudah **identik** (dicek dengan `assert`).
- `gold_share` mempertahankan informasi komposisi medali yang akan hilang jika memakai PCA.

**Mengapa bukan PCA?** Diuji sebagai pembanding (`output/03_pca.png`): PC1 menangkap 93% varians, loading ≈ sama (0,58/0,58/0,57), artinya hanya "skala prestasi". Namun hanya ada 3 atribut numerik yang bermakna, PC tidak dapat diinterpretasi, dan informasi komposisi (emas vs perunggu) hilang. PCA juga tidak menyentuh redundansi kategorikal (`country`/`NOC`).
**Mengapa bukan sampling?** Tidak ada masalah volume (1.807 baris kecil), dan sampling acak akan membuang edisi/negara kecil (misalnya negara yang hanya sekali menang medali), sehingga bias.

## 4. Perbandingan sebelum vs sesudah

| | Asli | Tahap 1 (atribut) | Tahap 2 (agregasi) |
|---|---|---|---|
| Baris | 1.807 | 1.807 | **154** (−91,5%) |
| Atribut | 9 | 6 | 11 (termasuk 4 fitur turunan) |
| Jumlah sel | 16.263 | 10.842 | **1.694** (−89,6%) |
| Memori | 401 KB | 272 KB | **21 KB** |
| Pasangan |r|>0,9 | 4 | – | – |
| VIF maksimum | ~10¹⁵ | – | – |
| Total emas/perak/perunggu | identik | identik | identik |

Visual: `output/02_sebelum_sesudah.png`.

## 5. Keterbatasan (perlu disampaikan jujur)
- Agregasi menghilangkan dimensi **waktu** per edisi (tren per tahun); hanya `tahun_pertama/terakhir` dan jumlah edisi yang tersisa. Jika tujuannya analisis tren, gunakan dataset tahap 1.
- Pada level negara, `gold/silver/bronze` justru jadi **sangat kolinear** (VIF 72–229) karena efek ukuran negara. Jika dataset ini dipakai untuk regresi/klastering, langkah lanjut yang tepat adalah PCA atau memakai rasio (`gold_share`, `medali_per_edisi`) daripada hitungan mentah.
- Negara historis (Uni Soviet, Jerman Timur/Barat) tercatat sebagai entitas terpisah; tidak digabung karena bukan sumber redundansi dalam data.
