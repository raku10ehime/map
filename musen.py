import pathlib
import re
import urllib.parse

import pandas as pd
import requests

d = {
    # 1:免許情報検索  2: 登録情報検索
    "ST": 1,
    # 詳細情報付加 0:なし 1:あり
    "DA": 1,
    # スタートカウント
    "SC": 1,
    # 取得件数
    "DC": 1,
    # 出力形式 1:CSV 2:JSON 3:XML
    "OF": 2,
    # 無線局の種別
    "OW": "FB_H",
    # 所轄総合通信局
    "IT": "G",
    # 免許人名称/登録人名称
    "NA": "楽天モバイル",
}

parm = urllib.parse.urlencode(d, encoding="shift-jis")

r = requests.get("https://www.tele.soumu.go.jp/musen/list", parm)
data = r.json()

update = data["musenInformation"]["lastUpdateDate"]

s = (
    data["musen"][0]["detailInfo"]["note"]
    .split("\\n", 2)[2]
    .replace("\\n", " ")
    .strip()
)

lst = re.findall("(\S+)\(([0-9,]+)\)", s)

df0 = pd.DataFrame(lst, columns=["市区町村名", "開設局数"])

df0["開設局数"] = df0["開設局数"].str.strip().str.replace(",", "").astype(int)

flag = df0["市区町村名"].str.endswith(("都", "道", "府", "県"))

df0["都道府県名"] = df0["市区町村名"].where(flag).fillna(method="ffill")

df1 = df0.reindex(columns=["都道府県名", "市区町村名", "開設局数"])

df2 = df1[df1["都道府県名"] == "愛媛県"].copy().rename(columns={"開設局数": update})

musen_path = pathlib.Path("map", "musen.csv")
musen_path.parent.mkdir(parents=True, exist_ok=True)

df2.to_csv(musen_path, index=False)

df2
