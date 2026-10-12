#!/usr/bin/env python3
# NOTA (claude-mind): script do projeto fundador "ensaio-gabi" — ajuste os caminhos
# (SRC/ALBUM/DST e faixas de numeracao) para o projeto atual antes de rodar.
"""Album PDF 'Ismael' v2 — fundos tematicos por secao, coracoes vetoriais,
fotos inclinadas estilo album artesanal, secao de silhuetas em pagina escura."""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ALBUM = "/Users/flaviolima/Downloads/ensaio-gabi/album_final"
OUT = "/Users/flaviolima/Downloads/ensaio-gabi/album_final/ALBUM_Ismael.pdf"
PW, PH = 2232, 3157
CREAM = (244, 238, 226)
INK = (46, 42, 56)
GOLD = (176, 142, 88)
GOLD_L = (205, 176, 124)
SEP = (110, 94, 74)
DARK_INK = (236, 224, 202)

F = "/System/Library/Fonts/Supplemental/"


def font(name, size):
    try:
        return ImageFont.truetype(F + name, size)
    except OSError:
        return ImageFont.load_default()


f_title = font("Georgia Italic.ttf", 230)
f_h1 = font("Georgia Italic.ttf", 124)
f_h2 = font("Georgia Italic.ttf", 72)
f_small = font("Georgia.ttf", 44)
f_tiny = font("Georgia.ttf", 34)


def heart_pts(cx, cy, size, n=80):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = (13 * math.cos(t) - 5 * math.cos(2 * t)
             - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * size / 16.0, cy - y * size / 16.0))
    return pts


def draw_heart(dr, cx, cy, size, fill):
    dr.polygon(heart_pts(cx, cy, size), fill=fill)


def ctext(dr, y, txt, fnt, fill):
    bb = dr.textbbox((0, 0), txt, font=fnt)
    dr.text(((PW - bb[2] + bb[0]) // 2, y), txt, font=fnt, fill=fill)
    return bb[3] - bb[1]


def add_grain(img, amt=2.4):
    n = np.random.default_rng(3).normal(0, amt, (PH // 4 + 1, PW // 4 + 1, 1))
    n = np.repeat(np.repeat(n, 4, 0), 4, 1)[:PH, :PW]
    a = np.asarray(img, np.int16) + n.astype(np.int16)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def cover_crop(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1),
                   Image.LANCZOS)
    return im.crop(((im.width - w) // 2, (im.height - h) // 2,
                    (im.width - w) // 2 + w, (im.height - h) // 2 + h))


def themed_bg(photo, dark=False, strength=0.18):
    """fundo aquarela: foto da secao desfocada fundida com o papel."""
    im = cover_crop(Image.open(os.path.join(ALBUM, photo)).convert("RGB"),
                    PW // 3, PH // 3).resize((PW, PH), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(70))
    if dark:
        base = Image.new("RGB", (PW, PH), (24, 20, 18))
        bg = Image.blend(base, im, 0.38)
        a = np.asarray(bg, np.float32) * 0.55
        bg = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    else:
        base = Image.new("RGB", (PW, PH), CREAM)
        bg = Image.blend(base, im, strength)
    # vinheta leve
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    d = np.hypot((xx - PW / 2) / (PW / 2), (yy - PH / 2) / (PH / 2)) / 1.42
    v = 1 - (0.22 if not dark else 0.30) * np.clip((d - 0.5) / 0.6, 0, 1) ** 2
    bg = Image.fromarray((np.asarray(bg, np.float32) * v[..., None])
                         .clip(0, 255).astype(np.uint8))
    bg = add_grain(bg)
    # moldura dupla dourada + coracao no topo
    dr = ImageDraw.Draw(bg)
    gold = GOLD if not dark else GOLD_L
    dr.rectangle([110, 110, PW - 110, PH - 110], outline=gold, width=3)
    dr.rectangle([134, 134, PW - 134, PH - 134], outline=gold, width=1)
    draw_heart(dr, PW // 2, 118, 26, gold)
    dr.line([PW // 2 - 180, 118, PW // 2 - 60, 118], fill=gold, width=2)
    dr.line([PW // 2 + 60, 118, PW // 2 + 180, 118], fill=gold, width=2)
    return bg


def paste_photo(page, path, cx, cy, w, h, angle=0.0, border=20):
    im = ImageOps.contain(Image.open(os.path.join(ALBUM, path)), (w, h),
                          Image.LANCZOS)
    card = Image.new("RGB", (im.width + 2 * border, im.height + 2 * border),
                     (252, 250, 245))
    card.paste(im, (border, border))
    if angle:
        card = card.convert("RGBA").rotate(angle, expand=True,
                                           resample=Image.BICUBIC)
    else:
        card = card.convert("RGBA")
    # sombra
    sh = Image.new("RGBA", (card.width + 120, card.height + 120), (0, 0, 0, 0))
    alpha = card.split()[3].point(lambda p: int(p * 0.45))
    sh.paste((25, 18, 12, 115), (70, 82), alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    x = cx - card.width // 2
    y = cy - card.height // 2
    page.paste(sh, (x - 60, y - 60), sh)
    page.paste(card, (x, y), card)
    return y + card.height


def caption(page, y, txt, dark=False):
    dr = ImageDraw.Draw(page)
    fill = SEP if not dark else GOLD_L
    bb = dr.textbbox((0, 0), txt, font=f_h2)
    tw = bb[2] - bb[0]
    cx = PW // 2
    dr.text((cx - tw // 2, y), txt, font=f_h2, fill=fill)
    dr.line([cx - tw // 2 - 170, y + 50, cx - tw // 2 - 50, y + 50],
            fill=GOLD, width=2)
    dr.line([cx + tw // 2 + 50, y + 50, cx + tw // 2 + 170, y + 50],
            fill=GOLD, width=2)


def photo_page(bgp, path, cap=None, dark=False):
    page = themed_bg(bgp, dark)
    yb = paste_photo(page, path, PW // 2, PH // 2 - 60, PW - 440, PH - 700)
    if cap:
        caption(page, yb + 60, cap, dark)
    return page


def duo_page(bgp, p1, p2, cap=None, dark=False):
    page = themed_bg(bgp, dark)
    paste_photo(page, p1, PW // 2 - 460, PH // 2 - 680, 980, 1380, angle=2.4)
    paste_photo(page, p2, PW // 2 + 460, PH // 2 + 600, 980, 1380, angle=-2.4)
    dr = ImageDraw.Draw(page)
    draw_heart(dr, PW // 2, PH // 2 - 20, 30, GOLD if not dark else GOLD_L)
    if cap:
        caption(page, PH - 320, cap, dark)
    return page


def divider(bgp, title, sub, dark=False):
    page = themed_bg(bgp, dark, strength=0.34)
    dr = ImageDraw.Draw(page)
    ink = INK if not dark else DARK_INK
    draw_heart(dr, PW // 2, PH // 2 - 330, 46, GOLD)
    h = ctext(dr, PH // 2 - 220, title, f_h1, ink)
    ctext(dr, PH // 2 - 220 + h + 90, sub, f_small,
          SEP if not dark else GOLD_L)
    return page


pages = []

# ---------- CAPA (aprovada, mantida) ----------
cover = cover_crop(Image.open(os.path.join(ALBUM, "36_arte-ultrassom-4k.png"))
                   .convert("RGB"), PW, PH)
dr = ImageDraw.Draw(cover)
grad = Image.new("L", (1, 500), 0)
for i in range(500):
    grad.putpixel((0, i), int(200 * (i / 500) ** 1.5))
grad = grad.resize((PW, 500))
cover.paste(Image.new("RGB", (PW, 500), (8, 6, 4)), (0, PH - 500), grad)
bb = dr.textbbox((0, 0), "Ismael", font=f_title)
dr.text(((PW - bb[2] + bb[0]) // 2 + 4, PH - 414), "Ismael", font=f_title,
        fill=(60, 40, 20))
dr.text(((PW - bb[2] + bb[0]) // 2, PH - 418), "Ismael", font=f_title,
        fill=(238, 214, 170))
bb2 = dr.textbbox((0, 0), "nosso maior presente", font=f_small)
dr.text(((PW - bb2[2] + bb2[0]) // 2, PH - 150), "nosso maior presente",
        font=f_small, fill=(205, 185, 150))
pages.append(cover)

# ---------- FOLHA DE ROSTO ----------
page = themed_bg("08_beijo-barriga.png", strength=0.14)
dr = ImageDraw.Draw(page)
h = ctext(dr, PH // 2 - 460, "Ismael", f_title, INK)
ctext(dr, PH // 2 + 40, "O ensaio da espera", f_h2, SEP)
draw_heart(dr, PW // 2, PH // 2 + 270, 34, GOLD)
dr.text((PW // 2 - 250, PH // 2 + 330), "Gabi", font=f_small, fill=SEP)
dr.text((PW // 2 + 130, PH // 2 + 330), "2026", font=f_small, fill=SEP)
pages.append(page)

# ---------- SECAO 1: jardim ----------
pages.append(divider("15_arvore.png", "O começo do dia",
                     "making-of e os primeiros sorrisos"))
pages.append(duo_page("01_making-of.png", "01_making-of.png",
                      "02_making-of.png", "os últimos retoques"))
pages.append(photo_page("03_ele.png", "03_ele.png", "o papai de Ismael"))
pages.append(duo_page("04_sapatinhos.png", "04_sapatinhos.png",
                      "05_sapatinhos-barriga.png", "os primeiros sapatinhos"))
pages.append(photo_page("06_casal-pergolado.png", "06_casal-pergolado.png"))
pages.append(photo_page("07_rede.png", "07_rede.png"))
pages.append(photo_page("08_beijo-barriga.png", "08_beijo-barriga.png",
                        "primeiro beijo"))
pages.append(duo_page("10_flor-exame.png", "09_carinho.png",
                      "10_flor-exame.png"))
pages.append(photo_page("11_ultrassom-celular.png", "11_ultrassom-celular.png",
                        "oi, Ismael"))
pages.append(duo_page("12_balanco-enxoval.png", "12_balanco-enxoval.png",
                      "13_roupinha.png", "tudo pronto para você"))
pages.append(photo_page("15_arvore.png", "15_arvore.png"))
pages.append(duo_page("16_flare-arte.png", "14_arvore-close.png",
                      "16_flare-arte.png"))
pages.append(photo_page("19_abraco-dourado.png", "19_abraco-dourado.png",
                        "luz de fim de tarde"))
pages.append(duo_page("18_olhares.png", "17_flare-perfil.png",
                      "18_olhares.png"))
pages.append(duo_page("20_abraco-riso.png", "20_abraco-riso.png",
                      "21_enxoval-flatlay.png"))

# ---------- SECAO 2: piscina ----------
pages.append(divider("24_danca-piscina.png", "Entre risos e água",
                     "a leveza de esperar por você"))
pages.append(photo_page("22_gargalhada.png", "22_gargalhada.png",
                        "alegria que transborda"))
pages.append(duo_page("24_danca-piscina.png", "23_olhar-maos.png",
                      "24_danca-piscina.png"))
pages.append(duo_page("26_maos-barriga.png", "25_perfil-arvore.png",
                      "26_maos-barriga.png"))
pages.append(photo_page("27_ele-fotografando.png", "27_ele-fotografando.png"))

# ---------- SECAO 3: silhuetas (paginas escuras) ----------
pages.append(divider("29_silhueta-beijo.jpg", "Na luz e na sombra",
                     "quando o amor vira silhueta", dark=True))
pages.append(photo_page("28_silhueta-perfil.jpg", "28_silhueta-perfil.jpg",
                        dark=True))
pages.append(duo_page("29_silhueta-beijo.jpg", "29_silhueta-beijo.jpg",
                      "30_silhueta-casal.jpg", dark=True))
pages.append(duo_page("31_silhueta-sorriso.jpg", "31_silhueta-sorriso.jpg",
                      "32_silhueta-lowkey.jpg", dark=True))
pages.append(duo_page("33_silhueta-sepia.jpg", "33_silhueta-sepia.jpg",
                      "34_silhueta-beijo-sepia.jpg", dark=True))
pages.append(photo_page("35_arte-ultrassom.jpg", "35_arte-ultrassom.jpg",
                        "o primeiro retrato de Ismael", dark=True))

# ---------- SECAO 4: praia ----------
pages.append(divider("45_praia-ceu-rosa.png", "O pôr do sol",
                     "o mar guardou o segredo até aqui"))
pages.append(photo_page("45_praia-ceu-rosa.png", "45_praia-ceu-rosa.png"))
pages.append(duo_page("40_praia-perfil-falesia.png", "39_praia-sorriso.png",
                      "40_praia-perfil-falesia.png"))
pages.append(duo_page("42_praia-testas.png", "41_praia-maos-dadas.png",
                      "42_praia-testas.png"))
pages.append(photo_page("43_praia-abraco.png", "43_praia-abraco.png"))
pages.append(duo_page("44_praia-olhando-mar.png", "44_praia-olhando-mar.png",
                      "47_praia-beijo-barcos.png", "esperando você chegar"))
pages.append(photo_page("46_praia-beijo-barriga.png",
                        "46_praia-beijo-barriga.png", "até já, meu amor"))
pages.append(duo_page("48_praia-riso-ajoelhado.png",
                      "48_praia-riso-ajoelhado.png",
                      "49_praia-maos-barriga.png"))
pages.append(duo_page("50_muro-verde-sorriso.png", "50_muro-verde-sorriso.png",
                      "51_muro-verde-olhares.png"))
pages.append(duo_page("52_quadro-gato.png", "52_quadro-gato.png",
                      "53_jardim-testas.png"))

# ---------- CONTRACAPA ----------
page = themed_bg("37_hero-arvore-dreamy-4k.png", strength=0.22)
paste_photo(page, "37_hero-arvore-dreamy-4k.png", PW // 2, PH // 2 - 350,
            1280, 1850)
dr = ImageDraw.Draw(page)
ctext(dr, PH - 760, "Te esperamos com amor,", f_h2, INK)
ctext(dr, PH - 610, "Ismael", f_h1, GOLD)
draw_heart(dr, PW // 2, PH - 390, 28, GOLD)
ctext(dr, PH - 310, "outubro de 2026", f_tiny, SEP)
pages.append(page)

pages[0].save(OUT, save_all=True, append_images=pages[1:], resolution=270.0)
print("PDF v2 pronto:", OUT, len(pages), "paginas",
      round(os.path.getsize(OUT) / 1e6, 1), "MB")

S = os.path.dirname(os.path.abspath(__file__))
for i in [1, 3, 9, 22, 24, 28]:
    pages[i].resize((pages[i].width // 3, pages[i].height // 3)).save(
        f"{S}/pdf2page_{i}.jpg", quality=88)
print("previews ok")
