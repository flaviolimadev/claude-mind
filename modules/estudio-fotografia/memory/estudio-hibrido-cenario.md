---
name: estudio-hibrido-cenario
description: Técnica híbrida aprovada — Higgsfield gera só o cenário/luz (prompt que preserva ambiente), as pessoas voltam dos pixels originais por máscara rembg; rosto idêntico com prova por mapa de diferença
metadata:
  type: decision
---

**Problema:** cliente quer o acabamento cinematográfico das referências (luz dramática, bloom,
atmosfera) mas com rosto E ambiente intocados. Grade local (PIL) foi reprovado 2× ("filtro
horrível"); IA direta na pessoa é proibida ([[estudio-regra-rosto]]).

**Solução (Mocidade Betfage, 28/out/2026, "amei"):** `pipelines/hibrido_cenario_ia.py`
1. Upload da foto natural (2048px) → `gpt_image_2_5`, aspect igual ao da foto, SEM referência de
   estilo, prompt: *"Professional cinematic re-lighting of this exact church photograph. Keep the
   photo EXACTLY as it is: same framing, same people in the same positions and sizes, same
   poses and clothes, and the SAME ENVIRONMENT — same walls, ceiling, lights, air conditioner,
   furniture, flowers… Change ONLY the light and atmosphere: dramatic directional warm light,
   soft bloom, deeper shadows with subtle blue-navy undertone, gentle depth haze… no added
   objects, no text."* (ref de estilo como 2ª imagem muda o ambiente — evitar).
2. Máscara das pessoas por rembg (u2net) na foto original em 2048px → upscale p/ 6000px.
3. Composite: plate IA redimensionado + pessoas = pixels originais (máscara dilatada 9px +
   pena 10px; dentro 100%), só ganho GLOBAL de tom 0,85–1,15 pra casar luz.
4. Prova: mapa |híbrido − original| → preto dentro das pessoas (diff média 0,002–0,02).

**Limites:** pessoas pequenas ao fundo fora da máscara vêm da IA (avisar o cliente; p/ rigor
total, detecção de rosto — MediaPipe precisa baixar modelos). Variante "reluz" (só mapa de luz
low-freq sobre a foto 100% original) gera halo nas bordas — não usar sem ratio edge-aware.
Custo: 0,25 cr/foto; plate sai 1024px (p/ post 1080×1350 basta; 4K = +2 cr).

**Why:** entrega o "resultado final" das referências sem violar a regra do rosto, com prova
objetiva.

**How to apply:** posts/artes de igreja com exigência de fidelidade → fotos naturais →
híbrido → motor de posts com `LOOK="natural"` (o look já está no plate). Ver
[[estudio-regra-rosto]], [[estudio-higgsfield]].
