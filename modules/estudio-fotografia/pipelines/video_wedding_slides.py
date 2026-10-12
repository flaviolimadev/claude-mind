#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Slideshow v4 — replica fiel do template 'Wedding Slides':

 - camera em push continuo: foto nasce pequena, cresce, e a camera a
   ATRAVESSA (desfoca + clarao rose) enquanto a proxima surge atras
 - texto viaja ancorado a lateral da foto (escala com a cena)
 - fundo = a propria foto ultra-desfocada + lavagem blush
 - fios de brilho verticais caindo + bokeh grande + light leak
 1080x1920 @ 30fps, sem cortes: um unico movimento continuo
"""
import math
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ALBUM = "/Users/flaviolima/Downloads/ensaio-gabi/album_final"
OUT = os.path.join(ALBUM, "VIDEO_Ismael_slides_animados.mp4")
W, H, FPS = 1080, 1920, 30
D = 2.9                       # duracao por foto
FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")

F = "/System/Library/Fonts/Supplemental/"
f_serif = ImageFont.truetype(F + "Georgia Italic.ttf", 124)
f_caps = ImageFont.truetype(F + "Georgia.ttf", 27)
f_caps2 = ImageFont.truetype(F + "Georgia.ttf", 21)


def sstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


files = sorted(f for f in os.listdir(ALBUM)
               if f[:2].isdigit() and f.lower().endswith((".jpg", ".png")))
N = len(files)


def section_of(f):
    n = int(f[:2])
    return ("O COMEÇO DO DIA" if n <= 21 else
            "ENTRE RISOS E ÁGUA" if n <= 27 else
            "NA LUZ E NA SOMBRA" if n <= 36 else
            "O PÔR DO SOL")


# ---------- base blush ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
g = yy / H
BLUSH = (np.array([248, 238, 231], np.float32)[None, None, :] * (1 - g[..., None])
         + np.array([240, 221, 212], np.float32)[None, None, :] * g[..., None])
d0 = np.hypot((xx - W * 0.42) / W, (yy - H * 0.36) / H)
BLUSH += (30 * np.exp(-(d0 / 0.5) ** 2))[..., None]
BLUSH = np.clip(BLUSH, 0, 255)

# light leak
lk = Image.new("RGB", (W, H), (0, 0, 0))
dl = ImageDraw.Draw(lk)
dl.ellipse([-320, -260, 650, 760], fill=(85, 58, 40))
dl.ellipse([W - 480, H - 860, W + 380, H + 180], fill=(66, 44, 34))
LEAK = np.asarray(lk.filter(ImageFilter.GaussianBlur(170)), np.float32)

# flash radial do zoom-through
fl = Image.new("L", (W, H), 0)
ImageDraw.Draw(fl).ellipse([W * 0.5 - 900, H * 0.5 - 1100,
                            W * 0.5 + 900, H * 0.5 + 1100], fill=255)
FLASH = (np.asarray(fl.filter(ImageFilter.GaussianBlur(220)),
                    np.float32) / 255.0)[..., None]
FLASH_RGB = np.array([255, 243, 238], np.float32)

# fios de brilho verticais (cortina de glitter)
rng = np.random.default_rng(31)
STRANDS = []
for _ in range(20):
    STRANDS.append((float(rng.uniform(30, W - 30)),
                    float(rng.uniform(0, H)),
                    float(rng.uniform(70, 150)),     # velocidade
                    float(rng.uniform(40, 120)),     # comprimento
                    float(rng.uniform(0.18, 0.4)),   # alpha
                    float(rng.uniform(0, 6.28))))
BOKEH = [(float(rng.uniform(0, W)), float(rng.uniform(0, H)),
          float(rng.uniform(90, 240)), float(rng.uniform(0.05, 0.14)),
          float(rng.uniform(0, 6.28)), float(rng.uniform(4, 12)))
         for _ in range(7)]
bok = Image.new("L", (160, 160), 0)
ImageDraw.Draw(bok).ellipse([14, 14, 146, 146], fill=255)
BOK = bok.filter(ImageFilter.GaussianBlur(9))


def draw_fx(img, t):
    dr = ImageDraw.Draw(img, "RGBA")
    for (x0, y0, sp, ln, al, ph) in STRANDS:
        y = (y0 + sp * t) % (H + 220) - 110
        x = x0 + 9 * math.sin(t * 0.8 + ph)
        a = int(255 * al * (0.6 + 0.4 * math.sin(t * 3 + ph)))
        dr.line([x, y, x, y + ln], fill=(255, 248, 235, a), width=2)
        dr.ellipse([x - 3, y + ln - 3, x + 3, y + ln + 3],
                   fill=(255, 250, 240, min(255, a + 50)))
    for (x0, y0, size, al, ph, drift) in BOKEH:
        x = x0 + drift * 10 * math.sin(t * 0.12 + ph)
        y = (y0 + 14 * t) % (H + size) - size / 2
        s = int(size)
        spr = BOK.resize((s, s))
        tint = Image.new("RGB", (s, s), (255, 240, 226))
        a = al * (0.7 + 0.3 * math.sin(t * 0.9 + ph))
        img.paste(tint, (int(x - s / 2), int(y - s / 2)),
                  spr.point(lambda p: int(p * a)))


# ---------- cards (lazy, cache 3 fotos) ----------
_cache = {}


def get_assets(f):
    if f in _cache:
        return _cache[f]
    im = ImageOps.contain(Image.open(os.path.join(ALBUM, f)), (800, 1140),
                          Image.LANCZOS)
    b = 15
    card = Image.new("RGB", (im.width + 2 * b, im.height + 2 * b),
                     (253, 251, 248))
    card.paste(im, (b, b))
    pad = 40
    spr = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad),
                    (0, 0, 0, 0))
    sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [pad - 3, pad + 7, pad + card.width + 3, pad + card.height + 13],
        fill=(80, 56, 44, 80))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    spr.paste(sh, (0, 0), sh)
    spr.paste(card, (pad, pad))
    blur1 = spr.filter(ImageFilter.GaussianBlur(7))
    blur2 = spr.filter(ImageFilter.GaussianBlur(22))
    # fundo: foto cobrindo o quadro, ultra blur
    big = ImageOps.fit(Image.open(os.path.join(ALBUM, f)), (W // 3, H // 3))
    big = big.filter(ImageFilter.GaussianBlur(26)).resize((W, H),
                                                          Image.BILINEAR)
    bg = (np.asarray(big, np.float32) * 0.42 + BLUSH * 0.58)
    assets = (spr, blur1, blur2, bg)
    if len(_cache) > 3:
        _cache.pop(next(iter(_cache)))
    _cache[f] = assets
    return assets


def spaced(dr, x, y, txt, fnt, fill, ls):
    for ch in txt:
        dr.text((x, y), ch, font=fnt, fill=fill)
        bb = dr.textbbox((0, 0), ch, font=fnt)
        x += (bb[2] - bb[0]) + ls
    return x


def label_sprite(section):
    s = Image.new("RGBA", (460, 170), (0, 0, 0, 0))
    dr = ImageDraw.Draw(s)
    spaced(dr, 6, 10, "ISMAEL", f_caps, (120, 98, 86, 255), 9)
    dr.line([8, 62, 180, 62], fill=(186, 152, 110, 230), width=2)
    spaced(dr, 6, 78, section, f_caps2, (140, 118, 104, 235), 4)
    return s


LABELS = {s: label_sprite(s) for s in
          ["O COMEÇO DO DIA", "ENTRE RISOS E ÁGUA",
           "NA LUZ E NA SOMBRA", "O PÔR DO SOL"]}

proc = subprocess.Popen(
    [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt",
     "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "18",
     "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
    stdin=subprocess.PIPE)


def card_at(img, f, scale, cx, cy, tilt, blur_mix=0.0, alpha=1.0,
            with_label=True, label_a=1.0):
    spr, b1, b2, _ = get_assets(f)
    if blur_mix <= 0.05:
        src = spr
    elif blur_mix < 0.5:
        src = Image.blend(spr, b1, blur_mix * 2)
    else:
        src = Image.blend(b1, b2, min(1.0, (blur_mix - 0.5) * 2))
    cw = max(2, int(src.width * scale))
    ch = max(2, int(src.height * scale))
    c = src.resize((cw, ch), Image.BILINEAR)
    if abs(tilt) > 0.2:
        c = c.rotate(tilt, resample=Image.BILINEAR, expand=True)
    a = c.split()[3]
    if alpha < 1.0:
        a = a.point(lambda p: int(p * alpha))
    x, y = int(cx - c.width / 2), int(cy - c.height / 2)
    img.paste(c, (x, y), a)
    if with_label and label_a > 0.03 and scale > 0.42:
        lab = LABELS[section_of(f)]
        lsc = max(0.3, scale * 0.95)
        ls = lab.resize((int(lab.width * lsc), int(lab.height * lsc)),
                        Image.BILINEAR)
        la = ls.split()[3].point(lambda p: int(p * label_a * alpha))
        if tilt >= 0:
            lx = int(cx - c.width / 2 - ls.width + 30 * scale)
        else:
            lx = int(cx + c.width / 2 - 30 * scale)
        ly = int(cy - ls.height / 2 + 30)
        lx = max(14, min(lx, W - ls.width - 14))
        img.paste(ls, (lx, ly), la)
    return c.width, c.height


S0, S1 = 0.40, 2.65           # escala inicial/final do push
K = math.log(S1 / S0)


def write_frame(arr):
    proc.stdin.write(arr.clip(0, 255).astype(np.uint8).tobytes())


def photo_stream(t_global):
    nF = int(D * FPS)
    for idx in range(N):
        f = files[idx]
        nxt = files[idx + 1] if idx < N - 1 else None
        _, _, _, bg = get_assets(f)
        side = 1 if idx % 2 == 0 else -1
        tilt = side * 2.2
        for i in range(nF):
            tn = i / nF
            ta = t_global + i / FPS
            img = Image.fromarray(bg.astype(np.uint8)).copy()
            # proxima foto surgindo ao fundo (antes da principal)
            if nxt and tn > 0.70:
                p2 = (tn - 0.70) / 0.30
                s2 = S0 * math.exp(K * (p2 * (1.0 / nF * FPS * 0) + 0))  # S0
                s2 = S0 * (0.85 + 0.15 * sstep(p2))
                card_at(img, nxt, s2,
                        W / 2 - side * 30 * (1 - p2),
                        H / 2 - 50, -side * 2.2,
                        alpha=sstep(p2 * 1.6),
                        label_a=0.0)
            # foto principal: push exponencial
            s = S0 * math.exp(K * tn)
            bmix = max(0.0, (s - 1.35) / (2.3 - 1.35))
            fade = 1.0 - min(1.0, max(0.0, (s - 1.85) / (S1 - 1.85)))
            drift_x = W / 2 + side * 46 * (1 - tn) + 10 * math.sin(ta * 0.5)
            drift_y = H / 2 - 50 + 26 * (tn - 0.5) + 8 * math.sin(ta * 0.33)
            label_a = sstep((tn - 0.08) / 0.22) * (1 - sstep((tn - 0.78) / 0.16))
            card_at(img, f, s, drift_x, drift_y, tilt,
                    blur_mix=bmix, alpha=fade, label_a=label_a)
            # fx
            draw_fx(img, ta)
            arr = np.asarray(img, np.float32)
            arr = 255 - (255 - arr) * (1 - LEAK *
                                       (0.7 + 0.3 * math.sin(ta * 0.45)) / 255)
            # clarao do zoom-through
            fa = math.exp(-((tn - 1.0) * D / 0.26) ** 2) * 0.9
            fa += math.exp(-((tn - 0.0) * D / 0.26) ** 2) * 0.9 if idx > 0 else 0
            if fa > 0.02:
                arr = arr * (1 - FLASH * fa) + FLASH_RGB * FLASH * fa
            write_frame(arr)
        t_global += D
    return t_global


def title_card(big, sub, dur, t_global, fade_from_white=False):
    n = int(dur * FPS)
    for i in range(n):
        t = i / n
        ta = t_global + i / FPS
        img = Image.fromarray(BLUSH.astype(np.uint8)).copy()
        draw_fx(img, ta)
        dr = ImageDraw.Draw(img, "RGBA")
        p = sstep(t / 0.35)
        fo = 1 - sstep((t - 0.78) / 0.22)
        a = p * fo
        bb = dr.textbbox((0, 0), big, font=f_serif)
        ty = H // 2 - 170 + int(40 * (1 - p))
        dr.text(((W - bb[2] + bb[0]) // 2, ty), big, font=f_serif,
                fill=(92, 76, 86, int(255 * a)))
        if sub:
            tw = sum(dr.textbbox((0, 0), c, font=f_caps)[2] + 8 for c in sub)
            spaced(dr, (W - tw) / 2, ty + 240, sub, f_caps,
                   (150, 124, 104, int(235 * a)), 8)
            dr.line([W / 2 - 66, ty + 220, W / 2 + 66, ty + 220],
                    fill=(186, 152, 110, int(220 * a)), width=1)
        arr = np.asarray(img, np.float32)
        arr = 255 - (255 - arr) * (1 - LEAK * 0.75 / 255)
        if fade_from_white and t < 0.3:
            wa = (1 - t / 0.3) * 0.8
            arr = arr * (1 - FLASH * wa) + FLASH_RGB * FLASH * wa
        write_frame(arr)
    return t_global + dur


gt = 0.0
gt = title_card("Ismael", "O ENSAIO DA ESPERA · 2026", 3.4, gt)
gt = photo_stream(gt)
gt = title_card("Ismael", "TE ESPERAMOS COM AMOR", 3.8, gt,
                fade_from_white=True)
proc.stdin.close()
proc.wait()
print("V4 PRONTO:", OUT)
