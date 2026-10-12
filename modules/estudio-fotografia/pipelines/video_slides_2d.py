#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Slideshow animado 2D tematico 'Ismael' — motion graphics com PIL+ffmpeg.

 - fundo papel creme com moldura dourada e particulas de luz subindo
 - fotos em cartao polaroid entram deslizando com rotacao que assenta
 - Ken Burns leve dentro do cartao apos a entrada
 - divisorias de secao com titulo e coracao dourado animados
 - secao das silhuetas em fundo escuro
 1080x1920 @ 30fps
"""
import math
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ALBUM = "/Users/flaviolima/Downloads/ensaio-gabi/album_final"
OUT = os.path.join(ALBUM, "VIDEO_Ismael_slides_animados.mp4")
W, H, FPS = 1080, 1920, 30
PHOTO_D = 2.5       # segundos por foto
XF = 0.4            # crossfade
FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")

GOLD = (205, 170, 110)
CREAM = (242, 235, 222)
INK = (52, 46, 60)

F = "/System/Library/Fonts/Supplemental/"
f_big = ImageFont.truetype(F + "Georgia Italic.ttf", 120)
f_mid = ImageFont.truetype(F + "Georgia Italic.ttf", 66)
f_sm = ImageFont.truetype(F + "Georgia.ttf", 34)


def smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def heart_pts(cx, cy, size, n=64):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = (13 * math.cos(t) - 5 * math.cos(2 * t)
             - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * size / 16.0, cy - y * size / 16.0))
    return pts


# ---------- fundos por secao ----------
def make_bg(dark=False, tint=(0, 0, 0)):
    base = (26, 22, 20) if dark else CREAM
    img = Image.new("RGB", (W, H), base)
    a = np.asarray(img, np.float32)
    if not dark and tint != (0, 0, 0):
        a = a * 0.92 + np.array(tint, np.float32) * 0.08
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) / 1.42
    v = 1 - (0.30 if dark else 0.16) * np.clip((d - 0.45) / 0.65, 0, 1) ** 2
    a *= v[..., None]
    n = np.random.default_rng(9).normal(0, 2.2, (H // 4 + 1, W // 4 + 1, 1))
    n = np.repeat(np.repeat(n, 4, 0), 4, 1)[:H, :W]
    img = Image.fromarray((a + n).clip(0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(img)
    g = GOLD if not dark else (178, 150, 104)
    dr.rectangle([46, 46, W - 46, H - 46], outline=g, width=2)
    dr.rectangle([58, 58, W - 58, H - 58], outline=g, width=1)
    dr.polygon(heart_pts(W // 2, 52, 13), fill=g)
    dr.line([W // 2 - 90, 52, W // 2 - 32, 52], fill=g, width=1)
    dr.line([W // 2 + 32, 52, W // 2 + 90, 52], fill=g, width=1)
    return np.asarray(img, np.float32)


BG_LIGHT = make_bg(False)
BG_AQUA = make_bg(False, (120, 180, 190))
BG_PEACH = make_bg(False, (235, 150, 110))
BG_DARK = make_bg(True)

# ---------- sprite de particula ----------
sp = Image.new("L", (72, 72), 0)
ImageDraw.Draw(sp).ellipse([18, 18, 54, 54], fill=255)
sp = sp.filter(ImageFilter.GaussianBlur(10))
SPRITE = sp

rng = np.random.default_rng(11)
PARTS = [(float(rng.uniform(60, W - 60)), float(rng.uniform(0, H)),
          float(rng.uniform(12, 38)), float(rng.uniform(0.5, 1.6)),
          float(rng.uniform(0, 6.28)), float(rng.uniform(18, 46)))
         for _ in range(16)]


def draw_particles(frame_img, t, dark):
    for (x0, y0, speed, tw, ph, size) in PARTS:
        y = (y0 - speed * t * FPS / 2) % (H + 120) - 60
        x = x0 + 26 * math.sin(t * tw + ph)
        alpha = 0.18 + 0.16 * (1 + math.sin(t * 2.1 + ph)) / 2
        if dark:
            alpha *= 1.5
        s = SPRITE.resize((int(size), int(size)))
        tint = Image.new("RGB", s.size, (255, 216, 150))
        mask = s.point(lambda p: int(p * alpha))
        frame_img.paste(tint, (int(x - size / 2), int(y - size / 2)), mask)


# ---------- cartao da foto ----------
def make_card(path, maxw=900, maxh=1330):
    im = ImageOps.contain(Image.open(os.path.join(ALBUM, path)), (maxw, maxh),
                          Image.LANCZOS)
    b = 16
    card = Image.new("RGB", (im.width + 2 * b, im.height + 2 * b),
                     (252, 250, 245))
    card.paste(im, (b, b))
    pad = 56
    spr = Image.new("RGBA", (card.width + 2 * pad, card.height + 2 * pad),
                    (0, 0, 0, 0))
    sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad - 6, pad + 10, pad + card.width + 6,
                                  pad + card.height + 22], fill=(20, 14, 10, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    spr.paste(sh, (0, 0), sh)
    spr.paste(card, (pad, pad))
    return spr


# ---------- writer ----------
proc = subprocess.Popen(
    [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
     "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "18",
     "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
    stdin=subprocess.PIPE)
TAIL = []           # frames finais do slide anterior p/ crossfade
XFN = int(XF * FPS)


def emit(frames):
    """recebe lista de np arrays; faz crossfade com TAIL anterior."""
    global TAIL
    for i, fr in enumerate(frames[:-XFN] if len(frames) > XFN else frames):
        if i < XFN and TAIL:
            a = smooth(i / XFN)
            fr = TAIL[i] * (1 - a) + fr * a
        proc.stdin.write(fr.astype(np.uint8).tobytes())
    TAIL = frames[-XFN:] if len(frames) > XFN else []


def photo_slide(path, bg, caption=None, dark=False, global_t0=0.0):
    card = make_card(path)
    n = int(PHOTO_D * FPS) + XFN
    frames = []
    ang0 = rng.uniform(-5, 5)
    ang1 = ang0 * 0.3
    side = 1 if rng.random() > 0.5 else -1
    for i in range(n):
        t = i / FPS
        p = ease_out(min(1.0, t / 0.55))          # entrada
        img = Image.fromarray(bg.astype(np.uint8)).copy()
        draw_particles(img, global_t0 + t, dark)
        # zoom lento pos-entrada
        hold = smooth(max(0.0, (t - 0.55) / (PHOTO_D - 0.55)))
        sc = 0.96 + 0.04 * p + 0.025 * hold
        ang = ang0 + (ang1 - ang0) * p
        c = card.rotate(ang, resample=Image.BICUBIC, expand=True)
        cw, ch = int(c.width * sc), int(c.height * sc)
        c = c.resize((cw, ch), Image.BILINEAR)
        x = W // 2 - cw // 2 + int(side * 420 * (1 - p))
        y = H // 2 - ch // 2 - 30 + int(140 * (1 - p))
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tmp.paste(c, (x, y), c)
        if p < 1:
            alpha = tmp.split()[3].point(lambda q: int(q * p))
            img.paste(tmp.convert("RGB"), (0, 0), alpha)
        else:
            img.paste(tmp.convert("RGB"), (0, 0), tmp.split()[3])
        if caption and t > 0.8:
            ca = smooth((t - 0.8) / 0.5)
            dr = ImageDraw.Draw(img)
            fill = tuple(int(v * ca + (26 if dark else 242) * (1 - ca))
                         for v in ((225, 210, 180) if dark else (110, 94, 74)))
            bb = dr.textbbox((0, 0), caption, font=f_mid)
            dr.text(((W - bb[2] + bb[0]) // 2, H - 190), caption,
                    font=f_mid, fill=fill)
        frames.append(np.asarray(img, np.float32))
    emit(frames)
    return global_t0 + n / FPS


def title_slide(title, sub, bg, dark=False, dur=2.6, big=False, global_t0=0.0):
    n = int(dur * FPS) + XFN
    frames = []
    fnt = f_big if big else f_mid
    ink = (235, 222, 200) if dark else INK
    for i in range(n):
        t = i / FPS
        img = Image.fromarray(bg.astype(np.uint8)).copy()
        draw_particles(img, global_t0 + t, dark)
        dr = ImageDraw.Draw(img)
        p = ease_out(min(1.0, t / 0.7))
        fade = min(1.0, (n - i) / (0.6 * FPS))
        a = p * fade
        # coracao que cresce
        hs = 30 * ease_out(min(1.0, t / 0.5))
        if hs > 2:
            g = tuple(int(v * a + (242 if not dark else 26) * (1 - a))
                      for v in GOLD)
            dr.polygon(heart_pts(W // 2, H // 2 - 240, hs), fill=g)
        bb = dr.textbbox((0, 0), title, font=fnt)
        ty = H // 2 - 120 + int(60 * (1 - p))
        col = tuple(int(v * a + (242 if not dark else 26) * (1 - a))
                    for v in ink)
        dr.text(((W - bb[2] + bb[0]) // 2, ty), title, font=fnt, fill=col)
        if sub and t > 0.45:
            sa = smooth((t - 0.45) / 0.5) * fade
            scol = tuple(int(v * sa + (242 if not dark else 26) * (1 - sa))
                         for v in ((190, 170, 140) if dark else (130, 112, 88)))
            bb2 = dr.textbbox((0, 0), sub, font=f_sm)
            dr.text(((W - bb2[2] + bb2[0]) // 2, ty + 230), sub,
                    font=f_sm, fill=scol)
        frames.append(np.asarray(img, np.float32))
    emit(frames)
    return global_t0 + n / FPS


files = sorted(f for f in os.listdir(ALBUM)
               if f[:2].isdigit() and f.lower().endswith((".jpg", ".png")))
sec = {"jardim": range(1, 22), "piscina": range(22, 28),
       "silhueta": range(28, 37), "praia": range(37, 54)}

gt = 0.0
gt = title_slide("Ismael", "o ensaio da espera  ·  2026", BG_LIGHT,
                 big=True, dur=3.2, global_t0=gt)
gt = title_slide("O começo do dia", "making-of e os primeiros sorrisos",
                 BG_LIGHT, global_t0=gt)
for f in files:
    num = int(f[:2])
    if num in sec["jardim"]:
        gt = photo_slide(f, BG_LIGHT, global_t0=gt)
gt = title_slide("Entre risos e água", "a leveza de esperar por você",
                 BG_AQUA, global_t0=gt)
for f in files:
    num = int(f[:2])
    if num in sec["piscina"]:
        gt = photo_slide(f, BG_AQUA, global_t0=gt)
gt = title_slide("Na luz e na sombra", "quando o amor vira silhueta",
                 BG_DARK, dark=True, global_t0=gt)
for f in files:
    num = int(f[:2])
    if num in sec["silhueta"]:
        gt = photo_slide(f, BG_DARK, dark=True, global_t0=gt)
gt = title_slide("O pôr do sol", "o mar guardou o segredo até aqui",
                 BG_PEACH, global_t0=gt)
for f in files:
    num = int(f[:2])
    if num in sec["praia"]:
        gt = photo_slide(f, BG_PEACH, global_t0=gt)
gt = title_slide("Te esperamos com amor,", "", BG_LIGHT, dur=1.6, global_t0=gt)
gt = title_slide("Ismael", "♥".replace("♥", ""), BG_LIGHT, big=True,
                 dur=3.0, global_t0=gt)

# despeja o tail final com fade-out
for i, fr in enumerate(TAIL):
    a = 1 - smooth(i / max(1, len(TAIL)))
    proc.stdin.write((fr * a).astype(np.uint8).tobytes())
proc.stdin.close()
proc.wait()
print("SLIDES 2D PRONTOS:", OUT)
