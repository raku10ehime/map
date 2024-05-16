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

df2.drop_duplicates(subset="ID", keep="last", inplace=True)

df3 = (
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

df4 = df2.reindex(columns=["ID", "投稿者", "備考", "URL"]).set_index("ID").sort_index()

df5 = df3.join(df4)

df5.sort_values(by="場所", inplace=True)

csv_path = pathlib.Path("map", "ehimex.csv")
df5.to_csv(csv_path, encoding="utf_8_sig")
