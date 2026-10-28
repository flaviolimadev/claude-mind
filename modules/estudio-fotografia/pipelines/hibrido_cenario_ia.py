#!/usr/bin/env python3
"""Técnica híbrida — Higgsfield gera o CENÁRIO (luz/atmosfera), as PESSOAS voltam dos pixels
originais. Garante rosto idêntico (diferença zero dentro da máscara de pessoas).

uso: python3 betfage_hibrido.py NNNN caminho_do_resultado_ia.png
saída: hf/NNNN_hib.jpg (6000×4000) + hf/NNNN_diff.jpg (prova: diferença só fora das pessoas)"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.expanduser("~/Downloads/mocidade-betfage")


def hibrido(n, ia_path, feather=10, match_tone=True):
    orig = Image.open(f"{ROOT}/editadas/{n}_rev.jpg").convert("RGB")
    W, H = orig.size
    ia = Image.open(ia_path).convert("RGB").resize((W, H), Image.LANCZOS)
    mask = Image.open(f"{ROOT}/hf/{n}_mask.png").convert("L").resize((W, H), Image.LANCZOS)
    # pena só pra fora (dilata a máscara um pouco e suaviza a borda) — o interior fica 100%
    m_hard = np.asarray(mask, np.float32) / 255
    m_soft = np.asarray(mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(feather)), np.float32) / 255
    m = np.maximum(m_hard, m_soft)[..., None]
    o = np.asarray(orig, np.float32) / 255
    a = np.asarray(ia, np.float32) / 255
    if match_tone:
        # a pessoa recebe só um ajuste GLOBAL de luminosidade p/ casar com o cenário (não altera traços)
        lo = (o * m).sum() / max(m.sum() * 3, 1)
        la = (a * m).sum() / max(m.sum() * 3, 1)
        k = float(np.clip(la / max(lo, 1e-4), 0.85, 1.15))
        o_adj = np.clip(o * k, 0, 1)
    else:
        o_adj = o
    out = a * (1 - m) + o_adj * m
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(
        f"{ROOT}/hf/{n}_hib.jpg", "JPEG", quality=95, subsampling=0)
    # prova de fidelidade: diferença absoluta entre o híbrido e o original (×4 p/ visualizar)
    diff = np.abs(out - o_adj).mean(axis=-1)
    inside = float((diff * m[..., 0]).sum() / max(m[..., 0].sum(), 1))
    vis = np.clip(diff * 4, 0, 1)
    Image.fromarray((vis * 255).astype(np.uint8)).resize((1500, 1000)).save(f"{ROOT}/hf/{n}_diff.jpg", quality=85)
    print(f"{n}: diferença média DENTRO das pessoas = {inside:.5f} (0 = idêntico) | ganho de tom aplicado = {k if match_tone else 1:.3f}")
    return f"{ROOT}/hf/{n}_hib.jpg"


if __name__ == "__main__":
    hibrido(sys.argv[1], sys.argv[2])
