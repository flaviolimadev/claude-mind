#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Arte ultrassom v5 — bebe ampliado e nitido no vao de luz."""
import numpy as np
from PIL import Image, ImageFilter, ImageOps

SIL = "/Users/flaviolima/Downloads/ensaio-gabi/IMG_8285.JPG"
US = ("/private/tmp/claude-501/-Users-flaviolima-Downloads-ensaio-gabi/"
      "1f7cc54c-739b-444a-b7da-6aab3c68c05a/images/8.jpg")
OUT1 = "/Users/flaviolima/Downloads/ensaio-gabi/editadas/ARTE_ultrassom.jpg"
OUT2 = "/Users/flaviolima/Downloads/ensaio-gabi/editadas_finais/ARTE_ultrassom.jpg"

SEPIA_X = np.array([0.00, 0.25, 0.50, 0.75, 1.00])
SEPIA_R = np.array([0.00, 0.30, 0.60, 0.85, 1.00])
SEPIA_G = np.array([0.00, 0.21, 0.45, 0.72, 0.94])
SEPIA_B = np.array([0.00, 0.13, 0.30, 0.53, 0.82])


def sepia(g):
    return np.stack([np.interp(g, SEPIA_X, SEPIA_R),
                     np.interp(g, SEPIA_X, SEPIA_G),
                     np.interp(g, SEPIA_X, SEPIA_B)], axis=-1)


def smoothstep(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def screen(a, b):
    return 1 - (1 - a) * (1 - b)


# ---------- silhueta ----------
sil_im = ImageOps.exif_transpose(Image.open(SIL))
W, H = sil_im.size
sil = np.asarray(sil_im.convert("L"), np.float32) / 255.0
wp = np.percentile(sil, 99.8)
sil_t = np.clip((sil - 0.055) / (wp - 0.055), 0, 1) ** 0.75

# casal por flood-fill /8
s8 = np.asarray(Image.fromarray((sil * 255).astype(np.uint8))
                .resize((W // 8, H // 8)), np.float32) / 255.0
mask = s8 < 0.09
seed = np.zeros_like(mask)
h8, w8 = mask.shape
for r, c in [(int(0.30 * h8), int(0.38 * w8)),
             (int(0.35 * h8), int(0.75 * w8)),
             (int(0.80 * h8), int(0.50 * w8))]:
    if mask[r, c]:
        seed[r, c] = True
prev = 0
for _ in range(1500):
    grown = seed.copy()
    grown[1:, :] |= seed[:-1, :]
    grown[:-1, :] |= seed[1:, :]
    grown[:, 1:] |= seed[:, :-1]
    grown[:, :-1] |= seed[:, 1:]
    seed = grown & mask
    s = seed.sum()
    if s == prev:
        break
    prev = s
couple = np.asarray(Image.fromarray((seed.astype(np.float32) * 255)
                                    .astype(np.uint8))
                    .resize((W, H)).filter(ImageFilter.GaussianBlur(6)),
                    np.float32) / 255.0
couple = smoothstep(couple, 0.35, 0.75)

# ---------- ultrassom: texto lateral + rosto ampliado ----------
us_im = ImageOps.exif_transpose(Image.open(US)).convert("L")
uw, uh = us_im.size
ua0 = np.asarray(us_im, np.float32) / 255.0

# (a) faixa de texto da direita do scan -> borda direita da arte
strip = us_im.crop((int(0.86 * uw), 0, uw, uh)).resize(
    (int(0.14 * uw * W / uw * 1.0), H), Image.LANCZOS)
strip_a = np.asarray(strip.filter(ImageFilter.GaussianBlur(1)),
                     np.float32) / 255.0
lo, hi = np.percentile(strip_a, 5), np.percentile(strip_a, 99.5)
strip_a = np.clip((strip_a - lo) / (hi - lo + 1e-6), 0, 1) ** 0.9
us_layer = np.zeros((H, W), np.float32)
sw = strip_a.shape[1]
us_layer[:, W - sw:] = strip_a * 0.55

# (b) rosto do bebe ampliado no vao de luz (esquerda)
face = us_im.crop((int(0.06 * uw), int(0.10 * uh),
                   int(0.84 * uw), int(0.80 * uh)))
face = face.filter(ImageFilter.GaussianBlur(1.0))
FW = int(W * 0.78)
FH = int(face.height * FW / face.width)
face = face.resize((FW, FH), Image.LANCZOS)
fa = np.asarray(face, np.float32) / 255.0
lo, hi = np.percentile(fa, 3), np.percentile(fa, 99.0)
fa = np.clip((fa - lo) / (hi - lo + 1e-6), 0, 1) ** 0.78
# mascara oval suave
fyy, fxx = np.mgrid[0:FH, 0:FW].astype(np.float32)
oval = 1 - smoothstep(np.hypot((fxx - FW / 2) / (FW / 2),
                               (fyy - FH / 2) / (FH / 2)), 0.72, 1.0)
fa *= oval

FX, FY = int(0.02 * W), int(0.05 * H)       # canto superior esquerdo
x1 = min(W, FX + FW)
y1 = min(H, FY + FH)
us_layer[FY:y1, FX:x1] = np.maximum(us_layer[FY:y1, FX:x1],
                                    fa[:y1 - FY, :x1 - FX] * 0.95)

# ---------- fundo ----------
small = Image.fromarray((sil * 255).astype(np.uint8)).resize((W // 8, H // 8))
Gm = np.asarray(small.filter(ImageFilter.GaussianBlur(30)), np.float32) / 255.0
thr = np.percentile(Gm, 99.2)
ys, xs = np.nonzero(Gm >= thr)
cx, cy = xs.mean() * 8, ys.mean() * 8

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dmax = max(np.hypot(cx, cy), np.hypot(W - cx, cy),
           np.hypot(cx, H - cy), np.hypot(W - cx, H - cy))
d = np.hypot(xx - cx, yy - cy) / dmax
grad = np.exp(-(d / 0.50) ** 2)
halo = np.exp(-(d / 0.20) ** 2) * 0.45
dv = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) / np.sqrt(2)
vign = 1 - 0.45 * smoothstep(dv, 0.52, 1.12)

bg = screen(grad * 0.40, us_layer)
bg = screen(bg, halo)
bg *= vign

bmin = 0.48 * (1 - smoothstep(yy / H, 0.60, 0.95)) * vign
light = np.maximum(sil_t, bmin * (1 - couple))
comp = bg * light

comp = np.clip(comp, 0, 1)
comp = comp + 0.07 * np.sin(2 * np.pi * (comp - 0.5)) * (comp * (1 - comp) * 4) * 0.5
rgb = sepia(np.clip(comp, 0, 1))

out = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
out.save(OUT1, "JPEG", quality=95, subsampling=0)
out.save(OUT2, "JPEG", quality=95, subsampling=0)
print("ok v5:", out.size)
