#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Correcao de cores natural para as fotos externas restantes.

 1. Balanco de branco automatico (gray-world nos meios-tons, amortecido)
 2. Recuperacao de altas luzes + leve abertura de sombras
 3. Curva S suave de contraste
 4. Vivacidade (+saturacao leve, protegendo pele)
Extra: IMG_8295 tambem ganha versao P&B filmica.
"""
import os
import numpy as np
from PIL import Image, ImageOps

SRC = "/Users/flaviolima/Downloads/ensaio-gabi"
DST = os.path.join(SRC, "editadas")
os.makedirs(DST, exist_ok=True)

FILES = ["IMG_8286.JPG", "IMG_8287.JPG", "IMG_8289.JPG", "IMG_8290.JPG",
         "IMG_8292.JPG", "IMG_8295.JPG", "IMG_8297.JPG", "IMG_8299.JPG",
         "IMG_8300.JPG", "IMG_8301.JPG", "IMG_8302.JPG"]


def corrigir(rgb):
    # 1) WB gray-world nos meios-tons (25-75%), amortecido em 55%
    lum = rgb.mean(axis=-1)
    mid = (lum > 0.25) & (lum < 0.75)
    if mid.sum() > 1000:
        means = rgb[mid].mean(axis=0)
        g = means[1]
        gain = g / (means + 1e-6)
        gain = 1 + 0.55 * (gain - 1)          # amortece
        gain = np.clip(gain, 0.9, 1.12)
        rgb = rgb * gain
    rgb = np.clip(rgb, 0, 1)

    # 2) altas luzes: joelho suave; sombras: leve abertura
    hi = np.clip((rgb - 0.80) / 0.20, 0, 1)
    rgb = rgb - hi * (rgb - 0.80) * 0.35
    sh = np.clip(1 - rgb / 0.30, 0, 1)
    rgb = rgb + sh * 0.035 * (0.30 - rgb)

    # 3) curva S suave
    rgb = np.clip(rgb, 0, 1)
    rgb = rgb + 0.05 * np.sin(2 * np.pi * (rgb - 0.5)) * (rgb * (1 - rgb) * 4) * 0.5

    # 4) vivacidade: satura mais onde ha pouca saturacao
    mx = rgb.max(axis=-1, keepdims=True)
    mn = rgb.min(axis=-1, keepdims=True)
    sat = (mx - mn) / (mx + 1e-6)
    boost = 1 + 0.14 * (1 - sat)              # vibrance
    mean = rgb.mean(axis=-1, keepdims=True)
    rgb = mean + (rgb - mean) * boost
    return np.clip(rgb, 0, 1)


def pb_filmico(rgb):
    # mix de canais favorecendo pele (R) + matte suave + curva S
    g = rgb[..., 0] * 0.45 + rgb[..., 1] * 0.40 + rgb[..., 2] * 0.15
    g = 0.03 + g * 0.97                        # matte
    g = g + 0.09 * np.sin(2 * np.pi * (g - 0.5)) * (g * (1 - g) * 4) * 0.5
    return np.clip(g, 0, 1)


for f in FILES:
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, f)))
    exif = im.info.get("exif")
    rgb = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    rgb = corrigir(rgb)
    kwargs = dict(quality=95, subsampling=0)
    if exif:
        kwargs["exif"] = exif
    out = Image.fromarray((rgb * 255).astype(np.uint8))
    out.save(os.path.join(DST, f.replace(".JPG", "_cor.jpg")), "JPEG", **kwargs)
    print("ok:", f.replace(".JPG", "_cor.jpg"))
    if f == "IMG_8295.JPG":
        g = pb_filmico(rgb)
        Image.fromarray((g * 255).astype(np.uint8)).convert("RGB").save(
            os.path.join(DST, "IMG_8295_pb.jpg"), "JPEG", **kwargs)
        print("ok: IMG_8295_pb.jpg")
