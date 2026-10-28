#!/usr/bin/env python3
"""Revelação FIEL À CÂMERA — "fotos reais, luz natural, sem IA, não modifique a foto".
A conversão RAW→JPEG do macOS (sips) sai mais escura e lavada que o JPG gravado pela câmera.
Casamos a conversão full-res com o JPG da câmera por histogram-matching GLOBAL por canal (tom e
cor da câmera em resolução cheia) e aplicamos só um acabamento mínimo (abertura de sombras em
cenas muito escuras, preto assentado). Nada local, nada generativo.

uso: python3 revelar_fiel_camera.py --full DIR_FULL --cam DIR_CAM --out DIR_OUT [--prefix IMG_] NNNN [NNNN ...]
     (ou @lista.json no lugar dos números)
  DIR_FULL/NNNN.jpg  = RAW convertido em resolução cheia
  DIR_CAM/IMG_NNNN.JPG = JPG original da câmera (referência de tom/cor)
  DIR_OUT/NNNN_rev.jpg = saída q95"""
import argparse
import json
import os
import numpy as np
from PIL import Image, ImageOps


def lut_match(src_small, ref_small):
    """LUT 256 por canal: quantis da conversão → quantis do JPG da câmera (monotônica)."""
    luts = []
    for c in range(3):
        hs = np.bincount(src_small[..., c].ravel(), minlength=256).astype(np.float64)
        hr = np.bincount(ref_small[..., c].ravel(), minlength=256).astype(np.float64)
        cs = np.cumsum(hs) / hs.sum()
        cr = np.cumsum(hr) / hr.sum()
        luts.append(np.maximum.accumulate(np.interp(cs, cr, np.arange(256)).astype(np.float32)))
    return luts


def revelar(full_path, cam_path, out_path, lift_dark=True, dark_med=0.22, max_gain=1.25):
    full = Image.open(full_path).convert("RGB")
    cam = ImageOps.exif_transpose(Image.open(cam_path)).convert("RGB")
    if (cam.size[0] < cam.size[1]) != (full.size[0] < full.size[1]):
        full = full.transpose(Image.ROTATE_270)
    luts = lut_match(np.asarray(full.resize((600, 400), Image.BOX)), np.asarray(cam.resize((600, 400), Image.BOX)))
    a = np.asarray(full)
    out = np.stack([np.take(luts[c], a[..., c]) for c in range(3)], axis=-1) / 255.0
    med = float(np.median(out[::16, ::16].mean(-1)))
    if lift_dark and med < dark_med:
        out = out * min(max_gain, dark_med / max(med, 0.02))
        t = np.maximum(out - 0.80, 0)
        out = np.where(out > 0.80, 0.80 + t / (1 + t / 0.20), out)  # ombro: nada estoura
    out = np.clip((out - 0.006) / (1 - 0.006), 0, 1)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(out_path, "JPEG", quality=95, subsampling=0)
    return med


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", required=True)
    ap.add_argument("--cam", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", default="IMG_")
    ap.add_argument("nums", nargs="+")
    args = ap.parse_args()
    nums = json.load(open(args.nums[0][1:])) if args.nums[0].startswith("@") else args.nums
    os.makedirs(args.out, exist_ok=True)
    for i, n in enumerate(nums):
        fp = os.path.join(args.full, f"{n}.jpg")
        cp = os.path.join(args.cam, f"{args.prefix}{n}.JPG")
        if os.path.exists(fp) and os.path.exists(cp):
            revelar(fp, cp, os.path.join(args.out, f"{n}_rev.jpg"))
        else:
            print("falta origem", n, flush=True)
        if (i + 1) % 25 == 0:
            print(f"{i+1}/{len(nums)}", flush=True)
    print("FIM", flush=True)
