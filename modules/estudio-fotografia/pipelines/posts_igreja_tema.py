#!/usr/bin/env python3
"""Motor de posts p/ eventos de igreja (origem: Mocidade Betfage, out/2026) — 17 estilos de
referências (cards arredondados, zoom/spin-blur, fatias, faixas, seleção nítida, polaroid,
countdown c/ recorte, leque, painéis P&B, frames, radial-título, tripla, bandas, mosaico).
Ajuste TEXTURAS/paleta por projeto.
17 estilos desconstruídos de ESTUDOS.md (R01–R19). REGRA: o rosto nunca é alterado —
só grade global, grão, blur em máscara FORA do sujeito, recorte por segmentação local,
molduras, colagens e tipografia. Nada generativo.

Uso (em código):  from betfage_posts import *;  cards_arredondados([...], "out.jpg", ...)
Formatos: feed 1080×1350 (padrão). Todas as funções recebem caminhos de fotos e gravam `out`.
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1350
# paleta do tema "REVESTIDOS DE AUTORIDADE" (Mt 10:1) — manda em tudo
NAVY = (20, 28, 63)
INDIGO = (58, 74, 138)
LAVENDER = (138, 148, 200)
OFFWHITE = (232, 233, 244)
GOLD = (217, 165, 87)
# acentos herdados das refs (usar com parcimônia; o padrão agora é GOLD)
LIME = GOLD
ORANGE = GOLD
RED = (178, 48, 58)
PAPER = (243, 239, 231)
PETROL = NAVY
INK = (18, 18, 20)
TAGS = (("MOCIDADE", INDIGO), ("BETFAGE", (90, 70, 160)), ("MT 10:1", GOLD), ("2026", LAVENDER))

_F = "/System/Library/Fonts/"
_S = _F + "Supplemental/"


def font(kind, size):
    """kind: cond (Avenir Next Condensed Bold), condm (Medium), script (Snell Black),
    serif (Didot), serifi (Didot Italic), sans (HelveticaNeue), mono (Menlo)."""
    try:
        if kind == "cond":
            return ImageFont.truetype(_F + "Avenir Next Condensed.ttc", size, index=0)
        if kind == "condm":
            return ImageFont.truetype(_F + "Avenir Next Condensed.ttc", size, index=5)
        if kind == "script":
            return ImageFont.truetype(_S + "SnellRoundhand.ttc", size, index=2)
        if kind == "serif":
            return ImageFont.truetype(_S + "Didot.ttc", size, index=0)
        if kind == "serifi":
            return ImageFont.truetype(_S + "Didot.ttc", size, index=1)
        if kind == "sans":
            return ImageFont.truetype(_F + "HelveticaNeue.ttc", size, index=0)
        if kind == "mono":
            return ImageFont.truetype(_F + "Menlo.ttc", size, index=0)
    except OSError:
        pass
    return ImageFont.load_default()


# ----------------------------------------------------------------- base
def load(path):
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def cover(im, w, h, fx=0.5, fy=0.42):
    """cobre w×h mantendo proporção; (fx,fy) = ponto de interesse (rosto) a preservar."""
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x0 = int(min(max(fx * im.width - w / 2, 0), im.width - w))
    y0 = int(min(max(fy * im.height - h / 2, 0), im.height - h))
    return im.crop((x0, y0, x0 + w, y0 + h))


def to_np(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def to_im(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def blur_np(a, r):
    """blur gaussiano em array float (2D ou HxWx3) preservando a forma de entrada."""
    if a.ndim == 2:
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
        return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0
    return to_np(to_im(a).filter(ImageFilter.GaussianBlur(r)))


def smoothstep(x, a, b):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------- correção + grades
def corrigir(a):
    """igreja de parede branca: exposição por mediana central (alvo BAIXO, mood escuro das refs)
    com trava de highlights (p99 ≤ 0.88) + ombro forte nas altas-luzes + WB amortecido."""
    h, w = a.shape[:2]
    c = a[h // 4: 3 * h // 4, w // 4: 3 * w // 4].mean(axis=-1)
    g = float(np.clip(0.34 / max(np.median(c), 0.02), 0.6, 2.2))
    g = min(g, 0.88 / max(float(np.percentile(c, 99)), 0.05))
    a = np.clip(a * g, 0, 1)
    t = np.maximum(a - 0.70, 0)
    a = np.where(a > 0.70, 0.70 + t / (1 + t / 0.24), a)      # assíntota 0.94: nada estoura
    a = np.clip(a, 0, 1)
    med = a.reshape(-1, 3).mean(axis=0)
    corr = np.clip(1 + 0.45 * (med.mean() / np.maximum(med, 1e-4) - 1), 0.88, 1.15)
    return np.clip(a * corr, 0, 1)


def teal_orange(a, forca=1.0):
    lum = a.mean(axis=-1, keepdims=True)
    sh = np.clip(1 - lum / 0.45, 0, 1)
    hi = np.clip((lum - 0.55) / 0.45, 0, 1)
    a = a + sh * np.array([-0.035, 0.0, 0.055]) * forca + hi * np.array([0.045, 0.015, -0.03]) * forca
    a = np.clip(a, 0, 1)
    a = a + 0.12 * np.sin(2 * np.pi * (a - 0.5)) * (a * (1 - a) * 4) * 0.5
    a = np.clip(a, 0, 1)
    m = np.array([0.025, 0.028, 0.040])
    a = m + a * (1 - m)
    mean = a.mean(axis=-1, keepdims=True)
    return np.clip(mean + (a - mean) * 1.10, 0, 1)


def navy_gold(a, forca=1.0):
    """grade do tema: sombras navy/índigo, altas-luzes e pele douradas, pretos azulados."""
    lum = a.mean(axis=-1, keepdims=True)
    sh = np.clip(1 - lum / 0.45, 0, 1)
    hi = np.clip((lum - 0.55) / 0.45, 0, 1)
    a = a + sh * np.array([-0.045, -0.02, 0.065]) * forca + hi * np.array([0.04, 0.025, -0.03]) * forca
    a = np.clip(a, 0, 1)
    a = a + 0.07 * np.sin(2 * np.pi * (a - 0.5)) * (a * (1 - a) * 4) * 0.5
    a = np.clip(a, 0, 1) * 0.96                                  # teto: altas-luzes nunca brancas
    m = np.array([0.03, 0.035, 0.06])
    a = m + a * (1 - m)
    mean = a.mean(axis=-1, keepdims=True)
    return np.clip(mean + (a - mean) * 1.08, 0, 1)


def halftone(w, h, cell=14, color=LAVENDER, alpha=70, seed=3, fade=None):
    """camada RGBA de pontos de halftone (textura do tema); fade=(x0,x1) frac p/ esvanecer."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = np.random.default_rng(seed)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            f = 1.0
            if fade:
                f = float(np.clip((x / w - fade[0]) / (fade[1] - fade[0] + 1e-6), 0, 1))
            r = cell * 0.18 + cell * 0.22 * f + rng.normal(0, 0.4)
            if r > 0.8:
                d.ellipse([x - r, y - r, x + r, y + r], fill=color + (int(alpha * (0.5 + 0.5 * f)),))
    return layer


def grunge_mask(w, h, seed=7, density=0.22, blur=1.2):
    """máscara L de desgaste (manchas) p/ dar textura a títulos como na arte do tema."""
    rng = np.random.default_rng(seed)
    n = rng.random((h // 3 + 1, w // 3 + 1))
    m = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(m, np.float32) / 255
    a = np.where(a < density, 0.0, 1.0)
    return Image.fromarray((a * 255).astype(np.uint8))


def grunge_text(canvas, xy, txt, fnt, fill=OFFWHITE, seed=7, density=0.2, center=True):
    """texto com textura grunge (buracos) — igual às letras de 'REVESTIDOS'."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = text_w(fnt, txt, d)
    x = xy[0] - w // 2 if center else xy[0]
    d.text((x, xy[1]), txt, font=fnt, fill=fill + (255,))
    g = grunge_mask(canvas.width, canvas.height, seed, density)
    a = layer.split()[3]
    a = Image.fromarray((np.asarray(a, np.float32) * np.asarray(g, np.float32) / 255).astype(np.uint8))
    layer.putalpha(a)
    canvas.paste(layer, (0, 0), layer)


def pb(a, contraste=1.25):
    L = a[..., 0] * 0.36 + a[..., 1] * 0.50 + a[..., 2] * 0.14
    L = np.clip((L - 0.5) * contraste + 0.5, 0, 1)
    L = L + 0.10 * np.sin(2 * np.pi * (L - 0.5)) * (L * (1 - L) * 4) * 0.5
    L = 0.02 + np.clip(L, 0, 1) * 0.97
    return np.stack([L] * 3, -1)


def sepia(a):
    L = a.mean(axis=-1, keepdims=True)
    tint = L * np.array([1.06, 0.93, 0.78])
    a = np.clip(a * 0.4 + tint * 0.6, 0, 1)
    a = 0.04 + a * 0.95
    return np.clip(a + 0.08 * np.sin(2 * np.pi * (a - 0.5)) * (a * (1 - a) * 4) * 0.5, 0, 1)


def grain(im, amt=0.045, seed=3):
    a = to_np(im)
    h, w = a.shape[:2]
    g = np.random.default_rng(seed).normal(0, 1, (h // 2 + 1, w // 2 + 1))
    gi = Image.fromarray(((g * 0.5 + 0.5).clip(0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    gn = (np.asarray(gi, np.float32) / 255 - 0.5) * 2
    return to_im(a + (gn * amt)[..., None])


def vinheta(im, amt=0.3):
    a = to_np(im)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / math.sqrt(2)
    return to_im(a * (1 - amt * smoothstep(d, 0.5, 1.15))[..., None])


def halation(im, thr=0.75, strength=0.2, color=(1.0, 0.7, 0.4)):
    a = to_np(im)
    hl = smoothstep(a.mean(axis=-1), thr, 0.97)
    glow = blur_np(hl, 35)
    return to_im(1 - (1 - a) * (1 - np.clip(glow[..., None] * np.array(color) * strength, 0, 1)))


def grade(im, estilo="teal", corr=True):
    a = to_np(im)
    if corr:
        a = corrigir(a)
    if estilo == "teal":          # padrão do projeto = navy & gold (tema)
        a = navy_gold(a)
    elif estilo == "tealorange":  # teal & orange das refs, só se pedido
        a = teal_orange(a)
    elif estilo == "pb":
        a = pb(a)
    elif estilo == "sepia":
        a = sepia(a)
    elif estilo == "navy":
        a = navy_gold(a, 1.5)
    return to_im(a)


# ----------------------------------------------------------------- efeitos (sempre em máscara fora do sujeito)
def radial_mask(w, h, cx, cy, r_in, r_out, ellipse=1.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot((xx - cx), (yy - cy) * ellipse)
    return smoothstep(d, r_in, r_out)


def zoom_blur(im, cx, cy, r_in, r_out, strength=0.18, n=14):
    """blur de zoom progressivo fora do raio: média de cópias escaladas a partir do centro."""
    w, h = im.size
    base = to_np(im)
    acc = np.zeros_like(base)
    for i in range(n):
        s = 1 + strength * i / (n - 1)
        big = im.resize((int(w * s) + 1, int(h * s) + 1), Image.BILINEAR)
        x0 = int(cx * s - cx)
        y0 = int(cy * s - cy)
        acc += to_np(big.crop((x0, y0, x0 + w, y0 + h)))
    blurred = acc / n
    m = radial_mask(w, h, cx, cy, r_in, r_out)[..., None]
    return to_im(base * (1 - m) + blurred * m)


def spin_blur(im, cx, cy, r_in, r_out, graus=10, n=16):
    w, h = im.size
    base = to_np(im)
    acc = np.zeros_like(base)
    for i in range(n):
        ang = -graus + 2 * graus * i / (n - 1)
        acc += to_np(im.rotate(ang, resample=Image.BILINEAR, center=(cx, cy)))
    m = radial_mask(w, h, cx, cy, r_in, r_out)[..., None]
    return to_im(base * (1 - m) + (acc / n) * m)


def motion_blur_h(im, px=40, n=12):
    a = to_np(im)
    acc = np.zeros_like(a)
    for i in range(n):
        dx = int(-px / 2 + px * i / (n - 1))
        acc += np.roll(a, dx, axis=1)
    return to_im(acc / n)


def gauss(im, r):
    return im.filter(ImageFilter.GaussianBlur(r))


def shadow_paste(canvas, layer_rgba, xy, blur=22, alpha=110, off=(10, 18)):
    sh = Image.new("RGBA", (layer_rgba.width + 2 * blur * 3, layer_rgba.height + 2 * blur * 3), (0, 0, 0, 0))
    a = layer_rgba.split()[3].point(lambda p: int(p * alpha / 255))
    sh.paste((0, 0, 0, 255), (blur * 3 + off[0], blur * 3 + off[1]), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(sh, (xy[0] - blur * 3, xy[1] - blur * 3), sh)
    canvas.paste(layer_rgba, xy, layer_rgba)


def rounded_card(im, w, h, radius=60, rot=0.0, fx=0.5, fy=0.42, border=0, border_color=(255, 255, 255)):
    c = cover(im, w, h, fx, fy).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    c.putalpha(mask)
    if border:
        bg = Image.new("RGBA", (w + 2 * border, h + 2 * border), (0, 0, 0, 0))
        m2 = Image.new("L", bg.size, 0)
        ImageDraw.Draw(m2).rounded_rectangle([0, 0, bg.width - 1, bg.height - 1], radius=radius + border, fill=255)
        bg.paste(border_color + (255,), (0, 0), m2)
        bg.paste(c, (border, border), c)
        c = bg
    if rot:
        c = c.rotate(rot, expand=True, resample=Image.BICUBIC)
    return c


def poly_card(im, w, h, pts, fx=0.5, fy=0.42):
    """recorte poligonal (paralelogramo/trapézio) de uma foto coberta em w×h."""
    c = cover(im, w, h, fx, fy).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    c.putalpha(mask)
    return c


def paper(w, h, color=PAPER, seed=5, noise=6):
    a = np.zeros((h, w, 3), np.float32) + np.array(color, np.float32)
    n = np.random.default_rng(seed).normal(0, noise, (h // 2 + 1, w // 2 + 1))
    ni = Image.fromarray((n + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    a += (np.asarray(ni, np.float32) - 128)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


TEX = os.path.expanduser("~/Downloads/mocidade-betfage/texturas/")
TEXTURAS = {
    "leak": TEX + "tx1_lightleak_poeira.jpg",   # vazamento de luz + poeira (screen)
    "mancha": TEX + "tx2_mancha_marrom.jpg",    # manchas marrons (fundo, tingir de navy)
    "rastros": TEX + "tx3_rastros_luz.jpg",     # rastros de luz (screen)
    "grao": TEX + "tx4_grao_escuro.jpg",        # grão escuro (screen leve)
    "couro": TEX + "tx5_couro_preto.jpg",       # couro preto (fundo / multiply)
    "circulo": TEX + "tx6_circulo_laranja.jpg",  # círculo laranja + papel amassado (screen)
}


def texture(canvas, nome, modo="screen", opacity=0.5, tint=None, fx=0.5, fy=0.5):
    """sobrepõe uma textura do cliente ao canvas (RGB). modo: screen | multiply | soft.
    tint: cor (r,g,b 0-1) p/ colorizar a textura pela luminância (ex.: navy)."""
    tex = cover(load(TEXTURAS[nome]), canvas.width, canvas.height, fx, fy)
    t = to_np(tex)
    if tint is not None:
        L = t.mean(axis=-1, keepdims=True)
        t = np.clip(L * np.array(tint) * 1.6, 0, 1)
    a = to_np(canvas)
    if modo == "screen":
        r = 1 - (1 - a) * (1 - t)
    elif modo == "multiply":
        r = a * t
    else:  # soft light
        r = np.where(t < 0.5, a - (1 - 2 * t) * a * (1 - a), a + (2 * t - 1) * (np.sqrt(a) - a))
    return to_im(a * (1 - opacity) + r * opacity)


def fundo_textura(w, h, nome="couro", tint=None, dark=0.85):
    """fundo de arte a partir da textura do cliente (ex.: couro preto tingido de navy)."""
    tex = cover(load(TEXTURAS[nome]), w, h)
    t = to_np(tex)
    if tint is not None:
        L = t.mean(axis=-1, keepdims=True)
        t = np.clip(L * np.array(tint) * 1.8 + np.array(tint) * 0.35, 0, 1)
    return to_im(t * dark)


def cutout(im):
    """recorte da pessoa por segmentação local (rembg/u2net). Pixels do sujeito são copiados
    tal e qual — nada é redesenhado."""
    from rembg import remove
    return remove(im.convert("RGBA"))


# ----------------------------------------------------------------- tipografia
def text_w(fnt, txt, d=None):
    d = d or ImageDraw.Draw(Image.new("RGB", (10, 10)))
    bb = d.textbbox((0, 0), txt, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def ctext(d, cx, y, txt, fnt, fill):
    w, h = text_w(fnt, txt, d)
    d.text((cx - w // 2, y), txt, font=fnt, fill=fill)
    return h


def glow_text(canvas, xy, txt, fnt, fill=(255, 255, 255), glow=(255, 255, 255), r=18, alpha=150, anchor_center=True):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = text_w(fnt, txt, d)
    x = xy[0] - w // 2 if anchor_center else xy[0]
    d.text((x, xy[1]), txt, font=fnt, fill=glow + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(r))
    canvas.paste(layer, (0, 0), layer)
    ImageDraw.Draw(canvas).text((x, xy[1]), txt, font=fnt, fill=fill)


def justified_spaced(d, lines, x0, x1, y, fnt, fill, gap=1.35):
    """linhas em caixa alta esticadas à largura (tracking variável) — estilo R15."""
    for ln in lines:
        chars = list(ln.replace(" ", "  "))
        widths = [text_w(fnt, c, d)[0] if c != " " else text_w(fnt, "n", d)[0] // 2 for c in chars]
        total = sum(widths)
        extra = (x1 - x0 - total) / max(len(chars) - 1, 1)
        x = x0
        for c, cw in zip(chars, widths):
            if c != " ":
                d.text((x, y), c, font=fnt, fill=fill)
            x += cw + extra
        y += int(text_w(fnt, "A", d)[1] * gap)
    return y


def hand_ellipse(d, box, color=LIME, width=4, seed=1):
    """elipse com traço irregular (caneta)."""
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    pts = []
    for i in range(80):
        t = 2 * math.pi * i / 79
        j = rng.normal(0, 1.8)
        pts.append((cx + (rx + j) * math.cos(t), cy + (ry + j) * math.sin(t)))
    d.line(pts + [pts[0]], fill=color, width=width, joint="curve")


def scribble(d, x0, y0, x1, y1, color=LIME, width=5, seed=2):
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(14):
        t = i / 13
        pts.append((x0 + (x1 - x0) * t + rng.normal(0, 6), y0 + (y1 - y0) * t + rng.normal(0, 10)))
    d.line(pts, fill=color, width=width, joint="curve")


def tag(d, x, y, txt, color, fnt):
    w, h = text_w(fnt, txt, d)
    d.rounded_rectangle([x, y, x + w + 36, y + h + 20], radius=8, fill=color)
    d.text((x + 18, y + 8), txt, font=fnt, fill=(255, 255, 255))
    return w + 36


# ================================================================= ESTILOS
def cards_arredondados(base, cards, out, assinatura="MOCIDADE BETFAGE @2026", fx=0.5, fy=0.4):
    """R01 — foto base full + 4 cards de cantos arredondados rotacionados. LOUVOR."""
    bg = grade(cover(load(base), W, H, fx, fy), "teal")
    bg = halation(bg, 0.7, 0.22, (0.4, 0.9, 1.0))
    canvas = bg.convert("RGBA")
    # cards nos 4 cantos — o centro (rosto da foto base) fica sempre livre
    specs = [((36, 28), 380, 270, -4), ((664, 40), 380, 270, 3), ((36, 1040), 380, 270, -2), ((664, 1030), 380, 270, 5)]
    for (xy, cw, ch, rot), p in zip(specs, cards):
        card = rounded_card(grade(load(p), "teal"), cw, ch, 52, rot)
        shadow_paste(canvas, card, xy, blur=18, alpha=120)
    canvas = canvas.convert("RGB")
    canvas = texture(canvas, "leak", "screen", 0.3, fx=0.3, fy=0.2)
    d = ImageDraw.Draw(canvas)
    ctext(d, W // 2, 1318, assinatura, font("condm", 22), GOLD)
    grain(vinheta(canvas, 0.22), 0.035).save(out, quality=94)


def split_vertical(top, bottom, out, titulo=("talk", "igreja CRIATIVA", "+ igreja do futuro"), laterais=None, estilo="navy"):
    """R02/R17 — duas fotos empilhadas, tipografia editorial mista. FAMÍLIA / IGREJA."""
    ht = int(H * 0.46)
    canvas = Image.new("RGB", (W, H))
    canvas.paste(grade(cover(load(top), W, ht, 0.5, 0.45), estilo), (0, 0))
    canvas.paste(grade(cover(load(bottom), W, H - ht, 0.5, 0.4), estilo), (0, ht))
    d = ImageDraw.Draw(canvas)
    d.text((70, 110), titulo[0], font=font("serifi", 62), fill=(235, 240, 245))
    d.text((70, 185), titulo[1], font=font("condm", 92), fill=(245, 248, 250))
    d.text((70, 290), titulo[2], font=font("serif", 54), fill=(225, 230, 240))
    if laterais:
        for i, t in enumerate(laterais):
            lt = Image.new("RGBA", (400, 40), (0, 0, 0, 0))
            ImageDraw.Draw(lt).text((0, 0), t, font=font("mono", 22), fill=(200, 210, 220, 230))
            lt = lt.rotate(90, expand=True)
            canvas.paste(lt, (24 if i == 0 else W - 64, H - 480), lt)
    grain(canvas, 0.04).save(out, quality=94)


def pb_zoomblur(foto, out, titulo="MARAVILHOSO,\nADMIRÁVEL, TÃO\nSUBLIME, GLORIOSO", versiculo="TUA PRESENÇA É MAIS DESEJÁVEL\nDO QUE O OURO. MELHOR QUE A\nVIDA É O TEU AMOR.", menu=("CONF", "VOCAÇÃO", "MISSÕES"), cx=0.5, cy=0.42, selo="MOCIDADE"):
    """R03 — P&B alto contraste + zoom-blur nas bordas, bloco de texto. LOUVOR banda."""
    im = grade(cover(load(foto), W, H, cx, cy), "pb")
    im = zoom_blur(im, int(cx * W), int(cy * H), 300, 640, 0.22)
    im = grain(im, 0.07)
    d = ImageDraw.Draw(im)
    for i, m in enumerate(menu):
        ctext(d, 200 + i * 340, 60, m, font("condm", 26), (235, 235, 235))
    y = 1040
    for ln in titulo.split("\n"):
        d.text((640, y), ln, font=font("cond", 44), fill=(255, 255, 255))
        y += 46
    for ln in versiculo.split("\n"):
        d.text((640, y + 12), ln, font=font("mono", 17), fill=(220, 220, 220))
        y += 22
    d.ellipse([960, 1230, 1040, 1310], outline=(255, 255, 255), width=3)
    ctext(d, 1000, 1258, selo[:4], font("cond", 24), (255, 255, 255))
    im.save(out, quality=94)


def faixas_inclinadas(fotos, out, palavras=("ESTAMOS", "AQUI", "PARA", "TE RECEBER!"), subs=("como uma família servindo, cuidando", "e compartilhando o amor de Cristo"), marca="MOCIDADE BETFAGE"):
    """R04 — 3 fotos em paralelogramos sobre verde-petróleo texturizado. GRUPO."""
    canvas = fundo_textura(W, H, "couro", tint=(0.16, 0.2, 0.42), dark=0.9)
    canvas = texture(canvas, "leak", "screen", 0.35, fx=0.2, fy=0.1)
    d = ImageDraw.Draw(canvas)
    ctext(d, W // 2, 48, marca, font("condm", 30), LAVENDER)
    skew = 34
    slots = [(150, 300), (520, 330), (900, 300)]
    for (y0, hh), p in zip(slots, fotos):
        cw = W - 180
        pts = [(skew, 0), (cw, 0 + 22), (cw - skew, hh), (0, hh - 22)]
        card = poly_card(grade(load(p), "teal", corr=True), cw, hh, pts, 0.5, 0.45)
        shadow_paste(canvas.convert("RGBA"), card, (90, y0)) if False else None
        canvas.paste(card, (90, y0), card)
    fb = font("cond", 86)
    d = ImageDraw.Draw(canvas)
    d.text((W - 110 - text_w(fb, palavras[0])[0], 95), palavras[0], font=fb, fill=(255, 255, 255))
    d.text((110, 470), palavras[1], font=fb, fill=(255, 255, 255))
    d.text((400, 492), subs[0], font=font("sans", 28), fill=(235, 240, 238))
    d.text((W - 110 - text_w(fb, palavras[2])[0], 870), palavras[2], font=fb, fill=(255, 255, 255))
    d.text((110, 892), subs[1], font=font("sans", 28), fill=(235, 240, 238))
    ctext(d, W // 2, 1225, palavras[3], fb, (255, 255, 255))
    grain(canvas, 0.03).save(out, quality=94)


def selecao_nitida(foto, out, box=(0.28, 0.2, 0.72, 0.72), estilo="sepia", fx=0.5, fy=0.42):
    """R05 — foto desfocada + retângulo nítido com alças de seleção. ORAÇÃO."""
    base = grade(cover(load(foto), W, H, fx, fy), estilo)
    blurred = gauss(base, 22)
    blurred = to_im(to_np(blurred) * 0.82)
    x0, y0, x1, y1 = int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)
    blurred.paste(base.crop((x0, y0, x1, y1)), (x0, y0))
    d = ImageDraw.Draw(blurred)
    d.rectangle([x0, y0, x1, y1], outline=(250, 250, 250), width=2)
    for px, py in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        d.rectangle([px - 6, py - 6, px + 6, py + 6], fill=(250, 250, 250))
    grain(vinheta(blurred, 0.2), 0.04).save(out, quality=94)


def fatias_verticais(fotos, out, larguras=(0.14, 0.24, 0.17, 0.25, 0.20), tints=((0.85, 0.3, 0.25), (0.35, 0.55, 1.0), (1.0, 0.6, 0.3), (0.3, 0.8, 0.9), (1.0, 0.5, 0.2)), gap=8, focos=None):
    """R06 — colunas verticais de fotos diferentes, cada uma com tom próprio. ADORAÇÃO."""
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    x = 0
    focos = focos or [(0.5, 0.4)] * len(fotos)
    for p, lw, tint, (fx, fy) in zip(fotos, larguras, tints, focos):
        cw = int(W * lw) - gap
        im = cover(load(p), cw, H, fx, fy)
        a = corrigir(to_np(im))
        L = a.mean(axis=-1, keepdims=True)
        a = np.clip(a * 0.35 + L * np.array(tint) * 0.85, 0, 1)
        a = np.clip((a - 0.5) * 1.3 + 0.5, 0, 1) * 0.92        # contraste fechado, sem lavar
        a = 0.02 + a * 0.98
        canvas.paste(to_im(a), (x, 0))
        x += cw + gap
    canvas = texture(canvas, "grao", "screen", 0.45)
    canvas = texture(canvas, "rastros", "screen", 0.3, fy=0.8)
    grain(vinheta(canvas, 0.25), 0.045).save(out, quality=94)


def polaroid_papel(fundo, close, out, legenda="MOCIDADE BETFAGE 2026 ©", rot=1.5, fx=0.5, fy=0.42):
    """R07 — fundo quente desfocado + card de papel com o close. ORAÇÃO/MINISTRAÇÃO."""
    bg = grade(cover(load(fundo), W, H, 0.5, 0.45), "sepia")
    bg = to_im(to_np(gauss(bg, 6)) * 0.85)
    cw, ch = 760, 860
    card = paper(cw, ch, (237, 230, 214), seed=4, noise=5).convert("RGBA")
    inner = grade(cover(load(close), cw - 60, ch - 170, fx, fy), "sepia")
    card.paste(inner, (30, 110))
    ImageDraw.Draw(card).text((cw - 30 - text_w(font("mono", 20), legenda)[0], 44), legenda, font=font("mono", 20), fill=(90, 80, 70))
    card = card.rotate(rot, expand=True, resample=Image.BICUBIC)
    canvas = bg.convert("RGBA")
    shadow_paste(canvas, card, ((W - card.width) // 2, (H - card.height) // 2 + 20), blur=26, alpha=140)
    grain(canvas.convert("RGB"), 0.04).save(out, quality=94)


def countdown_numero(foto_pessoa, out, numero="02", script="dias para o grande dia", nome="Pr. Nome Sobrenome", data="08 - NOV", tags=TAGS, fundo=None):
    """R08 — número gigante serif + pessoa recortada em P&B + fundo noturno. PREGAÇÃO/CONTAGEM."""
    canvas = Image.new("RGB", (W, H), NAVY)
    if fundo:
        f = grade(cover(load(fundo), W, H), "navy")
        f = to_im(to_np(gauss(f, 28)) * 0.5)
        canvas.paste(f, (0, 0))
    ht = halftone(W, H, 16, LAVENDER, 55, fade=(0.1, 0.9))
    canvas.paste(ht, (0, 0), ht)
    d = ImageDraw.Draw(canvas)
    fn = font("serif", 520)
    d.text((70, 20), numero, font=fn, fill=LAVENDER)
    pessoa = cutout(load(foto_pessoa))
    s = 1050 / pessoa.height
    pessoa = pessoa.resize((int(pessoa.width * s), 1050), Image.LANCZOS)
    rgb = to_im(pb(to_np(pessoa.convert("RGB")), 1.3)).convert("RGBA")
    rgb.putalpha(pessoa.split()[3])
    canvas_rgba = canvas.convert("RGBA")
    shadow_paste(canvas_rgba, rgb, (W - rgb.width - 40, 150), blur=30, alpha=160, off=(0, 20))
    canvas = canvas_rgba.convert("RGB")
    glow_text(canvas, (250, 760), script, font("script", 80), GOLD, GOLD, 16, 150)
    d = ImageDraw.Draw(canvas)
    ctext(d, W // 2, 1110, nome, font("serif", 54), OFFWHITE)
    x = 80
    ft = font("cond", 26)
    for t, c in tags:
        x += tag(d, x, 1190, t, c, ft) + 22
    ctext(d, W // 2, 1265, "-  " + data + "  -", font("serif", 40), (235, 235, 235))
    grain(canvas, 0.035).save(out, quality=94)


def leque_plateia(panoramica, cards, out, frase="QUE A BÊNÇÃO\nTE PERSIGA", logo="M B", fy=0.4):
    """R09 — panorâmica da igreja + leque de cards curvados + rodapé preto. IGREJA/LOUVOR."""
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    top = grade(cover(load(panoramica), W, 760, 0.5, fy), "teal")
    a = to_np(top)
    mean = a.mean(axis=-1, keepdims=True)
    a = mean + (a - mean) * 0.6
    yy = np.linspace(0, 1, 760)[:, None, None]
    a = a * (1 - np.clip((yy - 0.6) / 0.4, 0, 1) * 0.95)
    canvas.paste(to_im(a), (0, 0))
    canvas = canvas.convert("RGBA")
    # leque: cards grandes abrindo a partir de um pivô baixo; os de fora primeiro, o central por cima
    order = [(-22, 0), (22, 3), (-8, 1), (8, 2)]
    for ang, idx in order:
        p = cards[idx]
        card = rounded_card(grade(load(p), "teal"), 400, 540, 20, 0, 0.5, 0.38, border=8, border_color=OFFWHITE)
        card = card.rotate(ang, expand=True, resample=Image.BICUBIC)
        x = int(W / 2 - card.width / 2 + math.sin(math.radians(ang)) * 640)
        y = int(470 + abs(ang) * 2.2)
        shadow_paste(canvas, card, (x, y), blur=22, alpha=160)
    canvas = canvas.convert("RGB")
    canvas = texture(canvas, "rastros", "screen", 0.35, fy=0.3)
    canvas = texture(canvas, "grao", "screen", 0.3)
    d = ImageDraw.Draw(canvas)
    for i, ch in enumerate(logo.split()):
        cx = W // 2 + (i - (len(logo.split()) - 1) / 2) * 70
        d.ellipse([cx - 28, 1090, cx + 28, 1146], outline=(255, 255, 255), width=2)
        ctext(d, int(cx), 1104, ch, font("cond", 26), (255, 255, 255))
    y = 1175
    for ln in frase.split("\n"):
        y += ctext(d, W // 2, y, ln, font("cond", 34), (255, 255, 255)) + 6
    grain(canvas, 0.035).save(out, quality=94)


def paineis_pb_recorte(paineis, heroi, out, topo="REVESTIDOS DE AUTORIDADE", script="Parabéns", nome="NOME", sobrenome="SOBRENOME", data="08 - NOV", texto=("Que o Senhor continue", "te fortalecendo e", "renovando a tua unção."), tags=TAGS):
    """R10 — 3 painéis P&B + recorte colorido na frente, fundo claro. HOMENAGEM/PREGAÇÃO."""
    canvas = paper(W, H, (238, 238, 240), seed=9, noise=3)
    d = ImageDraw.Draw(canvas)
    ctext(d, W // 2, 60, "  ".join(topo), font("condm", 26), (40, 40, 48))
    pw, ph = 300, 560
    for i, p in enumerate(paineis):
        im = grade(cover(load(p), pw, ph, 0.5, 0.35), "pb")
        canvas.paste(im, (60 + i * (pw + 30), 130))
    pessoa = cutout(load(heroi))
    s = 760 / pessoa.height
    pessoa = pessoa.resize((int(pessoa.width * s), 760), Image.LANCZOS)
    canvas_rgba = canvas.convert("RGBA")
    shadow_paste(canvas_rgba, pessoa, (380, 420), blur=26, alpha=120, off=(6, 26))
    canvas = canvas_rgba.convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.text((70, 830), script, font=font("script", 70), fill=GOLD)
    d.text((70, 930), "  ".join(nome), font=font("condm", 30), fill=(30, 30, 36))
    # nome bold com preenchimento iridescente
    fb = font("cond", 110)
    tw, th = text_w(fb, sobrenome, d)
    gradient = Image.new("RGB", (tw + 20, th + 40))
    ga = np.zeros((th + 40, tw + 20, 3), np.float32)
    xs = np.linspace(0, 1, tw + 20)[None, :, None]
    ga = (np.array([0.08, 0.11, 0.25]) * (1 - xs) + np.array([0.85, 0.65, 0.34]) * xs) * (1 - 0.15 * np.linspace(0, 1, th + 40)[:, None, None])
    gradient = to_im(ga)
    mask = Image.new("L", gradient.size, 0)
    ImageDraw.Draw(mask).text((10, 0), sobrenome, font=fb, fill=255)
    canvas.paste(gradient, (60, 960), mask)
    d.rectangle([70, 1100, 300, 1150], fill=NAVY)
    ctext(d, 185, 1110, data, font("cond", 30), (255, 255, 255))
    y = 850
    for ln in texto:
        d.text((720, y), ln, font=font("sans", 22), fill=(60, 60, 70))
        y += 30
    x = 70
    for t, c in tags:
        x += tag(d, x, 1185, t, c, font("cond", 22)) + 14
    grain(canvas, 0.025).save(out, quality=94)


def frames_neon(foto, out, frame_rosto=(0.28, 0.14, 0.72, 0.48), frame_maos=(0.1, 0.56, 0.6, 0.82), titulo="JESUS É O", script="Foco", cor=LIME, fx=0.5, fy=0.42):
    """R11 — P&B suave + dois frames neon com área clareada. ORAÇÃO (jovem)."""
    base = cover(load(foto), W, H, fx, fy)
    a = pb(corrigir(to_np(base)), 1.05)
    a = 0.06 + a * 0.9
    im = grain(to_im(a), 0.05)
    d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1) in (frame_rosto, frame_maos):
        X0, Y0, X1, Y1 = int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)
        reg = to_np(im.crop((X0, Y0, X1, Y1)))
        reg = np.clip(reg * 1.15 + 0.05, 0, 1) * np.array([1.04, 1.0, 0.94])   # só brilho/tint da ÁREA
        im.paste(to_im(reg), (X0, Y0))
        d = ImageDraw.Draw(im)
        d.rectangle([X0, Y0, X1, Y1], outline=cor, width=3)
    fx0 = int(frame_maos[2] * W) + 30
    d.text((fx0, int(frame_maos[1] * H) + 40), titulo, font=font("cond", 46), fill=cor)
    d.text((fx0, int(frame_maos[1] * H) + 92), script, font=font("script", 70), fill=cor)
    im.save(out, quality=94)


def fit_font(kind, txt, max_w, start=190, min_size=60):
    """maior tamanho de fonte em que `txt` cabe em max_w px."""
    size = start
    while size > min_size and text_w(font(kind, size), txt)[0] > max_w:
        size -= 6
    return font(kind, size), size


def radial_blur_titulo(foto, out, titulo=("HOJE TEM", "CULTO"), info=("AV. EXEMPLO, 123", "BAIRRO, CIDADE", "ÀS 19:30"), logos=("mocidade", "betfage"), cx=0.5, cy=0.55, r_in=260, r_out=600, estilo="sepia"):
    """R12 — sépia + zoom-blur radial nas bordas (rostos dentro de r_in ficam nítidos) + título
    gigante com glow/grunge + caixa de info. RODA/CONJUNTO."""
    im = grade(cover(load(foto), W, H, cx, cy), estilo)
    im = zoom_blur(im, int(cx * W), int(cy * H), r_in, r_out, 0.3, 16)
    a = to_np(im)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dd = np.hypot((xx - cx * W) / (W / 2), (yy - cy * H) / (H / 2))
    a = np.clip(a + smoothstep(dd, 0.7, 1.4)[..., None] * 0.18, 0, 1)   # vinheta clara suave
    im = grain(to_im(a), 0.04)
    im = texture(im, "circulo", "screen", 0.45, fy=0.4)
    im = texture(im, "leak", "screen", 0.3, fx=0.8, fy=0.1)
    y = 60
    for i, ln in enumerate(titulo):
        fb, size = fit_font("cond", ln, W - 90, 190)
        glow_text(im, (W // 2, y), ln, fb, OFFWHITE, OFFWHITE, 22, 140)
        grunge_text(im, (W // 2, y), ln, fb, OFFWHITE, seed=7 + i, density=0.16)
        y += int(size * 1.02)
    d = ImageDraw.Draw(im)
    bx, by = 160, 1020
    d.rectangle([bx, by, bx + 560, by + 120], fill=GOLD)
    for i, ln in enumerate(info):
        d.text((bx + 22, by + 14 + i * 32), ln, font=font("condm", 26), fill=NAVY)
    d.rectangle([bx + 580, by, bx + 700, by + 120], fill=GOLD)
    d.text((bx + 612, by + 30), "✦", font=font("sans", 48), fill=NAVY)
    d.text((120, 1230), logos[0], font=font("condm", 40), fill=(255, 255, 255))
    d.text((W - 120 - text_w(font("condm", 40), logos[1])[0], 1230), logos[1], font=font("condm", 40), fill=(255, 255, 255))
    im.save(out, quality=94)


def foto_editorial(foto, out, fx=0.5, fy=0.4):
    """R13 — foto pura teal & orange com halation e grão. LOUVOR congregação."""
    im = grade(cover(load(foto), W, H, fx, fy), "teal")
    im = halation(im, 0.72, 0.25)
    grain(vinheta(im, 0.25), 0.04).save(out, quality=94)


def tripla_cinematica(silhueta, close, baixo, out, versiculo=("Portanto ide e fazei discípulos", "de todas as nações — Mt 28:19"), logo="MOCIDADE BETFAGE"):
    """R14 — 3 fotos fundidas por gradientes, mesma grade azul + luzes âmbar. LOUVOR+PREGAÇÃO."""
    canvas = grade(cover(load(baixo), W, H, 0.5, 0.55), "navy")
    a = to_np(canvas)
    # close grande à direita, fundido por gradiente
    cl = to_np(grade(cover(load(close), 700, 820, 0.5, 0.35), "navy"))
    m = np.ones((820, 700), np.float32)
    xs = np.linspace(0, 1, 700)[None, :]
    ys = np.linspace(0, 1, 820)[:, None]
    m = smoothstep(xs, 0.0, 0.35) * (1 - smoothstep(ys, 0.75, 1.0))
    a[80:900, 380:1080] = a[80:900, 380:1080] * (1 - m[..., None]) + cl * m[..., None]
    # silhueta no topo-esquerdo
    si = to_np(grade(cover(load(silhueta), 520, 520, 0.5, 0.4), "navy"))
    m2 = (1 - smoothstep(np.linspace(0, 1, 520)[None, :], 0.6, 1.0)) * (1 - smoothstep(np.linspace(0, 1, 520)[:, None], 0.7, 1.0))
    a[40:560, 0:520] = a[40:560, 0:520] * (1 - m2[..., None]) + si * m2[..., None]
    im = halation(to_im(a), 0.7, 0.22)
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(versiculo):
        d.text((60, 640 + i * 20), ln, font=font("mono", 15), fill=(220, 225, 235))
    d.text((W - 60 - text_w(font("condm", 22), logo)[0], 660), logo, font=font("condm", 22), fill=(230, 235, 240))
    grain(vinheta(im, 0.2), 0.04).save(out, quality=94)


def spin_blur_frase(foto, out, linhas=("A MAIOR", "CRIATIVIDADE DE", "UM CRISTÃO É", "EDIFICAR", "A IGREJA COM SEUS", "DONS."), circulada=(1, "CRIATIVIDADE"), cx=0.45, cy=0.42):
    """R15 — P&B + spin-blur nas bordas + frase espaçada justificada + palavra circulada. FRASE."""
    im = grade(cover(load(foto), W, H, cx, cy), "pb")
    im = spin_blur(im, int(cx * W), int(cy * H), 220, 560, 9, 16)
    im = grain(im, 0.06)
    d = ImageDraw.Draw(im)
    fnt = font("condm", 40)
    y0, x0, x1 = 300, 120, W - 120
    y = y0
    line_h = int(text_w(fnt, "A", d)[1] * 1.35)
    justified_spaced(d, linhas, x0, x1, y0, fnt, (245, 245, 245))
    li, palavra = circulada
    ln = linhas[li]
    # posição aproximada da palavra na linha justificada
    frac0 = ln.find(palavra) / max(len(ln), 1)
    frac1 = (ln.find(palavra) + len(palavra)) / max(len(ln), 1)
    yy = y0 + li * line_h
    hand_ellipse(d, (x0 + frac0 * (x1 - x0) - 30, yy - 14, x0 + frac1 * (x1 - x0) + 30, yy + 54), LIME, 4)
    scribble(d, W - 260, 30, W - 60, 60, LIME, 5, 2)
    scribble(d, 40, H - 70, 260, H - 40, LIME, 5, 7)
    im.save(out, quality=94)


def bandas_horizontais(fotos, out, textos=(None, "sua presença", None, "faz diferença!", "SEXTA 19H30\nSÁBADO 19H"), tints=((0.7, 0.95, 0.4), (0.4, 0.6, 1.0), None, (0.9, 0.5, 0.4), (0.5, 0.65, 0.9)), marca="MOCIDADE BETFAGE", blur_bands=(1, 3)):
    """R16 — 5 bandas horizontais, cada uma com tom próprio, textos nos vazios. PROGRAMAÇÃO."""
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    bh = (H - 4 * 6) // 5
    for i, (p, tint) in enumerate(zip(fotos, tints)):
        im = cover(load(p), W, bh, 0.5, 0.4)
        a = corrigir(to_np(im))
        if tint:
            L = a.mean(axis=-1, keepdims=True)
            a = np.clip(a * 0.55 + L * np.array(tint) * 0.7, 0, 1)
        else:
            a = teal_orange(a)
        im = to_im(a)
        if i in blur_bands:
            m = np.zeros((bh, W), np.float32)
            m[:, : W // 2] = 1
            m = to_np(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(60))) if False else blur_np(np.stack([m] * 3, -1), 60)[..., 0]
            im = to_im(to_np(im) * (1 - m[..., None]) + to_np(motion_blur_h(im, 60)) * m[..., None])
        canvas.paste(im, (0, i * (bh + 6)))
    d = ImageDraw.Draw(canvas)
    d.text((40, 24), "✦ " + marca, font=font("condm", 26), fill=(255, 255, 255))
    for i, t in enumerate(textos):
        if not t:
            continue
        y = i * (bh + 6) + bh // 2 - 20
        if "\n" in t:
            for j, ln in enumerate(t.split("\n")):
                d.text((60, y - 20 + j * 36), ln, font=font("cond", 34), fill=(255, 255, 255))
        elif i % 2 == 1 and i < 3:
            d.text((60, y), t, font=font("sans", 44), fill=(255, 255, 255))
        else:
            d.text((W - 60 - text_w(font("sans", 44), t)[0], y), t, font=font("sans", 44), fill=(255, 255, 255))
    grain(canvas, 0.035).save(out, quality=94)


def mosaico_paralelogramos(fotos, out, gap=14, focos=None):
    """R19 — 4 fotos em cortes diagonais sobre papel branco. FAMÍLIA/JOVENS."""
    canvas = paper(W, H, (246, 243, 238), seed=12, noise=3)
    m = 70
    focos = focos or [(0.5, 0.4)] * 4
    # geometria: 2 em cima (corte diagonal), 1 grande no meio, 1 embaixo
    cells = [
        [(m, m), (W // 2 + 40, m), (W // 2 - 60, 430), (m, 430)],
        [(W // 2 + 40 + gap, m), (W - m, m), (W - m, 430), (W // 2 - 60 + gap, 430)],
        [(m, 430 + gap), (W - m, 430 + gap), (W - m, 880), (m, 880 + 60)],
        [(m, 880 + 60 + gap), (W - m, 880 + gap), (W - m, H - m), (m, H - m)],
    ]
    for pts, p, (fx, fy) in zip(cells, fotos, focos):
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        local = [(q[0] - x0, q[1] - y0) for q in pts]
        card = poly_card(grade(load(p), "teal", corr=True), x1 - x0, y1 - y0, local, fx, fy)
        canvas.paste(card, (x0, y0), card)
    grain(canvas, 0.02).save(out, quality=94)


STYLES = {
    "R01": cards_arredondados, "R02": split_vertical, "R03": pb_zoomblur, "R04": faixas_inclinadas,
    "R05": selecao_nitida, "R06": fatias_verticais, "R07": polaroid_papel, "R08": countdown_numero,
    "R09": leque_plateia, "R10": paineis_pb_recorte, "R11": frames_neon, "R12": radial_blur_titulo,
    "R13": foto_editorial, "R14": tripla_cinematica, "R15": spin_blur_frase, "R16": bandas_horizontais,
    "R17": split_vertical, "R19": mosaico_paralelogramos,
}
