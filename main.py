# -*- coding: utf-8 -*-
import datetime
import pathlib
import urllib.parse
import html

import folium
import pandas as pd
import simplekml
import jinja2
from folium import plugins
from folium.features import DivIcon
from folium_vectortilelayer import VectorTileLayer

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN5xiHhlnPTkv3auHkYLT9NPvvjayj5AdPrH5VBQdbELOzfONi236Vub6eSshv8jAxQw3V1rgbbgE/pub?gid=0&single=true&output=csv"

JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
dt_now = datetime.datetime.now(JST)

dt_str = dt_now.strftime("%Y/%m/%d")

df = (
    pd.read_csv(
        url, usecols=[1, 2, 3, 5, 8, 9, 10, 11, 12, 13, 16, 17], dtype=str
    )
    .dropna(how="all")
    .fillna("")
)

df["color"] = df["状況"].replace(
    {"open": "green", "close": "red", "ready": "orange", "check": "gray"}
)

df["icon"] = df["状況"].replace(
    {"open": "signal", "close": "remove", "ready": "wrench", "check": "search"}
)

df["場所"] = df["場所"].str.strip()

df["緯度"] = df["緯度"].astype(float)
df["経度"] = df["経度"].astype(float)

# 5G
flag5G = df["sub6"].str.isnumeric() | df["ミリ波"].str.isnumeric()

df["icon"] = df["icon"].mask(flag5G, "plane")
df["color"] = df["color"].mask(flag5G & (df["状況"] == "open"), "darkblue")
df["場所"] = df["場所"].mask(flag5G, "【5G】" + df["場所"])

# 屋内
df["icon"] = df["icon"].mask(df["設置タイプ"] == "屋内", "home")
df["場所"] = df["場所"].mask(df["設置タイプ"] == "屋内", "【屋内】" + df["場所"])

# ピコセル
df["icon"] = df["icon"].mask(df["設置タイプ"] == "ピコセル", "folder-close")
df["場所"] = df["場所"].mask(df["設置タイプ"] == "ピコセル", "【ピコセル】" + df["場所"])

# 衛星
df["icon"] = df["icon"].mask(df["設置タイプ"] == "衛星", "globe")
df["場所"] = df["場所"].mask(df["設置タイプ"] == "衛星", "【衛星】" + df["場所"])

# au共用
df["icon"] = df["icon"].mask(df["設置タイプ"] == "au共用", "adjust")
df["場所"] = df["場所"].mask(df["設置タイプ"] == "au共用", "【au共用】" + df["場所"])

csv_path = pathlib.Path("map", "ehime.csv")
df.to_csv(csv_path, encoding="utf_8_sig")

map = folium.Map(
    tiles=None,
    location=[33.84167, 132.76611],
    zoom_start=12,
)

folium.raster_layers.TileLayer(
    tiles="https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png",
    name="国土地理院",
    attr='&copy; <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
).add_to(map)

folium.raster_layers.TileLayer(
    tiles="https://cyberjapandata.gsi.go.jp/xyz/blank/{z}/{x}/{y}.png",
    name="国土地理院（白地図）",
    attr='&copy; <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
).add_to(map)

folium.raster_layers.TileLayer(
    "https://cyberjapandata.gsi.go.jp/xyz/hillshademap/{z}/{x}/{y}.png",
    name="国土地理院（陰影起伏図）",
    attr="<a href='https://maps.gsi.go.jp/development/ichiran.html'>国土地理院</a>",
    opacity=0.6,
).add_to(map)

folium.raster_layers.TileLayer(
    "https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}",
    subdomains=["mt0", "mt1", "mt2", "mt3"],
    name="Google Map(航空写真)",
    attr="<a href='https://developers.google.com/maps/documentation'>© Google</a>",
    opacity=0.8,
).add_to(map)

folium.raster_layers.TileLayer(
    name="楽天モバイル（近々）",
    tiles="https://area-map.mobile.rakuten.co.jp/dsd/geoserver/4g2m/mno_coverage_map/gwc/service/gmaps?LAYERS=mno_coverage_map:all_map&FORMAT=image/png&TRANSPARENT=TRUE&x={x}&y={y}&zoom={z}&update=20220404",
    fmt="image/png",
    attr="楽天モバイルエリア",
    tms=False,
    overlay=True,
    control=True,
    opacity=1,
    show=False,
).add_to(map)

folium.raster_layers.TileLayer(
    name="楽天モバイル（予定）",
    tiles="https://area-map.mobile.rakuten.co.jp/dsd/geoserver/4g4m/mno_coverage_map/gwc/service/gmaps?LAYERS=mno_coverage_map:all_map&FORMAT=image/png&TRANSPARENT=TRUE&x={x}&y={y}&zoom={z}&update=20220404",
    fmt="image/png",
    attr="楽天モバイルエリア",
    tms=False,
    overlay=True,
    control=True,
    opacity=1,
).add_to(map)

folium.raster_layers.TileLayer(
    name="楽天モバイル5G",
    tiles="https://area-map.mobile.rakuten.co.jp/dsd/geoserver/5g/mno_coverage_map/gwc/service/gmaps?LAYERS=mno_coverage_map:all_map&FORMAT=image/png&TRANSPARENT=TRUE&x={x}&y={y}&zoom={z}&update=20220404",
    fmt="image/png",
    attr="楽天モバイルエリア",
    tms=False,
    overlay=True,
    control=True,
    opacity=1,
    show=False,
).add_to(map)

# 現在値
folium.plugins.LocateControl(position="bottomright").add_to(map)

# 距離測定
folium.plugins.MeasureControl().add_to(map)

# DRAW
folium.plugins.Draw(
    draw_options={"polygon": False, "rectangle": False, "circlemarker": False}
).add_to(map)

kml = simplekml.Kml(name="Ehime")

# アイコン設定

icons = ["open.png", "close.png", "ready.png", "check.png"]

for icon in icons:

    fn = kml.addfile(icon)

    def make_style(fn, scale=1):

        kmlstyle = simplekml.Style()
        kmlstyle.iconstyle.scale = scale
        kmlstyle.iconstyle.icon.href = fn

        return kmlstyle

    kmlstylemap = simplekml.StyleMap()
    kmlstylemap.normalstyle = make_style(fn)
    kmlstylemap.highlightstyle = make_style(fn)

    kml.document.stylemaps.append(kmlstylemap)

fol = kml.newfolder()

fg0 = folium.FeatureGroup(name="パートナーエリア", show=False).add_to(map)
fg1 = folium.FeatureGroup(name="基地局").add_to(map)
fg2 = folium.FeatureGroup(name="エリア（円）", show=False).add_to(map)
fg3 = folium.FeatureGroup(name="エリア（塗）", show=False).add_to(map)
fg4 = folium.FeatureGroup(name="eNB-LCID", show=False,).add_to(map)

options = {
    "vectorTileLayerStyles": {
        "rakuten": {
            "fill": True,
            "weight": 0,
            "fillColor": "orange",
            "fillOpacity": 0.4,
        },
    }
}

vc = VectorTileLayer("https://area.uqcom.jp/api2/rakuten/{z}/{x}/{y}.mvt", "auローミング", options)
fg0.add_child(vc)

for i, r in df.iterrows():

    # folium

    enb_lcid = r["eNB-LCID"] or "737XXX-X,X,X"
    pci = r["PCI"] or "XX,XX,XX"

    tag_map = f'<p><a href="https://www.google.com/maps?layer=c&cbll={r["緯度"]},{r["経度"]}" target="_blank" rel="noopener noreferrer">{r["場所"]}</a></p>'

    status = "報告" if r["状況"] == "open" else "新規開局"

    text = "\r\r".join(
        [
            f"○{status}",
            f"【日付】\r{dt_str}",
            f"【場所】\r{r['場所']}\r({r['緯度']}, {r['経度']})",
            f"【基地局】\r・eNB-LCID: {enb_lcid}\r・PCI: {pci}",
            f'【地図】\r\nhttps://www.google.co.jp/maps?q={r["緯度"]},{r["経度"]}',
        ]
    )
    
    escaped_text = html.escape(text)
    
    tag_clip = f'<textarea id="myInput">{escaped_text}</textarea><br><button onclick="myFunction()">Copy location</button>'

    tmp = pd.DataFrame(r.drop(labels=["場所", "color", "icon"]))

    fg1.add_child(
        folium.Marker(
            location=[r["緯度"], r["経度"]],
            popup=folium.Popup(
                "\n\n".join([tag_map, tmp.to_html(header=False), tag_clip]).strip(),
                max_width=300,
            ),
            tooltip=f'{r["場所"]}',
            icon=folium.Icon(color=r["color"], icon=r["icon"]),
            place=r["場所"],
        )
    )

    enb_lcid = r["eNB-LCID"] or "unknown"

    radius = 780
    
    if r["設置タイプ"] == "屋内":
        radius = 78
    elif r["設置タイプ"] == "ピコセル":
        radius = 312

    fg2.add_child(
        folium.Circle(
            location=[r["緯度"], r["経度"]],
            popup=folium.Popup(f"<p>{enb_lcid}</p>", max_width=300),
            radius=radius,
            color=r["color"],
        )
    )

    fg3.add_child(
        folium.Circle(
            location=[r["緯度"], r["経度"]],
            radius=radius,
            color="black",
            weight = 1,
            fill=True,
            fill_opacity=0.5,
        )
    )

    fg4.add_child(
        folium.Marker(
            location=[r["緯度"], r["経度"]],
            icon=DivIcon(
                icon_size=(110, 30),
                icon_anchor=(55, -10),
                html=f'<div style="text-align:center; font-size: 10pt; background-color:rgba(255,255,255,0.2)">{enb_lcid}</div>',
            ),
        )
    )    
    
    # fol

    pnt = fol.newpoint(name=r["場所"])
    pnt.coords = [(r["経度"], r["緯度"])]

    if r["状況"] == "open":
        pnt.stylemap = kml.document.stylemaps[0]
        pnt.description = f'eNB-LCID: {r["eNB-LCID"]}'

    elif r["状況"] == "close":
        pnt.stylemap = kml.document.stylemaps[1]

    elif r["状況"] == "ready":
        pnt.stylemap = kml.document.stylemaps[2]

    else:
        pnt.stylemap = kml.document.stylemaps[3]

    r.drop(labels=["icon", "color"], inplace=True)

    ex_data = simplekml.ExtendedData()

    for n, v in r.items():

        ex_data.newdata(name=str(n), value=str(v))

    pnt.extendeddata = ex_data

# 検索
folium.plugins.Search(
    layer=fg1,
    geom_type="Point",
    placeholder="場所検索",
    collapsed=True,
    search_label="place",
).add_to(map)

   
folium.LayerControl().add_to(map)

el = folium.MacroElement().add_to(map)
el._template = jinja2.Template("""
    {% macro script(this, kwargs) %}
    function myFunction() {
      /* Get the text field */
      var copyText = document.getElementById("myInput");

      /* Select the text field */
      copyText.select();
      copyText.setSelectionRange(0, 99999); /* For mobile devices */

      /* Copy the text inside the text field */
      document.execCommand("copy");
    }
    {% endmacro %}
""")

map_path = pathlib.Path("map", "index.html")

# map_path.parent.mkdir(parents=True, exist_ok=True)

map.save(str(map_path))

kmz_path = pathlib.Path("map", "ehime.kmz")

kml.savekmz(kmz_path)
