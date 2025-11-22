import html
import pathlib

import folium
import folium.plugins
import jinja2
import pandas as pd
from folium.features import DivIcon
from folium_vectortilelayer import VectorTileLayer

dt_now = pd.Timestamp.now(tz="Asia/Tokyo").tz_localize(None)
dt_str = dt_now.strftime("%Y/%m/%d")

p = pathlib.Path("map", "ehime.csv")

df = pd.read_csv(p, dtype=str).fillna("")

df["緯度"] = df["緯度"].astype(float)
df["経度"] = df["経度"].astype(float)

df["URL"] = df["URL"].apply(
    lambda url: f'<a target="_blank" href="{url}">リンク</a>'
    if url.startswith("https://x.com")
    else url
)

df

map = folium.Map(
    tiles=None,
    location=[33.84167, 132.76611],
    zoom_start=12,
)

folium.raster_layers.TileLayer(
    "https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}",
    subdomains=["mt0", "mt1", "mt2", "mt3"],
    name="Google Map(航空写真)",
    attr="<a href='https://developers.google.com/maps/documentation'>© Google</a>",
    opacity=0.8,
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
    tiles="https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png",
    name="国土地理院",
    attr='&copy; <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
    overlay=False,
).add_to(map)

folium.raster_layers.WmsTileLayer(
    url="https://area-map.rmb-ss.jp/turbo",
    layers="turbo",
    name="楽天モバイル",
    fmt="image/png",
    transparent=True,
    overlay=True,
    control=True,
    opacity=1.0,
    show=False,
    attr="<a href='https://network.mobile.rakuten.co.jp/'>楽天モバイル</a>",
).add_to(map)

fg0 = folium.FeatureGroup(name="パートナーエリア", show=False).add_to(map)
fg1 = folium.FeatureGroup(name="基地局").add_to(map)
fg2 = folium.FeatureGroup(name="エリア（円）", show=False).add_to(map)
fg3 = folium.FeatureGroup(name="エリア（塗）", show=False).add_to(map)
fg4 = folium.FeatureGroup(
    name="eNB-LCID",
    show=False,
).add_to(map)

# ベクターレイヤー

options = {
    "vectorTileLayerStyles": {
        "next_rakuten": {
            "fill": True,
            "weight": 0,
            "fillColor": "orange",
            "fillOpacity": 0.4,
        },
    }
}

vc = VectorTileLayer(
    "https://area.uqcom.jp/api3/next_rakuten/{z}/{x}/{y}.mvt", "auローミング", options
)

fg0.add_child(vc)

for i, r in df.iterrows():
    enb_lcid = r["eNB-LCID"] or "737XXX-X,X,X"
    enb_lcid_700 = r["eNB-LCID_700"] or "737XXX-X,X,X"

    tag_map = f'<p><a href="https://www.google.com/maps?layer=c&cbll={r["緯度"]},{r["経度"]}" target="_blank" rel="noopener noreferrer">{r["場所"]}</a></p>'

    text = "\r\r".join(
        [
            f"【日付】\r{dt_str}",
            f"【場所】\r{r['場所']}\r({r['緯度']}, {r['経度']})",
            f'【基地局】\r・eNB-LCID: {enb_lcid}\r・eNB-LCID_700: {enb_lcid_700}\r・基地局ID: {r["基地局ID"]}',
            f'【地図】\rhttps://www.google.co.jp/maps?q={r["緯度"]},{r["経度"]}',
            "#愛媛 #楽天モバイル #基地局",
        ]
    )

    escaped_text = html.escape(text)

    tag_clip = f'<p><textarea id="myInput">{escaped_text}</textarea></p><p><button onclick="myFunction()">Copy location</button></p>'

    tmp = pd.DataFrame(r.drop(labels=["場所", "color", "icon"]))

    fg1.add_child(
        folium.Marker(
            location=[r["緯度"], r["経度"]],
            popup=folium.Popup(
                "\n\n".join(
                    [tag_map, tmp.to_html(header=False, escape=False), tag_clip]
                ).strip(),
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

    if r["状況"] != "delete":
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
                weight=1,
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

# 検索
folium.plugins.Search(
    layer=fg1,
    geom_type="Point",
    placeholder="場所検索",
    collapsed=True,
    search_label="place",
).add_to(map)

# レイヤーコントロール
folium.LayerControl().add_to(map)

# 現在値
folium.plugins.LocateControl(position="bottomright").add_to(map)

# 距離測定
folium.plugins.MeasureControl().add_to(map)

# DRAW
folium.plugins.Draw(
    draw_options={"polygon": False, "rectangle": False, "circlemarker": False}
).add_to(map)

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
