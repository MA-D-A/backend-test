"""Transformasi Min-Max Normalization pada Olympic Medal Tally History."""
import pandas as pd

df = pd.read_csv("olympic_medal_tally_original.csv")
cols = ["gold", "silver", "bronze", "total"]

# Langkah 1: profil data sebelum transformasi
before = df[cols].agg(["count", "min", "max", "mean", "median", "std", "skew"]).T
print("=== SEBELUM ===\n", before.round(3))
print("Missing:", df.isna().sum().sum(), "| gold+silver+bronze==total:",
      (df.gold + df.silver + df.bronze == df.total).all())

# Langkah 2: simpan min & max tiap atribut
params = pd.DataFrame({"min": df[cols].min(), "max": df[cols].max()})
params["range"] = params["max"] - params["min"]
print("\n=== PARAMETER ===\n", params)

# Langkah 3: x' = (x - min) / (max - min)
out = df.copy()
for c in cols:
    out[c + "_norm"] = (df[c] - params.loc[c, "min"]) / params.loc[c, "range"]

# Langkah 4: contoh perhitungan manual (5 baris)
print("\n=== CONTOH PERHITUNGAN ===")
for i in [0, 1, 2, 3, 1000]:
    r = df.loc[i]
    print(f"{r.country} {r.year}: gold={r.gold} -> ({r.gold}-{params.loc['gold','min']})/"
          f"{params.loc['gold','range']} = {out.loc[i,'gold_norm']:.4f}")

# Langkah 5: profil sesudah
after = out[[c + "_norm" for c in cols]].agg(["min", "max", "mean", "median", "std", "skew"]).T
print("\n=== SESUDAH ===\n", after.round(4))
print("Korelasi gold~total sebelum/sesudah:",
      round(df.gold.corr(df.total), 6), round(out.gold_norm.corr(out.total_norm), 6))

out.round(6).to_csv("olympic_medal_tally_minmax.csv", index=False)
before.round(4).to_csv("summary_before.csv")
after.round(4).to_csv("summary_after.csv")
params.to_csv("minmax_parameters.csv")
# 10 baris contoh sebelum vs sesudah
cmp = out.loc[[0,1,2,3,100,500,1000,1500,1700,1806],
    ["edition","country"]+sum([[c,c+"_norm"] for c in cols],[])]
cmp.round(4).to_csv("sample_before_after.csv", index=False)
print("\n", cmp.round(4).to_string())
