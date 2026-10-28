---
name: estudio-revelar-fiel-camera
description: Revelação "sem IA, sem filtro" — a conversão CR3→JPEG do macOS sai mais escura/lavada que o JPG da Canon; casar a full-res com o JPG da câmera por histogram-matching global por canal devolve tom e cor reais em 6000px
metadata:
  type: decision
---

**Problema (Mocidade Betfage, 28/out/2026):** cliente exige "fotos reais, luz natural, ambiente
real, sem IA, não modifique a foto". A revelação por alvo fixo (mediana 0,42 com trava de p99)
deixou as cenas de luz baixa MAIS ESCURAS que o JPG que a própria câmera gravou (ex.: câmera
0,37 × nossa 0,19), porque `sips` renderiza o CR3 escuro/plano e a trava de highlight (luzes
do palco) impede o ganho.

**Solução — `pipelines/revelar_fiel_camera.py`:**
1. Fonte full-res = CR3 convertido (`full/NNNN.jpg`, 6000×4000). Referência = JPG da câmera
   (`IMG_NNNN.JPG`, 2400px) — é a renderização que o fotógrafo viu e aprovou no visor.
2. Histogram-matching GLOBAL por canal RGB (LUT 256, monotônica) da conversão → câmera, calculado
   em 600×400. Devolve tom + cor da Canon (pele, brancos da parede) na resolução cheia.
3. Acabamento mínimo: se mediana < 0,22 (culto com luz baixa), ganho ≤1,25 com ombro em 0,80
   (nada estoura); preto assentado 0,006. Nada local, nada generativo.
4. QA: mediana nova ≈ mediana da câmera (±0,02) em claras E escuras; zoom 1:1 do rosto mostra mais
   detalhe que o JPG 2400px, sem banding.

**Why:** "não modifique a foto" + "mais natural" = a régua é a própria câmera, não um alvo
numérico. O cliente não quer o nosso gosto; quer a foto dele, limpa e em alta resolução.

**How to apply:** em todo projeto com RAW+JPG da câmera, rodar isto como revelação-base ANTES de
qualquer estilo. Se o cliente pediu "natural/real" uma vez, esta é a entrega — grade, grão e
vinheta só dentro dos posts, se pedir. Ver [[estudio-regra-rosto]], [[estudio-cor-e-grade]],
[[estudio-hibrido-cenario]] (o que NÃO entregar).
