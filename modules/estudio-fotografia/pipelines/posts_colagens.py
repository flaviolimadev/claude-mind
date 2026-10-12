#!/usr/bin/env python3
"""10 postagens Instagram 'AVIVA' — cada uma replica uma referencia do ESTUDOS.md
na paleta bordo/cafe/bege. 1080x1350."""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

P = "/Users/flaviolima/Downloads/aviva-senhoras"
SRC_OLD = f"{P}/editadas_cine"
SRC_NEW = f"{P}/novas-fotos/editadas_cine"
OUT = f"{P}/album_final/posts"
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350

BORDO_D = (40, 11, 16)
BORDO = (94, 26, 36)
BORDO_L = (214, 160, 134)
CAFE_D = (26, 17, 12)
CAFE = (62, 42, 30)
CARAMELO = (138, 90, 59)
BEGE = (234, 223, 200)
CREME = (242, 234, 216)
OFFW = (250, 245, 234)
GOLD = (201, 169, 106)

F = "/System/Library/Fonts/Supplemental/"


def font_ttc(path, size, want):
    for i in range(14):
        try:
            f = ImageFont.truetype(path, size, index=i)
            if want.lower() in " ".join(f.getname()).lower():
                return f
        except OSError:
            break
    return None


def F_heavy(s):
    return (font_ttc("/System/Library/Fonts/Avenir Next Condensed.ttc", s, "heavy")
            or ImageFont.truetype(F + "Impact.ttf", s))


def F_black(s):
    return (font_ttc("/System/Library/Fonts/Avenir Next.ttc", s, "heavy")
            or ImageFont.truetype(F + "Arial Narrow Bold.ttf", s))


def F_demi(s):
    return font_ttc("/System/Library/Fonts/Avenir Next.ttc", s, "demi") or F_black(s)


def F_med(s):
    return font_ttc("/System/Library/Fonts/Avenir Next.ttc", s, "medium") or F_demi(s)


def F_script(s):
    return ImageFont.truetype(F + "Georgia Italic.ttf", s)


def foto(n, w, h, oy=0.0):
    for src in (SRC_NEW, SRC_OLD):
        p = os.path.join(src, f"_DSC{n}_cine.jpg")
        if os.path.exists(p):
            im = Image.open(p)
            return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.5 + oy))
    raise FileNotFoundError(n)


def grain(img, amt=5, seed=7):
    a = np.asarray(img, np.int16)
    n = np.random.default_rng(seed).normal(0, amt, a.shape[:2])[..., None]
    return Image.fromarray((a + n).clip(0, 255).astype(np.uint8))


def duotone(img, dark, mid, light):
    g = np.asarray(img.convert("L"), np.float32) / 255.0
    xs = np.array([0, 0.5, 1.0])
    out = np.stack([np.interp(g, xs, [dark[i], mid[i], light[i]]) for i in range(3)], -1)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def halftone(img, cell=7, fg=(80, 20, 28), bg=(26, 12, 10)):
    g = img.convert("L")
    gw, gh = img.width // cell, img.height // cell
    small = np.asarray(g.resize((gw, gh)), np.float32) / 255.0
    out = Image.new("RGB", img.size, bg)
    dr = ImageDraw.Draw(out)
    for yy in range(gh):
        for xx in range(gw):
            r = (small[yy, xx] ** 0.8) * cell * 0.62
            if r > 0.4:
                cx, cy = xx * cell + cell / 2, yy * cell + cell / 2
                dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fg)
    return out


def spaced(dr, x, y, txt, fnt, fill, ls=5, anchor="l"):
    widths = []
    for ch in txt:
        bb = dr.textbbox((0, 0), ch, font=fnt)
        widths.append(bb[2] - bb[0])
    tw = sum(widths) + ls * (len(txt) - 1)
    if anchor == "c":
        x -= tw / 2
    elif anchor == "r":
        x -= tw
    for ch, wd in zip(txt, widths):
        dr.text((x, y), ch, font=fnt, fill=fill)
        x += wd + ls
    return tw


def rounded(img, rad):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], rad, fill=255)
    img = img.convert("RGBA")
    img.putalpha(m)
    return img


def shadow_paste(base, card, x, y, blur=16, off=(0, 12), alpha=110):
    sh = Image.new("RGBA", (card.width + 120, card.height + 120), (0, 0, 0, 0))
    a = card.split()[3].point(lambda p: int(p * alpha / 255))
    sh.paste((12, 6, 5, alpha), (60 + off[0], 60 + off[1]), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.paste(sh, (x - 60, y - 60), sh)
    base.paste(card, (x, y), card)


def leak(img, cx, cy, rad, color, strength):
    lk = Image.new("RGB", img.size, (0, 0, 0))
    ImageDraw.Draw(lk).ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=color)
    lk = lk.filter(ImageFilter.GaussianBlur(rad * 0.6))
    a = np.asarray(img, np.float32)
    l = np.asarray(lk, np.float32) * strength
    return Image.fromarray((255 - (255 - a) * (1 - l / 255)).clip(0, 255).astype(np.uint8))


TEMA = "AVIVA, SENHOR, A TUA OBRA"
SUB = "HABACUQUE 3:2 · ANIVERSÁRIO DO CONJUNTO DE SENHORAS"


def rodape(img, dark_bg=True, y=None):
    dr = ImageDraw.Draw(img)
    y = y or H - 48
    col = (232, 212, 188) if dark_bg else (110, 88, 70)
    spaced(dr, W // 2, y, SUB, F_med(17), col, 3, "c")


# ============================================================ POST 1
def post1():
    art = Image.new("RGB", (W, H), CAFE_D)
    fo = F_heavy(560)
    word = "AVIVA"
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    bb = dm.textbbox((0, 0), word, font=fo)
    dm.text(((W - bb[2] + bb[0]) / 2, (H - bb[3] + bb[1]) / 2 - 60), word, font=fo, fill=255)
    ph = foto(1286, W, H)
    art.paste(ph, (0, 0), mask)
    # janela central nitida com o abraco
    cw, ch = 470, 640
    win = foto(1377, cw, ch)
    m2 = Image.new("L", (cw, ch), 255)
    art.paste(win, ((W - cw) // 2, (H - ch) // 2 - 40), m2)
    dr = ImageDraw.Draw(art)
    dr.rectangle([(W - cw) // 2, (H - ch) // 2 - 40,
                  (W + cw) // 2, (H + ch) // 2 - 40], outline=(240, 226, 205), width=3)
    art = leak(art, 160, 140, 420, (120, 60, 30), 0.85)
    art = leak(art, W - 120, H - 260, 380, (90, 28, 30), 0.8)
    dr = ImageDraw.Draw(art)
    spaced(dr, W // 2, H - 110, "SENHOR, A TUA OBRA", F_demi(30), (238, 220, 198), 8, "c")
    rodape(art)
    grain(art, 7, 1).save(f"{OUT}/post01_letras-mascara.jpg", quality=94)


# ============================================================ POST 2
def post2():
    base = foto(1294, W // 3, H // 3)
    art = halftone(base.resize((W, H)), 7, (84, 24, 32), (24, 13, 10))
    art = art.convert("RGB")
    dr = ImageDraw.Draw(art)
    # header
    dr.ellipse([64, 56, 104, 96], outline=GOLD, width=2)
    dr.line([64, 76, 104, 76], fill=GOLD, width=1)
    dr.arc([72, 56, 96, 96], 0, 360, fill=GOLD, width=1)
    tw1 = spaced(dr, 124, 62, "ANIVERSÁRIO · ", F_med(22), BEGE, 4)
    spaced(dr, 124 + tw1 + 14, 62, "CONJUNTO DE SENHORAS", F_demi(22), OFFW, 4)
    spaced(dr, W - 64, 62, "// 2026 · AVIVA", F_demi(22), GOLD, 4, "r")
    # 3 faixas
    fw, fh, gap = 300, 900, 24
    x0 = (W - 3 * fw - 2 * gap) // 2
    for i, (n, oy) in enumerate([(1327, -0.1), (1446, 0.0), (1353, -0.05)]):
        ph = foto(n, fw, fh, oy)
        art.paste(ph, (x0 + i * (fw + gap), 180))
    # assinatura rabisco
    pts = [(W - 260, H - 150), (W - 210, H - 200), (W - 170, H - 140),
           (W - 130, H - 195), (W - 95, H - 150), (W - 120, H - 120)]
    dr.line(pts, fill=GOLD, width=3, joint="curve")
    spaced(dr, 64, H - 150, TEMA, F_demi(26), OFFW, 5)
    spaced(dr, 64, H - 112, "HABACUQUE 3:2", F_med(20), BEGE, 4)
    grain(art, 6, 2).save(f"{OUT}/post02_faixas-halftone.jpg", quality=94)


# ============================================================ POST 3
def post3():
    # moldura externa: foto com blur radial fake
    bgf = foto(1370, W, H)
    acc = np.asarray(bgf, np.float32)
    for s in (1.04, 1.08, 1.12, 1.16):
        z = bgf.resize((int(W * s), int(H * s)))
        z = z.crop(((z.width - W) // 2, (z.height - H) // 2,
                    (z.width - W) // 2 + W, (z.height - H) // 2 + H))
        acc += np.asarray(z, np.float32)
    bg = Image.fromarray((acc / 5).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
    bg = duotone(bg, BORDO_D, BORDO, (226, 150, 110))
    art = bg.convert("RGB")
    # 3 faixas horizontais coladas
    bx, bw = 80, W - 160
    bh, y0 = 330, 115
    for i, (n, oy) in enumerate([(1363, -0.12), (1485, 0.0), (1375, -0.05)]):
        art.paste(foto(n, bw, bh, oy), (bx, y0 + i * bh))
    dr = ImageDraw.Draw(art)
    fb = F_black(104)
    for txt, (tx, ty), anc in [("aviva", (bx + 18, y0 + bh - 78), "l"),
                               ("senhor,", (bx + bw - 20, y0 + 2 * bh - 78), "r"),
                               ("a tua", (bx + 18, y0 + 3 * bh - 118), "l"),
                               ("obra", (bx + bw - 20, y0 + 3 * bh - 10), "r")]:
        bb = dr.textbbox((0, 0), txt, font=fb)
        x = tx if anc == "l" else tx - (bb[2] - bb[0])
        dr.text((x + 3, ty + 3), txt, font=fb, fill=(30, 10, 10))
        dr.text((x, ty), txt, font=fb, fill=OFFW)
    rodape(art, y=H - 46)
    grain(art, 6, 3).save(f"{OUT}/post03_palavras-faixas.jpg", quality=94)


# ============================================================ POST 4
def post4():
    art = Image.new("RGB", (W, H), CAFE_D)
    fw = W // 5
    for i, (n, oy) in enumerate([(1270, 0.0), (1282, -0.08), (1489, -0.05),
                                 (1294, -0.1), (1352, 0.0)]):
        art.paste(foto(n, fw, H), (i * fw, 0))
        if i:
            ImageDraw.Draw(art).line([i * fw, 0, i * fw, H], fill=CAFE_D, width=4)
    # véu central p/ texto
    dr = ImageDraw.Draw(art, "RGBA")
    dr.rectangle([0, 0, W, H], fill=(30, 16, 12, 70))
    # coracao-chama vetorial
    def heart(cx, cy, s, fill, width=4):
        pts = []
        for k in range(64):
            t = 2 * math.pi * k / 64
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((cx + x * s / 16, cy - y * s / 16))
        dr.line(pts + [pts[0]], fill=fill, width=width, joint="curve")
    heart(W // 2, 150, 40, GOLD)
    dr.line([W // 2, 108, W // 2 - 12, 82], fill=GOLD, width=4)
    dr.line([W // 2, 108, W // 2 + 12, 78], fill=GOLD, width=4)
    spaced(dr, W // 2, H - 220, "ANIVERSÁRIO DO CONJUNTO DE SENHORAS",
           F_med(24), (236, 222, 200), 5, "c")
    spaced(dr, W // 2, H - 178, "AVIVA, SENHOR, A TUA OBRA", F_demi(34), OFFW, 6, "c")
    spaced(dr, W // 2, H - 122, "HABACUQUE 3:2", F_med(22), GOLD, 6, "c")
    grain(art, 7, 4).save(f"{OUT}/post04_cinco-fatias.jpg", quality=94)


# ============================================================ POST 5
def post5():
    base = foto(1294, W // 3, H // 3).resize((W, H))
    art = halftone(base, 8, (96, 30, 38), (22, 11, 9)).convert("RGB")
    dr = ImageDraw.Draw(art)

    def circle_photo(n, dia, cx, cy, oy=0.0):
        ph = foto(n, dia, dia, oy)
        m = Image.new("L", (dia, dia), 0)
        ImageDraw.Draw(m).ellipse([0, 0, dia, dia], fill=255)
        art.paste(ph, (cx - dia // 2, cy - dia // 2), m)

    circle_photo(1363, 640, 400, 620, -0.08)
    circle_photo(1375, 520, 740, 940, -0.05)
    # icones outline topo
    def heartic(cx, cy, s):
        pts = []
        for k in range(48):
            t = 2 * math.pi * k / 48
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((cx + x * s / 16, cy - y * s / 16))
        dr.line(pts + [pts[0]], fill=OFFW, width=3, joint="curve")
    heartic(100, 96, 26)
    dr.polygon([(190, 120), (205, 72), (218, 100), (232, 62), (242, 120)],
               outline=OFFW, width=3)
    dr.ellipse([280, 72, 330, 122], outline=OFFW, width=3)
    dr.line([280, 97, 330, 97], fill=OFFW, width=2)
    dr.arc([292, 72, 318, 122], 0, 360, fill=OFFW, width=2)
    tw = spaced(dr, W - 170, 84, "AVIVA", F_demi(26), OFFW, 5, "r")
    for k, (dig, cxx) in enumerate([("2", W - 150), ("6", W - 104)]):
        dr.ellipse([cxx - 2, 78, cxx + 38, 118], outline=OFFW, width=3)
        fn = F_demi(24)
        bbd = dr.textbbox((0, 0), dig, font=fn)
        dr.text((cxx + 18 - (bbd[2] - bbd[0]) / 2, 86), dig, font=fn, fill=OFFW)
    spaced(dr, W // 2, H - 150, TEMA, F_demi(30), OFFW, 7, "c")
    rodape(art, y=H - 100)
    grain(art, 6, 5).save(f"{OUT}/post05_halftone-circulos.jpg", quality=94)


# ============================================================ POST 6
def post6():
    art = Image.new("RGB", (W, H), (16, 12, 11))
    arts = [(1286, 620, 420, 60, 120, 5), (1310, 560, 400, 440, 430, -4),
            (1336, 600, 410, 60, 700, 4), (1502, 560, 410, 430, 930, -5)]
    for n, cw, ch, x, y, ang in arts:
        ph = foto(n, cw, ch).convert("L")
        ph = Image.merge("RGB", (ph.point(lambda p: int(p * 1.02)),
                                 ph.point(lambda p: int(p * 0.95)),
                                 ph.point(lambda p: int(p * 0.86))))
        card = ph.convert("RGBA").rotate(ang, expand=True, resample=Image.BICUBIC)
        shadow_paste(art, card, x, y, blur=18, alpha=140)
    # streaks dourados
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(st)
    rng = np.random.default_rng(6)
    for _ in range(7):
        x = float(rng.uniform(-200, W))
        ds.line([x, -50, x + 420, H + 50],
                fill=(255, 212, 140, int(rng.uniform(40, 90))),
                width=int(rng.uniform(2, 7)))
    st = st.filter(ImageFilter.GaussianBlur(2))
    art.paste(st, (0, 0), st)
    dr = ImageDraw.Draw(art)
    spaced(dr, 64, H - 92, TEMA, F_demi(26), (235, 220, 200), 6)
    spaced(dr, 64, H - 54, "HABACUQUE 3:2 · ②⑥".replace(" · ②⑥", ""), F_med(20), GOLD, 4)
    grain(art, 8, 6).save(f"{OUT}/post06_pb-streaks.jpg", quality=94)


# ============================================================ POST 7
def post7():
    base = foto(1336, W // 3, H // 3).resize((W, H))
    art = halftone(base, 9, (58, 36, 26), (20, 13, 10)).convert("RGB")
    wins = [(1270, 320, 20, 40, -6), (1286, 360, 380, 10, 4), (1310, 330, 740, 50, -5),
            (1327, 350, 60, 350, 5), (1361, 400, 400, 330, -4), (1377, 330, 760, 390, 6),
            (1428, 360, 30, 740, -5), (1485, 400, 380, 730, 4), (1560, 340, 760, 760, -6),
            (1443, 360, 200, 1020, 3)]
    for n, wdt, x, y, ang in wins:
        ph = foto(n, wdt, int(wdt * 0.72))
        bar_h = 42
        win = Image.new("RGB", (wdt, ph.height + bar_h), (240, 233, 219))
        win.paste(ph, (0, bar_h))
        dw = ImageDraw.Draw(win)
        dw.text((12, 9), f"_DSC{n}.ARW", font=F_med(19), fill=(90, 70, 55))
        dw.ellipse([wdt - 58, 12, wdt - 40, 30], outline=(90, 70, 55), width=2)
        dw.line([wdt - 30, 13, wdt - 14, 29], fill=(90, 70, 55), width=2)
        dw.line([wdt - 30, 29, wdt - 14, 13], fill=(90, 70, 55), width=2)
        card = rounded(win, 14).rotate(ang, expand=True, resample=Image.BICUBIC)
        shadow_paste(art, card, x, y, blur=14, alpha=120)
    dr = ImageDraw.Draw(art)
    spaced(dr, W // 2, H - 56, SUB, F_med(17), (238, 226, 206), 3, "c")
    grain(art, 6, 7).save(f"{OUT}/post07_janelas-arquivo.jpg", quality=94)


# ============================================================ POST 8
def post8():
    hero = foto(1310, 720, 980)
    bgi = foto(1310, W, H).convert("L")
    art = Image.merge("RGB", (bgi.point(lambda p: int(p * 0.5 * 1.05)),
                              bgi.point(lambda p: int(p * 0.5 * 0.92)),
                              bgi.point(lambda p: int(p * 0.5 * 0.82))))
    art = art.filter(ImageFilter.GaussianBlur(4))
    hx, hy = (W - hero.width) // 2, 130
    cell = 180
    rng = np.random.default_rng(8)
    cols = hero.width // cell
    rows = hero.height // cell
    for ry in range(rows):
        for cx in range(cols):
            tile = hero.crop((cx * cell, ry * cell, (cx + 1) * cell, (ry + 1) * cell))
            r = rng.random()
            ox = int(rng.uniform(-14, 14))
            oyy = int(rng.uniform(-14, 14))
            px, py = hx + cx * cell + ox, hy + ry * cell + oyy
            if r < 0.09:
                Image.new("RGB", (cell, cell), BORDO)
                art.paste(Image.new("RGB", (cell - 6, cell - 6), BORDO), (px, py))
            elif r < 0.16:
                art.paste(Image.new("RGB", (cell - 6, cell - 6), CREME), (px, py))
            else:
                sh = Image.new("RGBA", (cell + 40, cell + 40), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rectangle([20, 26, cell + 14, cell + 26],
                                             fill=(10, 6, 5, 110))
                sh = sh.filter(ImageFilter.GaussianBlur(9))
                art.paste(sh, (px - 20, py - 20), sh)
                art.paste(tile.resize((cell - 6, cell - 6)), (px, py))
    dr = ImageDraw.Draw(art)
    spaced(dr, W // 2, H - 150, TEMA, F_demi(30), OFFW, 7, "c")
    spaced(dr, W // 2, H - 104, "HABACUQUE 3:2", F_med(21), GOLD, 5, "c")
    grain(art, 7, 8).save(f"{OUT}/post08_mosaico-quadros.jpg", quality=94)


# ============================================================ POST 9
def post9():
    art = Image.new("RGB", (W, H), BORDO_D)
    cw, chh = W // 3, H // 4
    palavras = ["aviva", "senhor", "a tua", "obra", "hc 3:2", "②⑥"]
    fotos9 = [1270, 1327, 1361, 1443, 1502, 1286]
    rng = np.random.default_rng(9)
    pi = fi = 0
    for ry in range(4):
        for cx in range(3):
            x, y = cx * cw, ry * chh
            is_word = (ry * 3 + cx) % 2 == (ry % 2)
            if is_word and pi < len(palavras):
                blk = np.full((chh, cw, 3), BORDO, np.float32)
                n = rng.normal(0, 9, (chh, cw, 1))
                yy, xx = np.mgrid[0:chh, 0:cw].astype(np.float32)
                d = np.hypot((xx - cw / 2) / cw, (yy - chh / 2) / chh)
                blk *= (1 - 0.5 * d)[..., None]
                blk += n
                tile = Image.fromarray(blk.clip(0, 255).astype(np.uint8))
                dt = ImageDraw.Draw(tile)
                word = palavras[pi]; pi += 1
                if word == "②⑥":
                    for k, dig in enumerate("26"):
                        ccx = cw // 2 - 46 + k * 52
                        dt.ellipse([ccx - 24, chh // 2 - 24, ccx + 24, chh // 2 + 24],
                                   outline=(226, 200, 164), width=3)
                        fn = F_demi(30)
                        bbd = dt.textbbox((0, 0), dig, font=fn)
                        dt.text((ccx - (bbd[2] - bbd[0]) / 2, chh // 2 - 20), dig,
                                font=fn, fill=(226, 200, 164))
                else:
                    fs = F_script(54)
                    bb = dt.textbbox((0, 0), word, font=fs)
                    dt.text(((cw - bb[2] + bb[0]) / 2, (chh - bb[3] + bb[1]) / 2),
                            word, font=fs, fill=(236, 214, 182))
                art.paste(tile, (x, y))
            else:
                if fi < len(fotos9):
                    art.paste(foto(fotos9[fi], cw, chh, -0.05), (x, y))
                    fi += 1
                else:
                    art.paste(Image.new("RGB", (cw, chh), BORDO), (x, y))
    grain(art, 5, 10).save(f"{OUT}/post09_xadrez-veludo.jpg", quality=94)


# ============================================================ POST 10
def post10():
    full = foto(1428, W, H)
    blur = full.filter(ImageFilter.GaussianBlur(7))
    dark = Image.fromarray((np.asarray(blur, np.float32) * 0.42).astype(np.uint8))
    art = dark.convert("RGB")
    fx, fy, fw, fh = 210, 300, 660, 760
    art.paste(full.crop((fx, fy, fx + fw, fy + fh)), (fx, fy))
    dr = ImageDraw.Draw(art)
    c = (242, 232, 214)
    dr.rectangle([fx, fy, fx + fw, fy + fh], outline=c, width=2)
    for px, py in [(fx, fy), (fx + fw, fy), (fx, fy + fh), (fx + fw, fy + fh),
                   (fx + fw // 2, fy), (fx + fw // 2, fy + fh),
                   (fx, fy + fh // 2), (fx + fw, fy + fh // 2)]:
        dr.rectangle([px - 7, py - 7, px + 7, py + 7], fill=(20, 12, 10), outline=c, width=2)
    spaced(dr, W // 2, H - 120, TEMA, F_demi(26), c, 7, "c")
    spaced(dr, W // 2, H - 78, "HABACUQUE 3:2", F_med(19), (200, 176, 148), 5, "c")
    grain(art, 6, 11).save(f"{OUT}/post10_molduraselecao.jpg", quality=94)


import sys
todo = sys.argv[1:] or ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
for t in todo:
    globals()[f"post{t}"]()
    print(f"post{t} ok", flush=True)
