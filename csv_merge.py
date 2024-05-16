import pathlib
import pandas as pd

df1 = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN5xiHhlnPTkv3auHkYLT9NPvvjayj5AdPrH5VBQdbELOzfONi236Vub6eSshv8jAxQw3V1rgbbgE/pub?gid=0&single=true&output=csv",
    parse_dates=["更新日時"],
    dtype={"sector": "Int64", "sub6": "Int64", "ミリ波": "Int64"},
)

df2 = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN5xiHhlnPTkv3auHkYLT9NPvvjayj5AdPrH5VBQdbELOzfONi236Vub6eSshv8jAxQw3V1rgbbgE/pub?gid=882951423&single=true&output=csv",
    parse_dates=["更新日時"],
    dtype={"sector": "Int64", "sub6": "Int64", "ミリ波": "Int64"},
).sort_values("更新日時")

# ID、投稿者のみ
df3 = df2[["ID", "投稿者"]].copy()

# 投稿者なしは削除
df3.dropna(subset="投稿者", inplace=True)

# 複数人を分割
df3["投稿者"] = df3["投稿者"].str.split()

# 投稿者展開後、同一地点の重複を削除
df4 = df3.explode("投稿者").drop_duplicates()

# 前後の空白を削除
df4["投稿者"] = df4["投稿者"].str.strip()

# 協力者でひとつにまとめる
collaborator = (
    df4.groupby("ID")["投稿者"].apply(lambda x: " ".join(x)).rename("協力者")
)

# 最新情報のみ残す
df2.drop_duplicates(subset="ID", keep="last", inplace=True)

df5 = (
    df1.reindex(
        columns=[
            "ID",
            "場所",
            "市区町村",
            "設置タイプ",
            "状況",
            "sector",
            "sub6",
            "ミリ波",
            "eNB-LCID",
            "PCI",
            "基地局ID",
            "緯度",
            "経度",
            "更新日時",
        ]
    )
    .set_index("ID")
    .sort_index()
)

# 履歴はID、投稿者、備考、URLのみ
df6 = df2.reindex(columns=["ID", "投稿者", "備考", "URL"]).set_index("ID").sort_index()

# 結合
df7 = df5.join(df6).join(collaborator)

csv_path = pathlib.Path("ehimex.csv")
df7.to_csv(csv_path, encoding="utf_8_sig")
