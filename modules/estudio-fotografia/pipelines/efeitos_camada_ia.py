#!/usr/bin/env python3
"""Estilos das 4 referências para os POSTS (pedido: "usar Higgsfield… sem alterar o cenário ou as
pessoas, apenas o efeito usando a foto original").
A foto é a revelação fiel (ENTREGA/01, pixels originais). O Higgsfield entra SÓ como camada de
efeito gerada em fundo preto (hf/fx/: anéis de luz, prisma, poeira, feixe, névoa) aplicada por
screen. O resto é global (tom/cor/grão/vinheta) ou fora do sujeito (spin blur). Nada redesenhado.

  A lowkey_quente  (ref 1) — escuro, quente, bloom, névoa/poeira, vinheta
  B duotone_teal   (ref 2) — monocromático azul-petróleo, névoa, grão
  C spin_blur      (ref 3) — rotação ao redor do rosto central nítido, quente
  D aneis_prisma   (ref 4) — anéis de luz/prisma ao redor do sujeito, grade film quente

Saída 4:5 (3200×4000) em ENTREGA/03_posts-estilo-refs/<estilo>/IMG_NNNN_<estilo>.jpg
uso: python3 betfage_estilos.py            (plano /tmp/betfage_estilos.json)
     python3 betfage_estilos.py D 0150 ...  (estilo + fotos)"""
import json
import math
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.expanduser("<PROJETO>")
SRC = os.path.join(ROOT, "ENTREGA", "01_fotos-editadas")
FX = os.path.join(ROOT, "hf", "fx")
OUT = os.path.join(ROOT, "ENTREGA", "03_posts-estilo-refs")
NOMES = {"A": "lowkey_quente", "B": "duotone_teal", "C": "spin_blur", "D": "aneis_prisma"}
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- utilidades
def to_f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255


def from_f(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def blur(a, r):
    """gaussiano em float; para raios grandes reduz, borra e amplia (rápido)."""
    im = from_f(a)
    if r > 12:
        k = r / 6
        small = im.resize((max(8, int(im.width / k)), max(8, int(im.height / k))), Image.BOX)
        return np.asarray(small.filter(ImageFilter.GaussianBlur(6)).resize(im.size, Image.BILINEAR), np.float32) / 255
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def scurve(a, k):
    return np.clip(a + k * np.sin(2 * np.pi * (a - 0.5)) * (a * (1 - a) * 4) * 0.5, 0, 1)


def sat(a, s):
    l = lum(a)[..., None]
    return np.clip(l + (a - l) * s, 0, 1)


def grain(a, sigma):
    h, w = a.shape[:2]
    g = RNG.normal(0, sigma, (h, w)).astype(np.float32)
    peso = (1 - lum(a)) * 0.7 + 0.3  # menos grão nas luzes
    return np.clip(a + (g * peso)[..., None], 0, 1)


def vinheta(a, forca, pot=2.2, cx=0.5, cy=0.5):
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x / w - cx) * 1.0) ** 2 + ((y / h - cy) * 0.8) ** 2) / 0.72
    v = 1 - forca * np.clip(d, 0, 1) ** pot
    return a * v[..., None]


def screen(a, layer, op):
    return np.clip(a + layer * op - a * layer * op, 0, 1)


def camada_fx(nome, size, center=None, escala=1.0, preto=0.06, rot=0):
    """camada Higgsfield (fundo preto) → float, nível de preto removido, 'cover' no tamanho,
    centrada em `center` (fração) e opcionalmente girada."""
    W, H = size
    im = Image.open(os.path.join(FX, nome)).convert("RGB")
    if rot:
        im = im.rotate(rot, resample=Image.BILINEAR)
    k = max(W / im.width, H / im.height) * escala
    im = im.resize((int(im.width * k) + 1, int(im.height * k) + 1), Image.LANCZOS)
    cx, cy = (0.5, 0.5) if center is None else center
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    canvas.paste(im, (int(W * cx - im.width / 2), int(H * cy - im.height / 2)))
    a = to_f(canvas)
    return np.clip((a - preto) / (1 - preto), 0, 1)


def mascara(n, size):
    p = os.path.join(ROOT, "hf", f"{n}_mask.png")
    if not os.path.exists(p):
        return None
    return np.asarray(Image.open(p).convert("L").resize(size, Image.BILINEAR), np.float32) / 255


def foco(m):
    """ponto de interesse: centróide da máscara na parte ALTA da caixa (onde ficam os rostos)."""
    if m is None or m.sum() < 100:
        return 0.5, 0.42
    ys, xs = np.nonzero(m > 0.5)
    y0, y1 = np.percentile(ys, 2), np.percentile(ys, 98)
    top = ys < y0 + 0.45 * (y1 - y0)
    if top.sum() < 50:
        top = np.ones_like(ys, bool)
    return float(xs[top].mean() / m.shape[1]), float(ys[top].mean() / m.shape[0])


def corte45(im, m, fx):
    """3:2 → 4:5 centrado horizontalmente no foco (altura inteira)."""
    W, H = im.size
    cw = int(H * 4 / 5)
    x0 = int(np.clip(fx * W - cw / 2, 0, W - cw))
    im2 = im.crop((x0, 0, x0 + cw, H))
    m2 = None if m is None else m[:, x0:x0 + cw]
    return im2, m2


def spin(a, fx, fy, graus, n=24, pad=0.18):
    """média de rotações em torno de (fx,fy) — calculado em 1600px e ampliado."""
    im = from_f(a)
    k = 1600 / im.width
    small = im.resize((1600, int(im.height * k)), Image.BILINEAR)
    s = np.asarray(small, np.float32) / 255
    ph, pw = int(s.shape[0] * pad), int(s.shape[1] * pad)
    sp = np.pad(s, ((ph, ph), (pw, pw), (0, 0)), mode="reflect")
    imp = from_f(sp)
    cx, cy = fx * s.shape[1] + pw, fy * s.shape[0] + ph
    acc = np.zeros_like(sp)
    angs = np.linspace(-graus, graus, n)
    for g in angs:
        acc += np.asarray(imp.rotate(g, resample=Image.BILINEAR, center=(cx, cy)), np.float32) / 255
    acc /= n
    out = from_f(acc[ph:ph + s.shape[0], pw:pw + s.shape[1]]).resize(im.size, Image.BICUBIC)
    return to_f(out)


def mask_radial(shape, fx, fy, r_in, r_out):
    h, w = shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt((x - fx * w) ** 2 + (y - fy * h) ** 2) / math.hypot(w, h)
    t = np.clip((d - r_in) / max(r_out - r_in, 1e-3), 0, 1)
    return (t * t * (3 - 2 * t)).astype(np.float32)


# ---------------------------------------------------------------- estilos
def A_lowkey_quente(a, m, fx, fy):
    a = np.clip(a, 0, 1) ** 1.3 * 0.93                # escurece como a ref 1
    a = np.clip((a - 0.025) / 0.975, 0, 1)            # pretos profundos
    a = scurve(a, 0.14)
    a = sat(a, 0.8)
    l = lum(a)[..., None]
    sombra = (1 - l)
    a = a * np.array([1.045, 1.0, 0.9], np.float32)   # quente, sem virar amarelo
    a = np.clip(a + sombra * np.array([0.02, 0.008, -0.015], np.float32), 0, 1)  # sombras marrons
    hi = np.clip((lum(a) - 0.62) / 0.38, 0, 1)[..., None]
    a = np.clip(a + blur(a * hi, 60) * 0.18, 0, 1)    # bloom
    nev = camada_fx("fx4_poeira.png", (a.shape[1], a.shape[0]), escala=1.05) * np.array([1.0, 0.88, 0.7], np.float32)
    a = screen(a, nev, 0.2)
    fei = camada_fx("fx5_feixe.png", (a.shape[1], a.shape[0]), escala=1.1) * np.array([1.0, 0.92, 0.78], np.float32)
    a = screen(a, fei, 0.13)
    a = vinheta(a, 0.58, 2.0, cx=fx, cy=min(fy + 0.1, 0.7))
    return grain(a, 0.03)


def B_duotone_teal(a, m, fx, fy):
    l = scurve(lum(a), 0.16)
    l = np.clip((l - 0.02) / 0.98, 0, 1)
    stops = np.array([0.0, 0.5, 1.0])
    cores = np.array([[10, 28, 32], [52, 112, 118], [206, 228, 224]], np.float32) / 255
    a = np.stack([np.interp(l, stops, cores[:, c]) for c in range(3)], axis=-1).astype(np.float32)
    nev = camada_fx("fx6_nevoa.png", (a.shape[1], a.shape[0]), escala=1.05) * np.array([0.62, 0.92, 0.9], np.float32)
    a = screen(a, nev, 0.32)
    a = vinheta(a, 0.32, 2.4)
    return grain(a, 0.045)


def C_spin_blur(a, m, fx, fy):
    b = spin(a, fx, fy, graus=7, n=26)
    mr = mask_radial(a.shape, fx, fy, 0.16, 0.5)[..., None]
    a = a * (1 - mr) + b * mr                           # centro = pixels originais
    a = scurve(a, 0.10)
    a = sat(a, 0.92) * np.array([1.05, 0.99, 0.92], np.float32)
    nev = camada_fx("fx4_poeira.png", (a.shape[1], a.shape[0]), escala=1.1, rot=180) * np.array([1.0, 0.9, 0.75], np.float32)
    a = screen(a, nev, 0.14)
    a = vinheta(a, 0.45, 2.0, cx=fx, cy=fy)
    return grain(a, 0.028)


def D_aneis_prisma(a, m, fx, fy, camada="fx1_aneis.png"):
    b = spin(a, fx, fy, graus=3, n=16)
    mr = mask_radial(a.shape, fx, fy, 0.28, 0.6)[..., None]
    a = a * (1 - mr) + b * mr
    a = np.clip(a * 0.96 + 0.035, 0, 1)                 # matte film
    a = scurve(a, 0.11)
    a = sat(a, 0.88) * np.array([1.06, 1.0, 0.88], np.float32)
    l = lum(a)[..., None]
    a = np.clip(a + (1 - l) * np.array([0.025, 0.02, -0.01], np.float32), 0, 1)  # sombras oliva
    anel = camada_fx(camada, (a.shape[1], a.shape[0]), center=(fx, fy), escala=0.95)
    if camada == "fx3_prisma.png":                      # anel fino: amacia pra não parecer vetor
        anel = blur(anel, 10) * 1.15
        op = 0.72
    else:
        op = 0.92
    a = screen(a, anel, op)
    hi = np.clip((lum(a) - 0.65) / 0.35, 0, 1)[..., None]
    a = np.clip(a + blur(a * hi, 50) * 0.12, 0, 1)    # bloom quente leve
    a = vinheta(a, 0.35, 2.2)
    return grain(a, 0.032)


ESTILOS = {"A": A_lowkey_quente, "B": B_duotone_teal, "C": C_spin_blur, "D": D_aneis_prisma}
ANEIS = ["fx1_aneis.png", "fx2_circulos.png", "fx3_prisma.png"]


FOCO_MANUAL = {}  # (fx, fy) em frações da foto 3:2, quando quiser forçar o foco
MODO_FOCO = {"A": "todos", "C": "principal", "D": "principal"}  # A = multidão/união; C e D = um rosto


def foco_rosto(n, estilo, m):
    """foco pelo ROSTO (Vision, pontuado) → fallback na máscara rembg."""
    if n in FOCO_MANUAL:
        return FOCO_MANUAL[n]
    try:
        from betfage_rostos import alvo
        a = alvo(n, MODO_FOCO.get(estilo, "principal"))
        if a is not None:
            return a
    except Exception:  # noqa: BLE001
        pass
    return foco(m)


def aplicar(estilo, n, idx=0):
    im = Image.open(os.path.join(SRC, f"IMG_{n}.jpg")).convert("RGB")
    m = mascara(n, im.size)
    fx, fy = foco_rosto(n, estilo, m)
    W0 = im.width
    im, m = corte45(im, m, fx)
    # converte o foco (frações da foto 3:2) para frações do corte 4:5
    x0 = np.clip(fx * W0 - im.width / 2, 0, W0 - im.width)
    fx = float((fx * W0 - x0) / im.width)
    a = to_f(im)
    if estilo == "D":
        out = D_aneis_prisma(a, m, fx, fy, ANEIS[idx % len(ANEIS)])
    else:
        out = ESTILOS[estilo](a, m, fx, fy)
    pasta = os.path.join(OUT, f"{estilo}_{NOMES[estilo]}")
    os.makedirs(pasta, exist_ok=True)
    dst = os.path.join(pasta, f"IMG_{n}_{NOMES[estilo]}.jpg")
    from_f(out).save(dst, "JPEG", quality=92, subsampling=0)
    print(f"{estilo} {n} foco=({fx:.2f},{fy:.2f}) -> {os.path.relpath(dst, ROOT)}", flush=True)
    return dst


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        for i, n in enumerate(args[1:]):
            aplicar(args[0], n, i)
    else:
        plano = json.load(open("/tmp/betfage_estilos.json"))
        for chave, nums in plano.items():
            for i, n in enumerate(nums):
                aplicar(chave[0], n, i)
    print("ESTILOS FIM", flush=True)
