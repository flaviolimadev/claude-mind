---
name: estudio-culling
description: Culling por nitidez (Laplaciano) + agrupamento de duplicadas por similaridade de thumbs, decisão em contact sheet, rejeitadas movidas (nunca rm)
metadata:
  type: learning
---

- **Nitidez** = variância do Laplaciano (kernel 4-vizinhos) sobre thumb L 192×192. Número bom
  para ranquear DENTRO de um grupo da mesma cena; entre cenas diferentes não compara.
- **Duplicadas**: thumb L 48×48 float; distância RMS com o ÚLTIMO membro do grupo corrente;
  limiar ~0.085 → mesmo grupo. Rajadas de 15–19 cliques idênticos são comuns.
- **Contact sheets** 3×4 (tiles ~420px) rotuladas `numero grupo* nitidez` — a decisão final é
  visual: expressão e história ganham de nitidez em empate; foco no lugar errado e olho fechado
  não aparecem no número.
- **Fotos sem informação não se salvam na edição**: silhueta pura não vira golden hour; flare
  estourado em 16 frames rende no máximo 1–2 "artísticas".
- Rejeitadas → `duplicadas/` levando **JPG e RAW (CR3) juntos**, via `mv`. Deleção permanente é
  do cliente, nunca nossa.

**Why:** 141 fotos viraram 15 escolhidas no caso Ismael sem perder nenhuma cena — e o cliente
pôde auditar a pasta de rejeitadas em vez de confiar cegamente.

**How to apply:** rodar `pipelines/culling.py` (ajustar SRC e faixa numérica), ler as pranchas,
ajustar a seleção do algoritmo com olho editorial, mover rejeitadas. Ver [[estudio-workflow]].
