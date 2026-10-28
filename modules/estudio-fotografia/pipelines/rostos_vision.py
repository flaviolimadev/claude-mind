#!/usr/bin/env python3
"""Rostos detectados pelo Vision (hf/faces.json, gerado por faces_vision.swift nas thumbs de
analise/) + pontuação para escolher o rosto PRINCIPAL de cada foto.
Pontuação = tamanho × nitidez (FIND_EDGES na caixa) × não-cortado pela borda × perto do centro.
(O maior rosto pode ser um desfocado de 1º plano — ex.: IMG_0550.)"""
import json
import math
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.expanduser("<PROJETO>")
FACES = json.load(open(os.path.join(ROOT, "hf", "faces.json")))
_SCORE = {}


def _nitidez(thumb, b):
    w, h = thumb.size
    x0, y0 = int(max(b[0], 0) * w), int(max(b[1], 0) * h)
    x1, y1 = int(min(b[0] + b[2], 1) * w), int(min(b[1] + b[3], 1) * h)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return 0.0
    c = thumb.crop((x0, y0, x1, y1)).convert("L")
    c = c.resize((96, int(96 * c.height / c.width) + 1))
    return float(np.asarray(c.filter(ImageFilter.FIND_EDGES), np.float32).std())


def rostos(n, min_rel=0.25):
    """[(score, [x,y,w,h])] ordenado do melhor pro pior; só os ≥ min_rel do melhor."""
    if n in _SCORE:
        return _SCORE[n]
    bs = FACES.get(n, [])
    if not bs:
        _SCORE[n] = []
        return []
    thumb = Image.open(os.path.join(ROOT, "analise", f"{n}.jpg"))
    pts = []
    for b in bs:
        x, y, w, h = b
        cortado = x < 0.005 or y < 0.005 or x + w > 0.995 or y + h > 0.995
        nit = _nitidez(thumb, b)
        dc = math.hypot(x + w / 2 - 0.5, y + h / 2 - 0.45)
        s = math.sqrt(w * h) * (nit + 2) ** 0.7 * (0.25 if cortado else 1.0) * (1 - 0.35 * dc)
        pts.append((s, b))
    pts.sort(key=lambda t: -t[0])
    best = pts[0][0]
    _SCORE[n] = [p for p in pts if p[0] >= best * min_rel]
    return _SCORE[n]


def alvo(n, modo="principal"):
    """(fx, fy) em frações da foto: rosto principal ou centro da união dos rostos relevantes.
    None se a foto não tem rosto detectado (quem chama decide o fallback)."""
    bs = [b for _, b in rostos(n)]
    if not bs:
        return None
    if modo == "principal":
        b = bs[0]
        return b[0] + b[2] / 2, b[1] + b[3] / 2
    x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
    x1, y1 = max(b[0] + b[2] for b in bs), max(b[1] + b[3] for b in bs)
    return (x0 + x1) / 2, (y0 + y1) / 2
