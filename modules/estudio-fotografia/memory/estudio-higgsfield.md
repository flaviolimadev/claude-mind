---
name: estudio-higgsfield
description: Manual operacional do Higgsfield MCP — fluxo de upload, custos, prompt de fidelidade anti-cara-de-IA, armadilhas (presets interceptando, uploads 000, resposta grande vira arquivo)
metadata:
  type: learning
---

**Fluxo de mídia:** `media_upload` (batch até 20) → `curl PUT` de cada arquivo na upload_url →
`media_confirm` (batch de ids). Armadilhas:
- Resposta grande do `media_upload` vira **arquivo JSON salvo** → scriptar os PUTs em Python
  lendo esse arquivo (nunca copiar URLs na mão para lotes).
- PUTs falham aleatório (`000`/exit 56) → sempre `--retry 3` e re-tentar os que falharem.

**Custos (plano Ultra, out/2026):** edição `gpt_image_2_5` 0,25 cr · upscale 4K bytedance 2 cr ·
i2v `seedance1_5` 4s/1080p 12 cr. `balance` antes de lote; `get_cost:true` para preflight;
relatar gasto na entrega.

**Enhancement fiel (anti "cara de IA")** — o passe que o cliente aprovou:
- Modelo `gpt_image_2_5`, role `image_references`, uma foto por request,
  `generate_image_batch` até 12.
- Prompt: "Subtle professional cinematic enhancement of this exact photograph… The output must
  be the SAME photograph, enhanced — not reimagined, no AI look. Keep absolutely identical:
  people, faces, expressions, poses, clothing, background, framing. Do not add, remove, replace
  or move anything. Only enhance: [luz/atmosfera desejada], deeper shadows with matte film
  blacks, subtle halation, fine analog film grain, gentle vignette."
- Funciona até para transformar céu estourado em pôr do sol ("recovered detail in the bright
  sky") mantendo todo o resto. Citar objetos críticos no prompt (tela do celular, exame impresso).
- Saída é ~688×1024 → **upscale 4K sempre** (job_id direto como image_id; width/height
  obrigatórios). Upscale falha às vezes → re-submeter resolve.

**Armadilha de preset:** `generate_video`/`generate_image` às vezes devolve
`submission_failed` com recomendação de preset — re-submeter com `declined_preset_id` resolve.

**i2v (dar vida à foto):** 1º quadro fiel, rostos DERIVAM com o movimento. Só a pedido
explícito; avisar da deriva; QA frame do meio; "slides animados" NÃO é isso.

**Composições artísticas:** 2 referências (foto + arte/estilo) + prompt descrevendo o que
preservar de cada uma; o modelo preserva silhuetas e padrões de tecido impressionantemente bem.
Não gera música avulsa (sonilo_music é restrito) — vídeo sai mudo.

**Why:** cada item acima custou uma tentativa falha ou um feedback negativo até acertar.

**How to apply:** seguir o fluxo na ordem; nunca pular QA pós-geração. Ver [[estudio-workflow]].
