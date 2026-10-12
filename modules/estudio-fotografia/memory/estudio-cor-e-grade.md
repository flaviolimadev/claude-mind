---
name: estudio-cor-e-grade
description: Correção SEMPRE antes do grade; film look profissional = textura (grão, matte, halation, clarity); paleta do grade nasce do figurino
metadata:
  type: feedback
---

- **Correção antes do grade — sem exceção.** Grade dourado aplicado direto no arquivo da câmera
  rendeu "amarelão" e reclamação do cliente; refeito como correção→grade ficou aprovado.
  Correção: WB gray-world nos meios-tons (25–75%) amortecido 55% e clampado [0.9, 1.12], joelho
  nas altas (>0.80, -35%), abertura de sombras (+3.5% abaixo de 0.30), curva S leve, vibrance
  que satura só o que está apagado protegendo pele.
- **"Edição limpa" = amadora** (feedback literal: "muito simples, sem nada de interessante").
  O look profissional é TEXTURA em camadas: curva fílmica com pretos matte TINGIDOS (nunca preto
  puro), 3-way grading, clarity em 2 raios (50px e 3px), halation quente nas altas, grão gerado
  em 1/3 da resolução (orgânico, não ruído fino), vinheta.
- **Paleta casada com o figurino** (pedido do cliente): o grade ecoa a roupa. Marinho+creme →
  sombras índigo `matte=[0.050,0.056,0.078]`, altas creme, azuis enriquecidos (+22% sat em
  h≈0.615). Vestido verde-menta → verdes PRESERVADOS/avivados (+6%), nunca o olive-escuro padrão.
- Tons de pele: proteger sempre (faixa h≈0.065±0.055 ganha saturação quando o resto perde).
- P&B filmico: mix de canais 45R/40G/15B (pele luminosa), matte 3%, curva S.

**Why:** foi a diferença entre "refaz" e "perfeito" no mesmo conjunto de fotos.

**How to apply:** `pipelines/correcao_cores.py` para o natural; `pipelines/grade_cine.py` para o
film look — SEMPRE revisar o bloco de verdes/azuis contra o figurino do projeto antes de rodar.
Testar em 3–4 fotos, prancha, depois o lote. Ver [[estudio-workflow]], [[estudio-caso-ismael]].
