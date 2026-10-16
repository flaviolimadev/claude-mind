#!/usr/bin/env python3
"""Revelação FIEL de RAW para foto de produto (módulo loja-catalogo do claude-mind).

Balanço de branco por um neutro da própria cena (aço, etiqueta branca, fundo cinza), exposição
automática pelo percentil 98 com ombro suave nos brilhos, curva S leve, NR de croma, sRGB e
recorte quadrado. Sem autocontraste, sem saturação: o produto tem que ser o produto.

Dependências: pip install rawpy numpy pillow

Uso:
  # 1) medir os ganhos de WB num trecho neutro (caixa x0,y0,x1,y1 em pixels do RAW decodificado)
  python3 revelar_raw.py wb  foto.ARW --box 2400,1800,2600,1900            # imprime R,B
  # 2) revelar o lote com esses ganhos, quadrado 2000 px, centrado (ou --center x,y --size w,h)
  python3 revelar_raw.py dev foto1.ARW foto2.ARW --wb 1.302,1.165 --out tratadas/ --square 2000

Validado em 2026-10-16 (Sony ZV-E10, relógios ~4 EV subexpostos em caixa verde).
"""
import argparse, os, sys
import numpy as np, rawpy
from PIL import Image, ImageFilter

LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)

def decode(path):
    """16 bits lineares, WB da câmera, sem auto-brilho. O rawpy já entrega o quadro em pé: não girar."""
    with rawpy.imread(path) as r:
        return r.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=16, gamma=(1, 1),
                             output_color=rawpy.ColorSpace.sRGB, demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
                             highlight_mode=rawpy.HighlightMode.Blend, fbdd_noise_reduction=rawpy.FBDDNoiseReductionMode.Light)

def srgb(x):
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(np.maximum(x, 0), 1 / 2.4) - 0.055)

def wb_gains(lin16, box):
    """Ganhos R,B que tornam cinza a mediana do trecho neutro (G fica 1.0)."""
    x0, y0, x1, y1 = box
    med = np.median(lin16[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32), axis=0)
    return float(med[1] / med[0]), float(med[1] / med[2])

def develop(lin16, gR, gB, target=0.86, knee=0.80, contrast=0.18, ev_clamp=(1.0, 30.0)):
    f = lin16.astype(np.float32) / 65535
    f *= np.array([gR, 1.0, gB], np.float32)                      # balanço de branco
    luma = f @ LUMA
    g = float(np.clip(target / max(1e-6, np.percentile(luma, 98.0)), *ev_clamp))  # p98 → 0.86 linear
    f *= g
    hi = f > knee                                                  # ombro suave: brilho do metal não estoura
    f = np.where(hi, knee + (1 - knee) * (1 - np.exp(-(f - knee) / (1 - knee))), f)
    s = srgb(np.clip(f, 0, 1))
    s = s + contrast * (s - 0.5) * (1 - np.abs(2 * s - 1)) * 0.5   # curva S leve só nos meios-tons
    img = Image.fromarray((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8))
    y, cb, cr = img.convert('YCbCr').split()                       # NR de croma (ruído colorido da sombra levantada)
    cb = cb.filter(ImageFilter.GaussianBlur(2.2)); cr = cr.filter(ImageFilter.GaussianBlur(2.2))
    return Image.merge('YCbCr', (y, cb, cr)).convert('RGB'), g

def finish(img, size, sharp=(1.0, 55, 2)):
    out = img.resize(size, Image.LANCZOS)
    return out.filter(ImageFilter.UnsharpMask(radius=sharp[0], percent=sharp[1], threshold=sharp[2]))

def crop_box(W, H, cx, cy, w, h):
    w = min(w, W); h = min(h, H)
    l = int(min(max(cx - w / 2, 0), W - w)); t = int(min(max(cy - h / 2, 0), H - h))
    return (l, t, l + w, t + h)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('wb', help='mede os ganhos R,B num trecho neutro'); a.add_argument('raw'); a.add_argument('--box', required=True)
    d = sub.add_parser('dev', help='revela o lote'); d.add_argument('raws', nargs='+'); d.add_argument('--wb', default='1,1', help='ganhos R,B (de `wb`)')
    d.add_argument('--out', default='tratadas'); d.add_argument('--square', type=int, default=2000)
    d.add_argument('--center', help='x,y do centro do recorte (padrão: centro do quadro)'); d.add_argument('--size', help='w,h do recorte antes do resize')
    args = ap.parse_args()
    if args.cmd == 'wb':
        gR, gB = wb_gains(decode(args.raw), tuple(int(v) for v in args.box.split(',')))
        print(f'--wb {gR:.3f},{gB:.3f}'); return
    gR, gB = (float(v) for v in args.wb.split(','))
    os.makedirs(args.out, exist_ok=True)
    for p in args.raws:
        img, g = develop(decode(p), gR, gB)
        W, H = img.size
        cx, cy = (int(v) for v in args.center.split(',')) if args.center else (W // 2, H // 2)
        w, h = (int(v) for v in args.size.split(',')) if args.size else (min(W, H), min(W, H))
        out = finish(img.crop(crop_box(W, H, cx, cy, w, h)), (args.square, args.square))
        dst = os.path.join(args.out, os.path.splitext(os.path.basename(p))[0] + '.jpg')
        out.save(dst, quality=90, optimize=True)
        print(f'{os.path.basename(p)} → {dst}  (ganho de exposição {g:.2f}×)')

if __name__ == '__main__':
    main()
