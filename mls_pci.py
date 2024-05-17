import pathlib

import requests
import pandas as pd

dt_now = pd.Timestamp.now(tz="Asia/Tokyo")

last_year = (dt_now - pd.DateOffset(years=1)).normalize()

start = int(last_year.timestamp())

p_csv = pathlib.Path("map", "mls44011.csv")
p_csv.parent.mkdir(parents=True, exist_ok=True)

url = f"https://44011.brave-hero.net/api/v1/csvexport?mcc=440&mnc=11&after={start}&mlscompatible=on&cellid_after=188743680&cellid_before=190023680"

r = requests.get(url)
r.raise_for_status()

with p_csv.open(mode="wb") as fw:
    fw.write(r.content)

df_mls = pd.read_csv(p_csv, dtype={"unit": str})

df_mls[["eNB", "LCID"]] = df_mls["cell"].apply(lambda x: pd.Series([x >> 8, x & 0xFF]))

df_pci = df_mls.pivot(index="eNB", columns="LCID", values="unit").fillna("-")

pci_json = df_pci.to_json(orient="index", force_ascii=False, indent=4)

p_json = pathlib.Path("map", "pci.json")
p_json.parent.mkdir(parents=True, exist_ok=True)

with open(p_json, "w") as f:
    f.write(pci_json)
