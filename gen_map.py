import pathlib

import pandas as pd
import simplekml


class KMLGenerator:
    def __init__(self, name="Ehime", title="楽天モバイル基地局（愛媛県）"):
        self.kml = simplekml.Kml(name=name)
        self.kml.document.name = title
        self.icons = ["open.png", "5g.png", "close.png", "ready.png", "check.png"]
        self.fol = self.kml.newfolder()

    def make_style(self, fn, scale=1):
        kmlstyle = simplekml.Style()
        kmlstyle.iconstyle.scale = scale
        kmlstyle.iconstyle.icon.href = fn
        return kmlstyle

    def generate_style_maps(self):
        for icon in self.icons:
            fn = self.kml.addfile(icon)
            kmlstylemap = simplekml.StyleMap()
            kmlstylemap.normalstyle = self.make_style(fn)
            kmlstylemap.highlightstyle = self.make_style(fn)
            self.kml.document.stylemaps.append(kmlstylemap)

    def add_point(self, longitude, latitude, name, status, eNB_LCID, extended_data):
        pnt = self.fol.newpoint(name=name)
        pnt.coords = [(longitude, latitude)]

        match status:
            case "open":
                if extended_data["color"] == "darkblue":
                    pnt.stylemap = self.kml.document.stylemaps[1]
                    pnt.description = f"eNB-LCID: {eNB_LCID}"
                else:
                    pnt.stylemap = self.kml.document.stylemaps[0]
                    pnt.description = f"eNB-LCID: {eNB_LCID}"

            case "close":
                pnt.stylemap = self.kml.document.stylemaps[2]

            case "ready":
                pnt.stylemap = self.kml.document.stylemaps[3]

            case _:
                pnt.stylemap = self.kml.document.stylemaps[4]

        ex_data = simplekml.ExtendedData()

        for t, v in extended_data.items():
            ex_data.newdata(name=str(t), value=str(v))
        pnt.extendeddata = ex_data

    def save_kml(self, file_path):
        self.kml.savekmz(file_path)


def generate_kml_for_area(df, fn, name, title):
    kml_generator = KMLGenerator(name, title)
    kml_generator.generate_style_maps()

    for i, r in df.iterrows():
        kml_generator.add_point(
            longitude=r["経度"],
            latitude=r["緯度"],
            name=r["場所"],
            status=r["状況"],
            eNB_LCID=r["eNB-LCID"],
            extended_data=r.to_dict(),
        )

    kmz_path = pathlib.Path("map", fn)
    kml_generator.save_kml(kmz_path)


p = pathlib.Path("map", "ehime.csv")

df_ehime = pd.read_csv(p, dtype=str).fillna("")

df_ehime

df_ehime["緯度"] = df_ehime["緯度"].astype(float)
df_ehime["経度"] = df_ehime["経度"].astype(float)

generate_kml_for_area(df_ehime, "ehime.kmz", "Ehime", "楽天モバイル基地局（愛媛県）")
