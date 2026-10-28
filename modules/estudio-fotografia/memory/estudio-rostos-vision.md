---
name: estudio-rostos-vision
description: Enquadramento pelo ROSTO com detecção nativa do macOS (Vision via Swift, sem download) + pontuação do rosto principal (tamanho × nitidez × não-cortado × centro); substitui o centróide da máscara rembg, que erra com mãos erguidas
metadata:
  type: decision
---

**Problema (Betfage, 28/out/2026):** "as fotos ficaram mal enquadradas, deveria mostrar o rosto".
O foco pelo centróide da parte alta da máscara rembg cai nas MÃOS erguidas ou no cabelo; e
recortes estreitos (fatias) mostravam orelha/testa. MediaPipe/cv2 precisariam baixar modelos
(permissão), então usamos o que o Mac já tem.

**Solução:**
1. `pipelines/faces_vision.swift` — `VNDetectFaceRectanglesRequest`; `swiftc -O` gera um
   binário; roda nas thumbs 1400px (`./faces_vision analise/*.jpg > faces_raw.tsv`, ~0,3 s/foto)
   → `hf/faces.json` {NNNN: [[x,y,w,h], …]} em frações, origem topo-esquerda.
2. `pipelines/rostos_vision.py` — `rostos(n)` pontua cada caixa: √área × (nitidez FIND_EDGES
   + 2)^0.7 × 0,25 se cortada pela borda × (1 − 0,35·dist. ao centro). **O maior rosto não é o
   principal**: em IMG_0550 era uma senhora desfocada em 1º plano. `alvo(n, "principal"|"todos")`
   devolve o centro do melhor rosto ou da união dos relevantes (≥ 25 % do melhor).
3. Recorte: `recorte(n, w, h, modo, y_rosto)` escala em "cover" e posiciona o alvo em
   (0,5 · w, y_rosto · h) — 0,26–0,36 pra retrato/fatia, 0,45–0,5 pra multidão com mãos erguidas.
   Efeitos centrados (spin blur, anéis de luz, vinheta) usam o mesmo ponto.
4. Fatias estreitas (1:3,75) só com fotos de corpo inteiro/perfil — close-up não cabe.

**Why:** rosto é o que o cliente olha primeiro; um enquadramento automático que corta testa ou
mostra orelha invalida o post inteiro mesmo com efeito bonito.

**How to apply:** rodar o detector logo depois do culling (uma vez por projeto) e usar
`alvo()` em TODO recorte/corte 4:5/9:16, posts e álbum. Ver [[estudio-album-e-cortes]],
[[estudio-efeitos-camada-ia]].
