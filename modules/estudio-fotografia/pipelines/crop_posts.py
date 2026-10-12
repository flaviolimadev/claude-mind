#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Cortes 4:5 (feed) e 9:16 (stories) das fotos editadas.

Enquadramento centrado no facho de luz (centroide de brilho), com:
 - 4:5: corte vertical limitado a no máx. 5% do topo (protege a cabeça)
 - 9:16: corte horizontal no ponto médio entre o facho e o centro do quadro
"""
import os
import numpy as np
from PIL import Image, ImageFilter

DST = "/Users/flaviolima/Downloads/ensaio-gabi/editadas"
FEED = os.path.join(DST, "posts", "feed_4x5")
STORIES = os.path.join(DST, "posts", "stories_9x16")
os.makedirs(FEED, exist_ok=True)
os.makedirs(STORIES, exist_ok=True)


def glow_center(im):
    small = im.convert("L").resize((im.width // 8, im.height // 8))
    b = np.asarray(small.filter(ImageFilter.GaussianBlur(4)),
                   dtype=np.float32)
    thr = np.percentile(b, 99.0)
    ys, xs = np.nonzero(b >= thr)
    if len(xs) < 20:
        return 0.5, 0.5
    return xs.mean() / b.shape[1], ys.mean() / b.shape[0]


def crop_45(im, cx, cy):
    w, h = im.size
    nh = int(round(w * 5 / 4))          # mantém largura, corta altura
    if nh >= h:
        return im
    free = h - nh
    y0 = int(round(cy * h - nh / 2))
    y0 = max(0, min(y0, free))
    y0 = min(y0, int(0.05 * h))          # nunca corta mais de 5% do topo
    return im.crop((0, y0, w, y0 + nh))


def crop_916(im, cx, cy):
    w, h = im.size
    nw = int(round(h * 9 / 16))          # mantém altura, corta largura
    if nw >= w:
        return im
    cxm = 0.5 * cx + 0.5 * 0.5           # meio-termo facho <-> centro
    x0 = int(round(cxm * w - nw / 2))
    x0 = max(0, min(x0, w - nw))
    return im.crop((x0, 0, x0 + nw, h))


files = sorted(f for f in os.listdir(DST)
               if f.endswith(("_pb.jpg", "_sepia.jpg")))
for f in files:
    im = Image.open(os.path.join(DST, f))
    cx, cy = glow_center(im)
    base = f[:-4]
    crop_45(im, cx, cy).save(os.path.join(FEED, base + "_4x5.jpg"),
                             "JPEG", quality=95, subsampling=0)
    crop_916(im, cx, cy).save(os.path.join(STORIES, base + "_9x16.jpg"),
                              "JPEG", quality=95, subsampling=0)
    print("ok:", base)
print(f"\n{len(files)} fotos x 2 cortes = {len(files)*2} arquivos")
