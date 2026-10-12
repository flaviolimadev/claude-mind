#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Video do album: Ken Burns + crossfades, 1080x1920@30fps, h264.

 - titulo de abertura e cartela final em serifa elegante
 - 53 fotos na ordem do album, ~2.7s cada + fade de 0.6s
 - zoom alternado in/out com pan sutil (deterministico)
"""
import os
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ALBUM = "/Users/flaviolima/Downloads/ensaio-gabi/album_final"
OUT = "/Users/flaviolima/Downloads/ensaio-gabi/album_final/VIDEO_ensaio_gabi.mp4"
W, H, FPS = 1080, 1920, 30
DUR = 2.7          # segundos visiveis por foto
XF = 0.6           # crossfade
ZOOM = 1.09

files = sorted(f for f in os.listdir(ALBUM)
               if f[:2].isdigit() and f.lower().endswith((".jpg", ".png")))
print(len(files), "fotos")

FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
proc = subprocess.Popen(
    [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
     "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "18",
     "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
    stdin=subprocess.PIPE)


def write(frame):
    proc.stdin.write(frame.astype(np.uint8).tobytes())


def smooth(t):
    return t * t * (3 - 2 * t)


def load_cover(path, scale=1.5):
    im = Image.open(path).convert("RGB")
    # cover para W*scale x H*scale
    tw, th = int(W * scale), int(H * scale)
    s = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1),
                   Image.LANCZOS)
    x0 = (im.width - tw) // 2
    y0 = (im.height - th) // 2
    return im.crop((x0, y0, x0 + tw, y0 + th))


def kb_frame(src, t, zoom_in, pan):
    """t em 0..1; retorna frame numpy do Ken Burns."""
    z0, z1 = (1.0, ZOOM) if zoom_in else (ZOOM, 1.0)
    z = z0 + (z1 - z0) * smooth(t)
    cw, ch = src.width / z, src.height / z
    maxx = src.width - cw
    maxy = src.height - ch
    cx = maxx * (0.5 + pan[0] * (t - 0.5))
    cy = maxy * (0.5 + pan[1] * (t - 0.5))
    cx = min(max(cx, 0), maxx)
    cy = min(max(cy, 0), maxy)
    f = src.resize((W, H), Image.BILINEAR, box=(cx, cy, cx + cw, cy + ch))
    return np.asarray(f, np.float32)


def text_card(lines, sub=None):
    img = Image.new("RGB", (W, H), (10, 9, 8))
    dr = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Italic.ttf", 92)
        f2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 40)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    y = H // 2 - 80 * len(lines)
    for ln in lines:
        bb = dr.textbbox((0, 0), ln, font=f1)
        dr.text(((W - bb[2] + bb[0]) // 2, y), ln, font=f1,
                fill=(232, 220, 200))
        y += (bb[3] - bb[1]) + 50
    if sub:
        bb = dr.textbbox((0, 0), sub, font=f2)
        dr.text(((W - bb[2] + bb[0]) // 2, y + 30), sub, font=f2,
                fill=(170, 155, 135))
    return np.asarray(img, np.float32)


def emit_card(card, dur, fade=0.8):
    n = int(dur * FPS)
    nf = int(fade * FPS)
    for i in range(n):
        a = 1.0
        if i < nf:
            a = i / nf
        elif i > n - nf:
            a = (n - i) / nf
        write(card * a)


XFN = int(XF * FPS)
CLIPN = int(DUR * FPS)
rng = np.random.default_rng(5)

# abertura
emit_card(text_card(["Ismael"], "o ensaio da espera  ·  Gabi  ·  2026"), 3.6)

prev_tail = None
for idx, f in enumerate(files):
    src = load_cover(os.path.join(ALBUM, f))
    zoom_in = idx % 2 == 0
    pan = (float(rng.uniform(-0.55, 0.55)), float(rng.uniform(-0.35, 0.35)))
    total = CLIPN + XFN
    frames_this = []
    for i in range(total):
        t = i / (total - 1)
        fr = kb_frame(src, t, zoom_in, pan)
        if i < XFN and prev_tail is not None:
            a = smooth(i / XFN)
            fr = prev_tail[i] * (1 - a) + fr * a
        if i < total - XFN or idx == len(files) - 1:
            if i < XFN and prev_tail is None and idx == 0:
                fr = fr * smooth(i / XFN)   # fade-in do preto na 1a foto
            write(fr)
        else:
            if len(frames_this) == 0:
                frames_this = []
            frames_this.append(fr)
    prev_tail = frames_this if frames_this else None
    if idx == len(files) - 1:
        # fade out final
        for i in range(XFN):
            write(fr * (1 - smooth(i / XFN)))
    print(f"clip {idx+1}/{len(files)} ok", flush=True)

# cartela final
emit_card(text_card(["Te esperamos", "com amor, Ismael"]), 3.8)

proc.stdin.close()
proc.wait()
print("VIDEO PRONTO:", OUT)
