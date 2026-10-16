"""Analisis redundansi atribut & reduksi data - Olympic Medal Tally History."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif_fn

OUT = "output/"
df = pd.read_csv("Olympic_Medal_Tally_History.csv")
ORIG = df.copy()
log = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); log.append(s)

P("="*70, "\n0. KONDISI AWAL\n", "="*70)
P("Shape:", df.shape, "| missing:", int(df.isna().sum().sum()), "| duplikat baris:", int(df.duplicated().sum()))
P("Memori (KB):", round(df.memory_usage(deep=True).sum()/1024, 1))
P(df.dtypes.to_string())

# ---------------- 1. Atribut numerik: korelasi + VIF ----------------
P("\n", "="*70, "\n1. ATRIBUT NUMERIK: KORELASI PEARSON/SPEARMAN & VIF\n", "="*70)
num = ["edition_id", "year", "gold", "silver", "bronze", "total"]
pear, spear = df[num].corr(), df[num].corr(method="spearman")
P("Pearson:\n", pear.round(3).to_string()); P("\nSpearman:\n", spear.round(3).to_string())
X = df[num].astype(float).assign(const=1.0)
vif = pd.Series([vif_fn(X.values, i) for i in range(len(num))], index=num)
P("\nVIF (semua numerik):\n", vif.round(2).to_string())
P("\nCek identitas: total == gold+silver+bronze pada", int((df.total == df.gold+df.silver+df.bronze).sum()), "/", len(df), "baris")
m3 = ["gold", "silver", "bronze"]
vif3 = pd.Series([vif_fn(df[m3].astype(float).assign(c=1.0).values, i) for i in range(3)], index=m3)
P("VIF tanpa 'total':\n", vif3.round(2).to_string())
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for a, m, t in zip(ax, [pear, spear], ["Pearson", "Spearman"]):
    sns.heatmap(m, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=a, cbar=False); a.set_title(t)
plt.tight_layout(); plt.savefig(OUT+"01_korelasi.png", dpi=130); plt.close()

# ---------------- 2. Atribut kategorikal: functional dependency, Cramer's V ----------------
P("\n", "="*70, "\n2. ATRIBUT KATEGORIKAL/IDENTIFIER: KETERGANTUNGAN FUNGSIONAL & CRAMER'S V\n", "="*70)
def cramers_v(a, b):
    ct = pd.crosstab(a, b); chi2 = ((ct - np.outer(ct.sum(1), ct.sum(0))/ct.values.sum())**2 /
        (np.outer(ct.sum(1), ct.sum(0))/ct.values.sum())).values.sum()
    n = ct.values.sum(); k = min(ct.shape)-1
    return np.sqrt(chi2/(n*k))
def fd(a, b):  # apakah a -> b (tiap nilai a hanya punya satu b)?
    return df.groupby(a)[b].nunique().max() == 1
df["season"] = df.edition.str.replace(r"^\d{4} ", "", regex=True)
rows = []
for a, b in [("country", "country_noc"), ("edition", "edition_id"), ("edition_id", "year"), ("year", "edition_id"),
             ("edition", "year"), ("year", "edition"), ("edition_id", "season"), ("year", "season")]:
    rows.append(dict(A=a, B=b, **{"A->B": fd(a, b), "B->A": fd(b, a), "CramersV": round(cramers_v(df[a], df[b]), 3),
                     "n_unik_A": df[a].nunique(), "n_unik_B": df[b].nunique()}))
fdt = pd.DataFrame(rows); P(fdt.to_string(index=False))
P("\nContoh: tahun dengan >1 edisi (Summer+Winter / Intercalated / Equestrian):")
P(df.groupby("year").edition.unique().loc[lambda s: s.map(len) > 1].head(6).to_string())
P("\nIsi 'edition' =", "tahun + jenis ajang. Jenis ajang:", df.season.value_counts().to_dict())
chk = df.edition.str[:4].astype(int).eq(df.year).all()
P("Tahun di awal string 'edition' selalu sama dengan 'year':", chk)

# ---------------- 3. Keputusan atribut ----------------
P("\n", "="*70, "\n3. KEPUTUSAN ATRIBUT (pertahankan/hapus)\n", "="*70)
decision = pd.DataFrame([
 ["total", "HAPUS", "Identitas aritmetika total = gold+silver+bronze (100% baris), VIF tinggi. Informasi 100% turunan (redundan sejati)."],
 ["country_noc", "HAPUS", "Pemetaan 1:1 dengan country (154=154, Cramer's V=1). Sama persis; NOC disimpan hanya sebagai kunci kode bila perlu."],
 ["edition_id", "HAPUS", "Pemetaan 1:1 dengan edition (55=55). ID urut tanpa makna analitik selain label edisi."],
 ["edition", "HAPUS (setelah diekstrak)", "Berisi year + jenis ajang. Year dipertahankan terpisah; jenis ajang diekstrak menjadi 'season'."],
 ["year", "PERTAHANKAN", "Korelasi sangat tinggi dg edition_id (r~1) TAPI BUKAN redundan penuh: 1 tahun dapat memiliki >1 edisi (Summer & Winter). Membawa makna waktu numerik."],
 ["season (baru)", "TAMBAH", "Hasil ekstraksi dari edition: Summer/Winter/Intercalated/Equestrian. Informasi yang tidak ada di year."],
 ["country", "PERTAHANKAN", "Kunci entitas analisis."],
 ["gold, silver, bronze", "PERTAHANKAN", "Korelasi tinggi (r~0.8-0.9) tapi MAKNA berbeda (kualitas medali). Hubungan kuat, bukan informasi sama -> tidak dihapus."],
], columns=["Atribut", "Keputusan", "Justifikasi"])
P(decision.to_string(index=False))

# ---------------- 4. Uji PCA pada gold/silver/bronze (pembanding) ----------------
P("\n", "="*70, "\n4. UJI PEMBANDING: PCA pada gold/silver/bronze\n", "="*70)
Z = StandardScaler().fit_transform(df[m3]); pca = PCA().fit(Z)
ev = pca.explained_variance_ratio_
P("Explained variance ratio:", ev.round(3), "| kumulatif:", ev.cumsum().round(3))
P("Loading PC1:", dict(zip(m3, pca.components_[0].round(3))))
P("-> PC1 menangkap ~%.0f%% varians tetapi hanya 'ukuran/skala prestasi'; informasi komposisi medali (rasio emas/perak/perunggu) hilang dan PC tidak dapat diinterpretasi." % (ev[0]*100))

# ---------------- 5. Reduksi tahap 1: reduksi atribut ----------------
stage1 = df[["year", "season", "country", "gold", "silver", "bronze"]].copy()
stage1.to_csv(OUT+"olympic_tahap1_atribut_tereduksi.csv", index=False)

# ---------------- 6. Reduksi tahap 2: agregasi per negara ----------------
g = stage1.groupby("country")
agg = pd.DataFrame({
    "gold": g.gold.sum(), "silver": g.silver.sum(), "bronze": g.bronze.sum(),
    "n_edisi": g.size(), "tahun_pertama": g.year.min(), "tahun_terakhir": g.year.max(),
    "n_summer": g.season.apply(lambda s: (s == "Summer Olympics").sum()),
    "n_winter": g.season.apply(lambda s: (s == "Winter Olympics").sum()),
}).reset_index()
tot = agg.gold + agg.silver + agg.bronze
agg["gold_share"] = (agg.gold / tot).round(4)          # komposisi medali (rasio, menggantikan 'total')
agg["medali_per_edisi"] = (tot / agg.n_edisi).round(2)  # intensitas prestasi
agg = agg.sort_values("gold", ascending=False).reset_index(drop=True)
agg.to_csv(OUT+"olympic_tahap2_agregasi_per_negara.csv", index=False)
assert agg.gold.sum() == df.gold.sum() and agg.silver.sum() == df.silver.sum() and agg.bronze.sum() == df.bronze.sum()
P("\n", "="*70, "\n5-6. DATASET HASIL REDUKSI (head)\n", "="*70); P(agg.head(8).to_string(index=False))
P("Validasi: total medali emas/perak/perunggu sebelum = sesudah agregasi (tidak ada informasi medali hilang).")

# ---------------- 7. Perbandingan sebelum vs sesudah ----------------
def mem(d): return round(d.memory_usage(deep=True).sum()/1024, 1)
agg_corr = agg[["gold", "silver", "bronze", "n_edisi", "n_summer", "n_winter", "medali_per_edisi"]].corr()
cmp = pd.DataFrame({
 "Asli": [ORIG.shape[0], 9, ORIG.size, mem(ORIG), int((pear.abs().where(~np.eye(6, dtype=bool)) > .9).sum().sum()//2), round(vif.max(), 1)],
 "Tahap 1 (atribut)": [stage1.shape[0], stage1.shape[1], stage1.size, mem(stage1), "-", "-"],
 "Tahap 2 (agregasi)": [agg.shape[0], agg.shape[1], agg.size, mem(agg), "-", "-"],
}, index=["Jumlah baris", "Jumlah atribut", "Jumlah sel", "Memori (KB)", "Pasangan |r|>0.9 (asli)", "VIF maksimum (asli)"])
P("\n", "="*70, "\n7. PERBANDINGAN SEBELUM vs SESUDAH\n", "="*70); P(cmp.to_string())
P("Reduksi sel: %.1f%%  | reduksi baris: %.1f%%" % ((1-agg.size/(df.shape[0]*9))*100, (1-len(agg)/len(df))*100))
v2 = [vif_fn(agg[["gold", "silver", "bronze"]].astype(float).assign(c=1.0).values, i) for i in range(3)]
P("VIF gold/silver/bronze (level negara):", np.round(v2, 2))

fig, ax = plt.subplots(1, 3, figsize=(14, 4))
ax[0].bar(["Asli", "Tahap 1", "Tahap 2"], [df.shape[0], stage1.shape[0], agg.shape[0]], color=["#888", "#888", "#2a6"]); ax[0].set_title("Jumlah baris")
ax[1].bar(["Asli", "Tahap 1", "Tahap 2"], [9, 6, agg.shape[1]], color=["#888", "#2a6", "#2a6"]); ax[1].set_title("Jumlah atribut")
ax[2].bar(["Asli", "Tahap 1", "Tahap 2"], [df.size, stage1.size, agg.size], color=["#888", "#2a6", "#2a6"]); ax[2].set_title("Jumlah sel")
for a in ax: a.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(OUT+"02_sebelum_sesudah.png", dpi=130); plt.close()
fig, ax = plt.subplots(figsize=(5, 4)); ax.bar(range(1, 4), ev, color="#2a6"); ax.set_title("PCA gold/silver/bronze (varians)")
ax.set_xlabel("PC"); ax.spines[["top", "right"]].set_visible(False); plt.tight_layout(); plt.savefig(OUT+"03_pca.png", dpi=130)
decision.to_csv(OUT+"keputusan_atribut.csv", index=False); fdt.to_csv(OUT+"uji_ketergantungan_kategorikal.csv", index=False)
cmp.to_csv(OUT+"perbandingan_sebelum_sesudah.csv")
open(OUT+"log_hasil.txt", "w").write("\n".join(log))
