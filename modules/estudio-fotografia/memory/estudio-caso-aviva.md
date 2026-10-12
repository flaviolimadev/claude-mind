---
name: estudio-caso-aviva
description: Caso 2 do estúdio (out/2026) — aniversário do conjunto de senhoras, 296 RAWs Sony → 171 editadas cine + 5 artes + 10 posts de colagem; receitas de igreja em luz baixa e Drive em lote
metadata:
  type: decision
---

Projeto 2 (12/out/2026), pasta `~/Downloads/aviva-senhoras/`. Culto de aniversário do conjunto
de senhoras (Assembleia de Deus). Tema: **AVIVA, SENHOR, A TUA OBRA — Hc 3:2**. Paleta derivada
das ROUPAS (bege/marrom/bordô) — o cliente corrigiu a paleta inicial (azul) ao ver as fotos:
**sempre confirmar a paleta contra o figurino real antes de desenhar**.

**Números:** 296 RAWs Sony .ARW em 2 lotes (116 + 192, com 12 repostas) → sips converte ARW
nativamente no macOS (6000×4000) → 125 duplicatas exatas fora (limiar 0.035 preserva variações
de pose) → 171 editadas. Grades: `aviva_grade.py` (natural) e `aviva_cine.py` (âmbar cinema,
aprovado). Higgsfield fidelidade nas 60 do lote 1 + 4K em 12 heroínas (~39 cr).

**Entregas:** `AVIVA_ENTREGA_FINAL/` (171 cine + 4K/ + posts/ + artes/, 1,4GB) · 5 artes das
refs do briefing · **10 posts de colagem** (ESTUDOS.md → `pipelines/posts_colagens.py`).

**Lições novas (além do caso Ismael):**
- **Igreja luz baixa**: exposição automática por mediana central (alvo 0.33–0.36, clamp ≤2.8)
  ANTES de tudo; pele de todos os tons protegida; duotone de cor só em FUNDOS de arte.
- **Google Drive em lote**: gdown bloqueia após ~40 arquivos anônimos ("many accesses") — o
  caminho é o cliente baixar ZIPs (vêm em MÚLTIPLAS partes -001/-002/-003; conferir se a soma
  bate com a listagem do embeddedfolderview, que dá os 116+ nomes/ids via regex em `entry-ID`).
- **Estudo de referência vira arquivo** (`ESTUDOS.md`): 1 bloco por ref com elementos→adaptação
  à paleta→status; refs redundantes são "absorvidas" e documentadas.
- Receitas de colagem reutilizáveis em `posts_colagens.py`: halftone por círculos, letras-
  máscara, palavras sobre emendas de faixas, janelas de arquivo com nomes REAIS dos RAWs,
  mosaico de tiles deslocados, xadrez veludo+palavras, moldura de seleção de editor, streaks
  dourados sobre P&B, zoom-blur como moldura, fatias verticais com véu.

**Why:** segundo caso confirma o fluxo do estúdio e adiciona o vertical "igreja/eventos".

**How to apply:** projeto de culto novo → [[estudio-workflow]] + estas receitas; posts a partir
de referências → ESTUDOS.md primeiro, engine depois. Ver [[estudio-caso-ismael]],
[[estudio-higgsfield]].
