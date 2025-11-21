import pathlib

import pandas as pd


def make_df():
    df1 = pd.read_csv(
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN5xiHhlnPTkv3auHkYLT9NPvvjayj5AdPrH5VBQdbELOzfONi236Vub6eSshv8jAxQw3V1rgbbgE/pub?gid=0&single=true&output=csv",
        dtype=str,
    )

    df2 = pd.read_csv(
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN5xiHhlnPTkv3auHkYLT9NPvvjayj5AdPrH5VBQdbELOzfONi236Vub6eSshv8jAxQw3V1rgbbgE/pub?gid=882951423&single=true&output=csv",
        dtype=str,
    ).sort_values("更新日時")

    # ID、投稿者のみ
    df3 = df2[["ID", "投稿者"]].dropna(subset="投稿者").copy()

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
                "eNB-LCID_700",
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
    df6 = (
        df2.reindex(columns=["ID", "投稿者", "備考", "URL"])
        .set_index("ID")
        .sort_index()
    )

    # 結合
    df7 = df5.join(df6).join(collaborator)

    return df7.fillna("")


df = make_df()

df["場所"] = df["場所"].str.strip()

df["緯度"] = df["緯度"].astype(float)
df["経度"] = df["経度"].astype(float)

csv_path = pathlib.Path("map", "list.csv")
df.reindex(
    columns=[
        "場所",
        "市区町村",
        "設置タイプ",
        "更新日時",
        "状況",
        "eNB-LCID",
        "eNB-LCID_700",
        "基地局ID",
        "sector",
        "sub6",
        "ミリ波",
        "緯度",
        "経度",
    ]
).to_csv(csv_path, index=False, encoding="utf_8_sig")

df["color"] = df["状況"].replace(
    {
        "open": "green",
        "close": "red",
        "ready": "orange",
        "check": "gray",
        "delete": "black",
    }
)

df["icon"] = df["状況"].replace(
    {
        "open": "signal",
        "close": "remove",
        "ready": "wrench",
        "check": "search",
        "delete": "trash",
    }
)

# 5Gフラグの設定
flag5G = df["sub6"].str.isnumeric() | df["ミリ波"].str.isnumeric()

df["icon"] = df["icon"].mask(flag5G, "upload")
df["color"] = df["color"].mask(flag5G & (df["状況"] == "open"), "darkblue")
df["場所"] = df["場所"].mask(flag5G, "【5G】" + df["場所"])

# 設置タイプごとの処理
d = {
    "屋内": "home",
    "ピコセル": "folder-close",
    "衛星": "globe",
    "鉄塔": "tower",
    "au共用": "adjust",
    "撤去": "",
}

for k, v in d.items():
    df["icon"] = df["icon"].mask((df["設置タイプ"] == k) & bool(v), v)
    df["場所"] = df["場所"].mask((df["設置タイプ"] == k), f"【{k}】" + df["場所"])

csv_path = pathlib.Path("map", "ehime.csv")
df.to_csv(csv_path, encoding="utf_8_sig")
