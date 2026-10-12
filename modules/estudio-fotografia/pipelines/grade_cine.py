#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Grade editorial cinematografico 'film look' — inspirado nas refs 9/10/11.

Camadas (em ordem):
 1. correcao base (WB, altas, sombras)         [reusa corrigir() do golden_v2]
 2. exposicao mood: -7%, curva filmica com pretos foscos TINGIDOS de marrom
 3. color grading 3-way: sombras marrom-oliva, medios terrosos, altas creme
 4. verdes -> floresta profunda (escurece + dessatura + hue p/ oliva)
 5. dessaturacao global leve com pele protegida
 6. contraste local (clarity) em 2 raios
 7. halation: bloom quente nas altas luzes
 8. grao de filme (luminance-dependent, grosso)
 9. vinheta suave
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SRC = "/Users/flaviolima/Downloads/ensaio-gabi"
DST = os.path.join(SRC, "editadas")


def smoothstep(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.max(rgb, axis=-1)
    mn = np.min(rgb, axis=-1)
    d = mx - mn + 1e-8
    h = np.zeros_like(mx)
    m = mx == r
    h[m] = ((g - b)[m] / d[m]) % 6
    m = mx == g
    h[m] = (b - r)[m] / d[m] + 2
    m = mx == b
    h[m] = (r - g)[m] / d[m] + 4
    return h / 6.0 % 1.0, d / (mx + 1e-8), mx


def hsv_to_rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r = np.choose(i, [v, q, p, p, t, v])
    g = np.choose(i, [t, v, v, q, p, p])
    b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], axis=-1)


def corrigir(rgb):
    lum = rgb.mean(axis=-1)
    mid = (lum > 0.25) & (lum < 0.75)
    if mid.sum() > 1000:
        means = rgb[mid].mean(axis=0)
        gain = means[1] / (means + 1e-6)
        gain = 1 + 0.55 * (gain - 1)
        gain = np.clip(gain, 0.9, 1.12)
        rgb = rgb * gain
    rgb = np.clip(rgb, 0, 1)
    hi = np.clip((rgb - 0.80) / 0.20, 0, 1)
    rgb = rgb - hi * (rgb - 0.80) * 0.35
    sh = np.clip(1 - rgb / 0.30, 0, 1)
    rgb = rgb + sh * 0.035 * (0.30 - rgb)
    return np.clip(rgb, 0, 1)


def blur_np(a, radius):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius)),
                      np.float32) / 255.0


def cine(rgb):
    rgb = corrigir(rgb)

    # 2) mood: leve sub-exposicao + curva filmica
    rgb = rgb * 0.93
    # rolloff de altas
    hi = np.clip((rgb - 0.75) / 0.25, 0, 1)
    rgb = rgb - hi * (rgb - 0.75) * 0.30
    # contraste global (S)
    rgb = np.clip(rgb, 0, 1)
    rgb = rgb + 0.10 * np.sin(2 * np.pi * (rgb - 0.5)) * (rgb * (1 - rgb) * 4) * 0.5
    rgb = np.clip(rgb, 0, 1)
    # pretos foscos tingidos de indigo (paleta do guarda-roupa, nunca preto puro)
    matte = np.array([0.050, 0.056, 0.078])
    rgb = matte + rgb * (1 - matte)

    # 3) grading 3-way "denim & cream": sombras indigo, medios neutros-terrosos,
    #    altas luzes creme (harmonia com camisa marinho + vestido off-white)
    lum = rgb.mean(axis=-1, keepdims=True)
    shadows = np.clip(1 - lum / 0.40, 0, 1)
    mids = np.clip(1 - np.abs(lum - 0.5) / 0.35, 0, 1)
    highs = np.clip((lum - 0.70) / 0.30, 0, 1)
    rgb = rgb + shadows * np.array([-0.012, -0.002, 0.024])  # indigo profundo
    rgb = rgb + mids * np.array([0.010, 0.004, -0.006])      # terroso suave
    rgb = rgb + highs * np.array([0.032, 0.020, -0.008])     # creme quente
    rgb = np.clip(rgb, 0, 1)

    # 4) verdes -> oliva profundo  |  azuis (roupas) enriquecidos  |  5) dessatura c/ pele viva
    h, s, v = rgb_to_hsv(rgb)
    green = np.clip(1 - np.abs(h - 0.30) / 0.15, 0, 1)
    s = s * (1 - 0.30 * green)
    v = v * (1 - 0.22 * green)
    h = h - 0.040 * green
    blue = np.clip(1 - np.abs(h - 0.615) / 0.10, 0, 1)       # navy/indigo
    s = np.clip(s * (1 + 0.22 * blue), 0, 1)                 # azul rico
    v = v * (1 - 0.06 * blue)                                # navy denso
    skin = np.clip(1 - np.abs(h - 0.065) / 0.055, 0, 1)
    s = s * (0.88 + 0.18 * skin)
    rgb = hsv_to_rgb(h % 1.0, np.clip(s, 0, 1), np.clip(v, 0, 1))

    # 6) clarity: 2 raios
    L = rgb.mean(axis=-1)
    big = blur_np(L, 50)
    det = blur_np(L, 3)
    gain = 1 + 0.20 * (L - big) / (L + 0.04) + 0.22 * (L - det) / (L + 0.04)
    rgb = np.clip(rgb * gain[..., None], 0, 1)

    # 7) halation quente
    hl = smoothstep(rgb.mean(axis=-1), 0.70, 0.95)
    glow = blur_np(hl, 35)
    halo = glow[..., None] * np.array([1.0, 0.62, 0.35]) * 0.28
    rgb = 1 - (1 - rgb) * (1 - np.clip(halo, 0, 1))

    # 8) grao de filme (gerado em 1/3 da resolucao -> grao grosso organico)
    hh, ww = rgb.shape[:2]
    gsmall = np.random.default_rng(42).normal(0, 1, (hh // 3 + 1, ww // 3 + 1))
    g_im = Image.fromarray(((gsmall * 0.5 + 0.5).clip(0, 1) * 255).astype(np.uint8))
    grain = np.asarray(g_im.resize((ww, hh), Image.BILINEAR), np.float32) / 255.0
    grain = (grain - 0.5) * 2
    lum2 = rgb.mean(axis=-1)
    amp = 0.030 * (1 - smoothstep(lum2, 0.55, 0.95)) + 0.008
    rgb = np.clip(rgb + (grain * amp)[..., None], 0, 1)

    # 9) vinheta
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    d = np.hypot((xx - ww / 2) / (ww / 2), (yy - hh / 2) / (hh / 2)) / np.sqrt(2)
    rgb *= (1 - 0.30 * smoothstep(d, 0.55, 1.15))[..., None]
    return np.clip(rgb, 0, 1)


def process(nums):
    for n in nums:
        f = os.path.join(SRC, f"IMG_{n}.JPG")
        im = ImageOps.exif_transpose(Image.open(f))
        exif = im.info.get("exif")
        rgb = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
        rgb = cine(rgb)
        out = Image.fromarray((rgb * 255).astype(np.uint8))
        kwargs = dict(quality=95, subsampling=0)
        if exif:
            kwargs["exif"] = exif
        out.save(os.path.join(DST, f"IMG_{n}_cine.jpg"), "JPEG", **kwargs)
        print("ok:", n)


if __name__ == "__main__":
    nums = [int(a) for a in sys.argv[1:]]
    process(nums)
