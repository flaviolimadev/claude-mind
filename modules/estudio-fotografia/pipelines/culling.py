#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Culling do lote novo (IMG_8376-8459):
 - mede nitidez (variancia do Laplaciano) e brilho
 - agrupa duplicadas por similaridade (thumb 48x48, consecutivas)
 - gera contact sheets rotuladas (nome + nitidez + grupo)
 - salva relatorio em JSON
"""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps

SRC = "/Users/flaviolima/Downloads/ensaio-gabi"
OUT = ("/private/tmp/claude-501/-Users-flaviolima-Downloads-ensaio-gabi/"
       "1f7cc54c-739b-444a-b7da-6aab3c68c05a/scratchpad")

files = sorted(f for f in os.listdir(SRC)
               if f.endswith(".JPG") and 8460 <= int(f[4:8]) <= 8601)
print(len(files), "fotos novas")

data = []
for f in files:
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, f)))
    thumb = im.convert("L").resize((192, 192))
    a = np.asarray(thumb, np.float32)
    lap = (4 * a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1]
           - a[1:-1, :-2] - a[1:-1, 2:])
    sharp = float(lap.var())
    tiny = np.asarray(im.convert("L").resize((48, 48)), np.float32) / 255.0
    data.append({"f": f, "sharp": round(sharp, 1),
                 "bright": round(float(tiny.mean()), 3),
                 "tiny": tiny, "im": im})

# agrupamento: compara com o ULTIMO membro do grupo corrente
groups = []
for d in data:
    if groups:
        prev = groups[-1][-1]
        dist = float(np.sqrt(((d["tiny"] - prev["tiny"]) ** 2).mean()))
        if dist < 0.085:
            groups[-1].append(d)
            continue
    groups.append([d])

report = []
for gi, g in enumerate(groups):
    best = max(g, key=lambda x: x["sharp"])
    for d in g:
        d["group"] = gi
        d["best"] = d is best
    report.append({"group": gi,
                   "members": [m["f"] for m in g],
                   "best": best["f"],
                   "sharps": {m["f"]: m["sharp"] for m in g}})

# contact sheets 3x4
TW, TH = 420, 420
COLS, ROWS = 3, 4
per = COLS * ROWS
for s in range((len(data) + per - 1) // per):
    sheet = Image.new("RGB", (COLS * TW, ROWS * TH + 40), (16, 16, 16))
    dr = ImageDraw.Draw(sheet)
    for i, d in enumerate(data[s * per:(s + 1) * per]):
        r, c = divmod(i, COLS)
        t = ImageOps.contain(d["im"], (TW, TH - 46))
        x = c * TW + (TW - t.width) // 2
        sheet.paste(t, (x, r * TH + 4))
        tag = "*" if d["best"] else " "
        dr.text((c * TW + 8, r * TH + TH - 38),
                f"{d['f'][4:8]} g{d['group']}{tag} n={d['sharp']:.0f}",
                fill=(255, 220, 120) if d["best"] else (170, 170, 170))
    sheet.save(os.path.join(OUT, f"sheetB_{s}.jpg"), quality=88)
    print("sheet", s, "ok")

for d in data:
    d.pop("tiny"), d.pop("im")
with open(os.path.join(OUT, "culling.json"), "w") as fp:
    json.dump(report, fp, indent=1, ensure_ascii=False)
print(len(groups), "grupos;",
      sum(1 for g in groups if len(g) > 1), "com duplicadas")
