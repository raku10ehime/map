# -*- coding: utf-8 -*-
import pathlib

import folium
from folium.features import DivIcon
from folium import plugins
import pandas as pd
import simplekml

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRE1NoYtNw1FmjRQ8wcdPkcE0Ryeoc2mfFkCQPHjzwL5CpwNKkLXnBl_F7c0LZjrtbLtRLH55ZVi6gQ/pub?gid=0&single=true&output=csv"

df = (
    pd.read_csv(url, index_col=0, usecols=[0, 1, 2, 7, 8, 11, 12, 13, 14])
    .dropna(how="all")
    .fillna("")
)

df["color"] = df["状況"].replace({"open": "green", "close": "red", "ready": "orange", "check": "gray"})
df["場所"] = df["場所"].str.strip()

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
    opacity=0.4,
).add_to(map)

folium.raster_layers.TileLayer(
    "https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}",
    subdomains=["mt0", "mt1", "mt2", "mt3"],
    name="Google Map(航空写真)",
    attr="<a href='https://developers.google.com/maps/documentation' target='_blank'>© Google</a>",
    opacity=0.6,
).add_to(map)

folium.raster_layers.TileLayer(
    name="楽天モバイル（直近）",
    tiles="https://gateway-api.global.rakuten.com/dsd/geoserver/4g2m/mno_coverage_map/gwc/service/gmaps?LAYERS=mno_coverage_map:all_map&FORMAT=image/png&TRANSPARENT=TRUE&x={x}&y={y}&zoom={z}",
    fmt="image/png",
    attr="楽天モバイルエリア",
    tms=False,
    overlay=True,
    control=True,
    opacity=1,
).add_to(map)

folium.raster_layers.TileLayer(
    name="楽天モバイル（予定）",
    tiles="https://gateway-api.global.rakuten.com/dsd/geoserver/4g4m/mno_coverage_map/gwc/service/gmaps?LAYERS=mno_coverage_map:all_map&FORMAT=image/png&TRANSPARENT=TRUE&x={x}&y={y}&zoom={z}",
    fmt="image/png",
    attr="楽天モバイルエリア",
    tms=False,
    overlay=True,
    control=True,
    opacity=1,
    show=False,
).add_to(map)

folium.raster_layers.TileLayer(
    name="楽天モバイル5G",
    tiles="https://gateway-api.global.rakuten.com/dsd/geoserver/5g/mno_coverage_map/gwc/service/gmaps?LAYERS=mno_coverage_map:all_map&FORMAT=image/png&TRANSPARENT=TRUE&x={x}&y={y}&zoom={z}",
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

# 開局

open_img = kml.addfile("open.png")

# スタイル
open_normal = simplekml.Style()
open_normal.iconstyle.scale = 1
open_normal.iconstyle.icon.href = open_img

# スタイル
open_highlight = simplekml.Style()
open_highlight.iconstyle.scale = 1
open_highlight.iconstyle.icon.href = open_img

open_stylemap = simplekml.StyleMap()
open_stylemap.normalstyle = open_normal
open_stylemap.highlightstyle = open_highlight

# 未開局

close_img = kml.addfile("close.png")

# スタイル
close_normal = simplekml.Style()
close_normal.iconstyle.scale = 1
close_normal.iconstyle.icon.href = close_img

# スタイル
close_highlight = simplekml.Style()
close_highlight.iconstyle.scale = 1
close_highlight.iconstyle.icon.href = close_img

close_stylemap = simplekml.StyleMap()
close_stylemap.normalstyle = close_normal
close_stylemap.highlightstyle = close_highlight

# 準備

ready_img = kml.addfile("ready.png")

# スタイル
ready_normal = simplekml.Style()
ready_normal.iconstyle.scale = 1
ready_normal.iconstyle.icon.href = ready_img

# スタイル
ready_highlight = simplekml.Style()
ready_highlight.iconstyle.scale = 1
ready_highlight.iconstyle.icon.href = ready_img

ready_stylemap = simplekml.StyleMap()
ready_stylemap.normalstyle = ready_normal
ready_stylemap.highlightstyle = ready_highlight

# チェック

check_img = kml.addfile("check.png")

# スタイル
check_normal = simplekml.Style()
check_normal.iconstyle.scale = 1
check_normal.iconstyle.icon.href = check_img

# スタイル
check_highlight = simplekml.Style()
check_highlight.iconstyle.scale = 1
check_highlight.iconstyle.icon.href = check_img

check_stylemap = simplekml.StyleMap()
check_stylemap.normalstyle = check_normal
check_stylemap.highlightstyle = check_highlight

# スタイルマップに登録

kml.document.stylemaps.append(open_stylemap)
kml.document.stylemaps.append(close_stylemap)
kml.document.stylemaps.append(ready_stylemap)
kml.document.stylemaps.append(check_stylemap)

fol = kml.newfolder()

fg1 = folium.FeatureGroup(name="基地局").add_to(map)
fg2 = folium.FeatureGroup(name="eNB-LCID").add_to(map)
fg3 = folium.FeatureGroup(name="エリア").add_to(map)

for i, r in df.iterrows():

    # folium

    enb_lcid = r["eNB-LCID"] or "unknown"

    fg1.add_child(
        folium.Marker(
            location=[r["緯度"], r["経度"]],
            popup=folium.Popup(
                f'<p><a href="https://www.google.com/maps?layer=c&cbll={r["緯度"]},{r["経度"]}" target="_blank">{r["場所"]}</a></p>',
                max_width=300,
            ),
            tooltip=f'{r["場所"]}',
            icon=folium.Icon(color=r["color"], icon="signal"),
        )
    )

    fg2.add_child(
        folium.Marker(
            location=[r["緯度"], r["経度"]],
            icon=DivIcon(
                icon_size=(110, 30),
                icon_anchor=(55, -10),
                html=f'<div style="text-align:center; font-size: 10pt; background-color:rgba(255,255,255,0.2)">{enb_lcid}</div>',
            ),
        )
    )

    fg3.add_child(
        folium.Circle(
            location=[r["緯度"], r["経度"]],
            popup=folium.Popup(f"<p>{enb_lcid}</p>", max_width=300),
            radius=780,
            color=r["color"],
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

    ex_data = simplekml.ExtendedData()

    for n, v in r.items():

        ex_data.newdata(name=str(n), value=str(v))

    pnt.extendeddata = ex_data

folium.LayerControl().add_to(map)

map_path = pathlib.Path("map", "index.html")

# map_path.parent.mkdir(parents=True, exist_ok=True)

map.save(str(map_path))

kmz_path = pathlib.Path("map", "ehime.kmz")

kml.savekmz(kmz_path)
