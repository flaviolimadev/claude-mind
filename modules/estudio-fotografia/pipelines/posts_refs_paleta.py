#!/usr/bin/env python3
"""7 posts replicando as referências N1–N7 (28/10 à noite) com as fotos da entrega
(ENTREGA/01_fotos-editadas, pixels originais) — v2 após feedback:
  • ENQUADRAMENTO PELO ROSTO: caixas do Vision (hf/faces.json) → rosto principal / união dos rostos
    posicionados no recorte (nunca mais centro de máscara).
  • PALETA DO ANIVERSÁRIO em tudo que é fundo/acento: navy #141C3F · índigo #3A4A8A · lavanda
    #8A94C8 · off-white #E8E9F4 · dourado #D9A557 (sem verde-limão, laranja ou petróleo).
  • Fotos: grade "navy & gold" sutil (sombras navy, luzes douradas, pele natural) ou P&B.
  • Textura do tema: se existir referencias/tema_logo.(png|jpg) entra esmaecida nos fundos navy.
Grade/efeito só dentro do post; pessoas por recorte local (rembg); sem texto (TEXTOS=False).
Canvas 4:5 em 2160×2700. Saída: ENTREGA/02_posts/N?_*.jpg
uso: python3 betfage_posts_refs2.py [N1 N2 ...]"""
import json
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import betfage_estilos as E  # noqa: E402

ROOT = os.path.expanduser("<PROJETO>")
SRC = os.path.join(ROOT, "ENTREGA", "01_fotos-editadas")
OUT = os.path.join(ROOT, "ENTREGA", "02_posts")
os.makedirs(OUT, exist_ok=True)
W, H = 2160, 2700
TEXTOS = False
RNG = np.random.default_rng(3)
FACES = json.load(open(os.path.join(ROOT, "hf", "faces.json")))

# paleta OFICIAL (camisas/revestidos-de-autoridade.html + arte-final.html)
NAVY = np.array([0x1B, 0x23, 0x40], np.float32) / 255      # fundo principal
DEEP = np.array([0x0F, 0x13, 0x26], np.float32) / 255      # navy profundo
INDIGO = np.array([0x2B, 0x34, 0x56], np.float32) / 255    # brilho dos fundos
LAV = np.array([0x8E, 0x9B, 0xCF], np.float32) / 255       # lavanda
OFF = np.array([0xEF, 0xE7, 0xD4], np.float32) / 255       # creme/off-white
GOLD = np.array([0xD9, 0xAE, 0x6A], np.float32) / 255      # dourado
GOLD8 = (0xD9, 0xAE, 0x6A)
LAV8 = (0x8E, 0x9B, 0xCF)
OFF8 = (0xEF, 0xE7, 0xD4)


# ------------------------------------------------------------------ fotos + rostos
def foto(n):
    return Image.open(os.path.join(SRC, f"IMG_{n}.jpg")).convert("RGB")


from betfage_rostos import rostos, alvo as _alvo_rosto  # noqa: E402


def alvo(n, modo="principal"):
    """(fx, fy) do alvo: rosto principal / união dos rostos; fallback na máscara rembg."""
    a = _alvo_rosto(n, modo)
    if a is not None:
        return a
    im = foto(n)
    return E.foco(E.mascara(n, im.size))


def recorte(n, w, h, modo="principal", y_rosto=0.36, x_rosto=0.5, zoom=1.0):
    """recorte w×h da foto com o rosto-alvo posicionado em (x_rosto, y_rosto) do recorte."""
    im = foto(n)
    fx, fy = alvo(n, modo)
    k = max(w / im.width, h / im.height) * zoom
    im2 = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    x0 = int(np.clip(fx * im2.width - x_rosto * w, 0, im2.width - w))
    y0 = int(np.clip(fy * im2.height - y_rosto * h, 0, im2.height - h))
    return im2.crop((x0, y0, x0 + w, y0 + h))


def cutout(n):
    im = foto(n)
    m = Image.open(os.path.join(ROOT, "hf", f"{n}_mask.png")).convert("L").resize(im.size, Image.LANCZOS)
    im.putalpha(m.filter(ImageFilter.GaussianBlur(1.2)))
    return im


# ------------------------------------------------------------------ grades (paleta do aniversário)
def grade_navy_gold(a, mix=0.65, contraste=0.12):
    """sombras navy, meios marrom-dourado, luzes creme-dourado; `mix` = quanto da cor original fica."""
    l = E.scurve(E.lum(a), contraste)
    stops = np.array([0.0, 0.32, 0.68, 1.0])
    cores = np.array([[18, 26, 60], [112, 80, 52], [214, 166, 92], [244, 232, 206]], np.float32) / 255
    mono = np.stack([np.interp(l, stops, cores[:, c]) for c in range(3)], axis=-1).astype(np.float32)
    out = mono * (1 - mix) + E.scurve(a, contraste) * mix
    return E.grain(np.clip(out, 0, 1), 0.03)


def grade_natural_dourado(a):
    """quase natural: contraste leve, luzes puxadas pro dourado, sombras um fio de navy."""
    a = E.scurve(a, 0.10)
    l = E.lum(a)[..., None]
    a = a + l * np.array([0.03, 0.012, -0.03], np.float32) + (1 - l) * np.array([-0.012, -0.006, 0.02], np.float32)
    return E.grain(np.clip(a, 0, 1), 0.028)


def grade_pb(a):
    l = E.scurve(E.lum(a), 0.22)
    l = np.clip((l - 0.03) / 0.97, 0, 1) ** 1.05
    return E.grain(np.repeat(l[..., None], 3, axis=-1), 0.05)


# ------------------------------------------------------------------ fundos (paleta) + textura do tema
def halftone(w, h, passo=16, raio=4.2):
    y, x = np.mgrid[0:h, 0:w]
    dx = (x % passo) - passo / 2
    dy = (y % passo) - passo / 2
    d = np.sqrt(dx * dx + dy * dy)
    return np.clip(raio + 0.8 - d, 0, 1).astype(np.float32)


TEMA = os.path.join(ROOT, "camisas")
ARTE = os.path.join(TEMA, "artes", "revestidos-de-autoridade-oficial.png")       # arte completa (fundo navy)
LEAO = os.path.join(TEMA, "photoshop", "camadas", "3-leao.png")                     # leão gravura (alpha)
LEAO_CONTORNO = os.path.join(TEMA, "photoshop", "contornos-azuis", "3-leao-contorno.png")
MANTO = os.path.join(TEMA, "photoshop", "camadas", "1-manto.png")


def _encaixe(im, w, h, escala, pos):
    k = max(w / im.width, h / im.height) * escala
    im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(im, (int(w * pos[0] - im.width / 2), int(h * pos[1] - im.height / 2)))
    return canvas


def aplicar_tema(bg, forca=0.22, escala=1.08, pos=(0.5, 0.42)):
    """arte oficial completa (leão + tipografia + manto) como TEXTURA esmaecida em screen."""
    h, w = bg.shape[:2]
    arte = _encaixe(Image.open(ARTE).convert("RGBA"), w, h, escala, pos)
    a = E.to_f(arte.convert("RGB"))
    a = np.clip((a - NAVY * 0.9), 0, 1)          # tira o fundo navy da arte → sobra só o desenho
    return E.screen(bg, a, forca)


def aplicar_leao(bg, forca=0.3, escala=0.9, pos=(0.72, 0.3), cor=None, camada=None):
    """leão (camada com alpha) tingido na paleta, como marca-d'água."""
    h, w = bg.shape[:2]
    im = Image.open(camada or LEAO).convert("RGBA")
    im = im.crop(im.getbbox())
    k = (w * escala) / im.width
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(im, (int(w * pos[0] - im.width / 2), int(h * pos[1] - im.height / 2)))
    alpha = np.asarray(canvas.split()[3], np.float32) / 255
    lum = E.lum(E.to_f(canvas.convert("RGB")))
    cor = LAV if cor is None else cor
    camada_rgb = (lum * 0.6 + 0.4)[..., None] * cor
    return np.clip(bg + camada_rgb * (alpha * forca)[..., None], 0, 1)


def fundo_navy(w, h, glow=(0.15, 0.1), forca=0.8, tema="arte"):
    y, x = np.mgrid[0:h, 0:w]
    t = np.clip(1 - np.sqrt(((x / w - glow[0]) * 1.1) ** 2 + ((y / h - glow[1]) * 1.3) ** 2) / 0.95, 0, 1).astype(np.float32)
    bg = DEEP + (INDIGO - DEEP) * (t ** 2.2)[..., None] * forca
    bg = np.clip(bg + halftone(w, h)[..., None] * LAV * 0.08, 0, 1)
    if tema == "arte":
        bg = aplicar_tema(bg)
    elif tema == "leao":
        bg = aplicar_leao(bg)
    return E.grain(bg, 0.025)


def fundo_offwhite(w, h):
    bg = np.full((h, w, 3), OFF, np.float32)
    bg = np.clip(bg + RNG.normal(0, 0.012, (h, w)).astype(np.float32)[..., None], 0, 1)
    # leão em contorno, bem esmaecido em lavanda (aparece nas frestas e margens)
    im = Image.open(LEAO_CONTORNO).convert("RGBA")
    im = im.crop(im.getbbox())
    k = (w * 1.1) / im.width
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(im, (int(w * 0.55 - im.width / 2), int(h * 0.5 - im.height / 2)))
    alpha = np.asarray(canvas.split()[3], np.float32) / 255
    return np.clip(bg - (OFF - LAV) * (alpha * 0.22)[..., None], 0, 1)


def mascara_arredondada(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    return m


def colar(canvas, im, pos, mask=None, sombra=0.0):
    x, y = pos
    if sombra > 0:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if mask is not None:
            sh.paste((0, 0, 0, int(255 * sombra)), (0, 0), mask)
        else:
            sh.paste((0, 0, 0, int(255 * sombra)), (0, 0, im.width, im.height))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)), (x + 18, y + 26))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    im = im.convert("RGBA")
    if mask is not None:
        im.putalpha(mask)
    layer.paste(im, (x, y))
    canvas.alpha_composite(layer)


def card_girado(canvas, a, pos, ang, raio=60, sombra=0.5):
    im = E.from_f(a).convert("RGBA")
    im.putalpha(mascara_arredondada(im.width, im.height, raio))
    rot = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", rot.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, int(255 * sombra)), (0, 0), rot.split()[3])
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)), (pos[0] + 14, pos[1] + 22))
    canvas.alpha_composite(rot, pos)


def rabisco(draw, x, y, w, h, cor=GOLD8 + (235,)):
    pts = []
    for i in range(60):
        t = i / 59
        px = x + t * w + RNG.normal(0, 6)
        py = y + h / 2 + math.sin(t * 9.5) * h / 2 * (0.4 + 0.6 * abs(math.sin(t * 3))) + RNG.normal(0, 5)
        pts.append((px, py))
    draw.line(pts, fill=cor, width=6, joint="curve")
    draw.line([(x + w * 0.1, y + h * 0.95), (x + w * 0.95, y + h * 0.75)], fill=cor, width=5)


def wireframe(draw, cx, cy, r, alt, cor=LAV8 + (70,)):
    hexa = [(cx + r * math.cos(math.radians(60 * i)), cy + r * 0.38 * math.sin(math.radians(60 * i))) for i in range(6)]
    draw.polygon(hexa, outline=cor, width=2)
    for px, py in hexa:
        draw.line([(px, py), (px, py + alt)], fill=cor, width=2)
    draw.polygon([(px, py + alt) for px, py in hexa], outline=cor, width=2)


def icone_globo(draw, cx, cy, r, cor=GOLD8 + (230,)):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=cor, width=3)
    draw.ellipse((cx - r * 0.45, cy - r, cx + r * 0.45, cy + r), outline=cor, width=2)
    draw.line((cx - r, cy, cx + r, cy), fill=cor, width=2)


def pontos_logo(draw, cx, cy, r=22, R=52, cor=GOLD8 + (255,)):
    for i in range(6):
        px, py = cx + R * math.cos(math.radians(60 * i + 30)), cy + R * math.sin(math.radians(60 * i + 30))
        draw.ellipse((px - r, py - r, px + r, py + r), fill=cor)


def zoom_blur(a, cx, cy, forca=0.14, n=16):
    im = E.from_f(a)
    acc = np.zeros_like(a)
    for i in range(n):
        s = 1 + forca * i / (n - 1)
        w2, h2 = int(W * s) + 1, int(H * s) + 1
        im2 = im.resize((w2, h2), Image.BILINEAR)
        x0, y0 = int(cx * w2 - cx * W), int(cy * h2 - cy * H)
        acc += E.to_f(im2.crop((x0, y0, x0 + W, y0 + H)))
    return acc / n


def mascara_eliptica(w, h, cx, cy, rx, ry, pena):
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    return np.clip((1.0 - d) / (pena / max(rx, ry)) + 1, 0, 1).astype(np.float32)


# ------------------------------------------------------------------ POSTS
def N1_cards_quente(out):
    """ref 1 — cards arredondados inclinados; grade navy & gold forte, poeira dourada."""
    base = E.to_f(recorte("0069", W, H, "todos", 0.45))
    bg = grade_navy_gold(E.blur(base, 40), 0.1) * 0.38
    bg = E.vinheta(bg, 0.5)
    bg = aplicar_tema(bg, forca=0.2)
    canvas = E.from_f(bg).convert("RGBA")
    ang = -7
    cards = [  # (foto, w, h, x, y, modo, y_rosto)
        ("0317", 700, 1300, -230, -60, "todos", 0.45),
        ("0117", 980, 760, 1300, -150, "todos", 0.45),
        ("0571", 760, 1080, 1520, 700, "principal", 0.36),
        ("0037", 640, 980, -120, 1640, "principal", 0.36),
        ("0535", 1040, 1460, 330, -40, "principal", 0.36),
        ("0605", 1280, 1500, 470, 1270, "principal", 0.36),
    ]
    for n, w, h, x, y, modo, yr in cards:
        a = grade_navy_gold(E.to_f(recorte(n, w, h, modo, yr)), 0.38, 0.2)
        card_girado(canvas, a, (x, y), ang)
    a = E.to_f(canvas.convert("RGB"))
    poeira = E.camada_fx("fx4_poeira.png", (W, H), escala=1.05) * GOLD / GOLD.max()
    a = E.screen(a, poeira, 0.35)
    a = E.grain(E.vinheta(a, 0.25), 0.02)
    E.from_f(a).save(out, "JPEG", quality=92, subsampling=0)


def N2_grade6_papel(out):
    """ref 2 — grade 3 colunas em off-white lavanda, fotos natural-dourado."""
    mg, gap = 64, 26
    cw = (W - 2 * mg - 2 * gap) // 3
    ch = H - 2 * mg
    canvas = E.from_f(fundo_offwhite(W, H)).convert("RGBA")
    h_meio = (ch - gap) // 2
    h_a, h_b = int(ch * 0.6) - gap // 2, ch - int(ch * 0.6) - gap // 2
    cel = [  # (foto, x, y, w, h)
        ("0046", mg, mg, cw, h_meio),
        ("0304", mg, mg + h_meio + gap, cw, ch - h_meio - gap),
        ("0574", mg + cw + gap, mg, cw, h_a),
        ("0519", mg + cw + gap, mg + h_a + gap, cw, h_b),
        ("0535", mg + 2 * (cw + gap), mg, cw, h_b),
        ("0335", mg + 2 * (cw + gap), mg + h_b + gap, cw, h_a),
    ]
    for n, x, y, w, h in cel:
        a = grade_navy_gold(E.to_f(recorte(n, w, h, "principal", 0.36)), 0.72)
        colar(canvas, E.from_f(a), (x, y))
    canvas.convert("RGB").save(out, "JPEG", quality=92, subsampling=0)


def N3_fatias_lime(out):
    """ref 3 — três fatias verticais de perfis sobre navy com brilho índigo e meio-tom lavanda."""
    canvas = E.from_f(fundo_navy(W, H, glow=(0.1, 0.05))).convert("RGBA")
    co = cutout("0153")
    co = co.crop(co.getbbox())
    co = co.resize((int(co.width * 0.55), int(co.height * 0.55)), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
    a = np.clip(grade_pb(E.to_f(co.convert("RGB"))) * 0.7 + 0.1, 0, 1)
    a = a * (NAVY * 0.6 + 0.6)                      # cinza puxado pro navy
    pb = E.from_f(a).convert("RGBA")
    pb.putalpha(co.split()[3])
    canvas.alpha_composite(pb, (W - int(pb.width * 0.5), H - int(pb.height * 0.42)))
    fw, gap, fh = 570, 30, 2140
    x0 = (W - 3 * fw - 2 * gap) // 2
    y0 = 330
    for i, n in enumerate(["0153", "0535", "0019"]):
        a = grade_natural_dourado(E.to_f(recorte(n, fw, fh, "principal", 0.26)))
        colar(canvas, E.from_f(a), (x0 + i * (fw + gap), y0), sombra=0.4)
    d = ImageDraw.Draw(canvas)
    icone_globo(d, 470, 180, 36)
    d.line((530, 180, 1240, 180), fill=GOLD8 + (150,), width=2)
    d.ellipse((1290, 160, 1480, 200), outline=GOLD8 + (220,), width=3)
    rabisco(d, 1560, 2300, 420, 200)
    canvas.convert("RGB").save(out, "JPEG", quality=92, subsampling=0)


def N4_semicirculo_cutout(out):
    """ref 4 — cúpula com mãos erguidas, bloco inferior, pessoa recortada por cima (fundo navy)."""
    canvas = E.from_f(fundo_navy(W, H, glow=(0.12, 0.06), forca=0.9, tema="leao")).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    wireframe(d, 1180, 520, 760, 620)
    pontos_logo(d, 130, 250)
    cw, ch = 1900, 1000
    cx0, cy0 = (W - cw) // 2, 540
    a = grade_natural_dourado(E.to_f(recorte("0285", cw, ch, "todos", 0.52)))
    m = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(m).pieslice((0, 0, cw, 2 * ch), 180, 360, fill=255)
    colar(canvas, E.from_f(a), (cx0, cy0), mask=m, sombra=0.45)
    bw, bh = 1700, 920
    bx0, by0 = (W - bw) // 2 - 60, cy0 + ch + 10
    a = grade_natural_dourado(E.to_f(recorte("0276", bw, bh, "todos", 0.45)))
    a = E.blur(a, 3) * 0.8
    m = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=420, fill=255, corners=(False, False, True, False))
    colar(canvas, E.from_f(a), (bx0, by0), mask=m, sombra=0.35)
    co = cutout("0519")
    co = co.crop((0, 0, int(co.width * 0.56), co.height))
    co = co.crop(co.getbbox())
    k = 1250 / co.height
    co = co.resize((int(co.width * k), 1250), Image.LANCZOS)
    a = grade_natural_dourado(E.to_f(co.convert("RGB")))
    pc = E.from_f(a).convert("RGBA")
    pc.putalpha(co.split()[3])
    sh = Image.new("RGBA", pc.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (0, 0), pc.split()[3])
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)), (W // 2 - pc.width // 2 + 60, H - pc.height - 10))
    canvas.alpha_composite(pc, (W // 2 - pc.width // 2 + 40, H - pc.height - 40))
    canvas.convert("RGB").save(out, "JPEG", quality=92, subsampling=0)


def N5_fatias_teal(out):
    """ref 5 — três fotos verticais de alegria com cantos arredondados sobre navy/índigo."""
    canvas = E.from_f(fundo_navy(W, H, glow=(0.5, 0.0), forca=1.0)).convert("RGBA")
    fw, gap, fh = 640, 30, 2320
    x0, y0 = (W - 3 * fw - 2 * gap) // 2, (H - fh) // 2
    for i, n in enumerate(["0550", "0656", "0612"]):
        a = grade_natural_dourado(E.to_f(recorte(n, fw, fh, "principal", 0.34)))
        colar(canvas, E.from_f(a), (x0 + i * (fw + gap), y0), mask=mascara_arredondada(fw, fh, 72), sombra=0.45)
    canvas.convert("RGB").save(out, "JPEG", quality=92, subsampling=0)


def N6_bandas_pb(out):
    """ref 6 — três bandas horizontais P&B, full-bleed, frestas off-white."""
    gap = 14
    bh = (H - 2 * gap) // 3
    canvas = Image.new("RGB", (W, H), OFF8)
    for i, n in enumerate(["0104", "0127", "0330"]):
        a = grade_pb(E.to_f(recorte(n, W, bh, "todos", 0.47)))
        canvas.paste(E.from_f(a), (0, i * (bh + gap)))
    canvas.save(out, "JPEG", quality=92, subsampling=0)


def N7_colagem_radial(out):
    """ref 7 — colagem fundida com bordas suaves, zoom blur nas bordas, moldura off-white."""
    base = E.to_f(recorte("0550", W, H, "principal", 0.46))
    comp = base.copy()
    camadas = [  # (foto, cx, cy, rx, ry, w, h)
        ("0046", 1080, 520, 820, 560, 1400, 1100),
        ("0476", 460, 2230, 560, 500, 1100, 950),
        ("0482", 1720, 2180, 560, 560, 1100, 1100),
    ]
    y, x = np.mgrid[0:H, 0:W]
    for n, cx, cy, rx, ry, w, h in camadas:
        im = recorte(n, w, h, "principal", 0.5)
        layer = np.zeros_like(comp)
        x0, y0 = int(np.clip(cx - w / 2, 0, W - w)), int(np.clip(cy - h / 2, 0, H - h))
        layer[y0:y0 + h, x0:x0 + w] = E.to_f(im)
        m = mascara_eliptica(W, H, cx, cy, rx, ry, 260)
        dentro = np.minimum.reduce([x - x0, x0 + w - 1 - x, y - y0, y0 + h - 1 - y]).astype(np.float32)
        m = m * np.clip(dentro / 120, 0, 1)
        comp = comp * (1 - m[..., None]) + layer * m[..., None]
    comp = np.clip(E.sat(E.scurve(comp, 0.12), 1.25) * np.array([1.04, 1.0, 0.97], np.float32) * 1.04, 0, 1)
    zb = zoom_blur(comp, 0.5, 0.5, 0.16, 18)
    mr = E.mask_radial(comp.shape, 0.5, 0.5, 0.14, 0.42)[..., None]
    a = comp * (1 - mr) + zb * mr
    borda = np.minimum.reduce([x, W - 1 - x, y, H - 1 - y]).astype(np.float32)
    fade = np.clip(borda / 160, 0, 1) ** 1.3
    a = a * fade[..., None] + OFF * (1 - fade[..., None])
    E.from_f(E.grain(a, 0.03)).save(out, "JPEG", quality=92, subsampling=0)


POSTS = {
    "N1": ("N1_cards_quente", N1_cards_quente),
    "N2": ("N2_grade6_papel", N2_grade6_papel),
    "N3": ("N3_fatias_lime", N3_fatias_lime),
    "N4": ("N4_semicirculo_cutout", N4_semicirculo_cutout),
    "N5": ("N5_fatias_teal", N5_fatias_teal),
    "N6": ("N6_bandas_pb", N6_bandas_pb),
    "N7": ("N7_colagem_radial", N7_colagem_radial),
}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(POSTS)
    for k in keys:
        nome, fn = POSTS[k]
        try:
            fn(os.path.join(OUT, nome + ".jpg"))
            print("OK", nome, flush=True)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            print("FAIL", nome, repr(e), flush=True)
