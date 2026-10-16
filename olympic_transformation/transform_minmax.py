"""Min-Max Normalization pada Olympic Medal Tally History."""
import pandas as pd

df = pd.read_csv("olympic_medal_tally_original.csv")
cols = ["gold", "silver", "bronze", "total"]

# Langkah 1: kondisi sebelum transformasi
print("=== SEBELUM ===")
print(df[cols].agg(["min", "max", "mean", "std"]).T.round(3))

# Langkah 2: menentukan min, max, dan range tiap atribut
params = pd.DataFrame({"min": df[cols].min(), "max": df[cols].max()})
params["range"] = params["max"] - params["min"]
print("\n=== PARAMETER ===")
print(params)

# Langkah 3: menerapkan x' = (x - min) / (max - min)
out = df.copy()
for c in cols:
    out[c + "_norm"] = (df[c] - params.loc[c, "min"]) / params.loc[c, "range"]

print("\n=== CONTOH PERHITUNGAN ===")
for i in [0, 1, 1000]:
    r = df.loc[i]
    for c in cols:
        mn, rg = params.loc[c, "min"], params.loc[c, "range"]
        print(f"{r.country} {r.year} {c}: ({r[c]} - {mn}) / {rg} = {out.loc[i, c + '_norm']:.4f}")

# Langkah 4: kondisi sesudah transformasi
print("\n=== SESUDAH ===")
print(out[[c + "_norm" for c in cols]].agg(["min", "max", "mean", "std"]).T.round(4))

out.round(4).to_csv("olympic_medal_tally_minmax.csv", index=False)
