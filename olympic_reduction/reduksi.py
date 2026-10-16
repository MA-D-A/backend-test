"""Analisis redundansi atribut & reduksi data (agregasi) - Olympic Medal Tally History."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns

df = pd.read_csv("Olympic_Medal_Tally_History.csv")
log = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); log.append(s)

# 1. Deteksi redundansi atribut numerik: korelasi Pearson
num = ["edition_id", "year", "gold", "silver", "bronze", "total"]
corr = df[num].corr()
P("1. KORELASI PEARSON (atribut numerik)\n", corr.round(3).to_string())
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1)
plt.title("Korelasi Pearson"); plt.tight_layout(); plt.savefig("output/korelasi.png", dpi=130); plt.close()

# Tinjau isi: apakah total benar-benar turunan dari gold+silver+bronze?
P("\ntotal == gold+silver+bronze:", int((df.total == df.gold + df.silver + df.bronze).sum()), "dari", len(df), "baris")

# 2. Deteksi redundansi atribut kategorikal/identifier: cek pemetaan 1:1
def map_1_1(a, b):
    return df.groupby(a)[b].nunique().max() == 1, df.groupby(b)[a].nunique().max() == 1
P("\n2. PEMETAAN ANTAR-ATRIBUT KATEGORIKAL/IDENTIFIER")
for a, b in [("country", "country_noc"), ("edition", "edition_id"), ("year", "edition_id"), ("year", "edition")]:
    ab, ba = map_1_1(a, b)
    P(f"{a} ({df[a].nunique()} unik) -> {b} ({df[b].nunique()} unik): {a}->{b}={ab}, {b}->{a}={ba}")
P("\nTahun dengan lebih dari satu edisi:")
P(df.groupby("year").edition.unique().loc[lambda s: s.map(len) > 1].to_string())

# 3. Hapus atribut yang terbukti redundan
reduced_attr = df.drop(columns=["total", "country_noc", "edition_id"])

# 4. Reduksi data: agregasi per negara
hasil = (reduced_attr.groupby("country")[["gold", "silver", "bronze"]].sum()
         .sort_values(["gold", "silver", "bronze"], ascending=False).reset_index())
hasil.to_csv("output/dataset_hasil_reduksi.csv", index=False)

# 5. Perbandingan sebelum vs sesudah
P("\n5. PERBANDINGAN SEBELUM vs SESUDAH")
cmp = pd.DataFrame({"Sebelum": [df.shape[0], df.shape[1], df.size, df.gold.sum(), df.silver.sum(), df.bronze.sum()],
                    "Sesudah": [hasil.shape[0], hasil.shape[1], hasil.size, hasil.gold.sum(), hasil.silver.sum(), hasil.bronze.sum()]},
                   index=["Jumlah baris", "Jumlah atribut", "Jumlah sel", "Total emas", "Total perak", "Total perunggu"])
P(cmp.to_string())
P("\nDataset hasil reduksi (10 teratas):\n", hasil.head(10).to_string(index=False))
open("output/log_hasil.txt", "w").write("\n".join(log))
