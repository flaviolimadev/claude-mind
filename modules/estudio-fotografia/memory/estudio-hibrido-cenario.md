---
name: estudio-hibrido-cenario
description: Técnica híbrida (Higgsfield gera só o cenário/luz, pessoas voltam dos pixels originais por máscara rembg) — aprovada e depois DESCARTADA pelo cliente Betfage ("sem IA"); manter como opção, nunca como padrão
metadata:
  type: decision
---

**⚠️ ATUALIZAÇÃO 28/out/2026 (mesmo dia):** depois de "amei" e de 147 plates gerados (~37 cr), o
cliente mandou *"luz natural com fotos reais e ambiente real SEM IA, não modifique a foto em
hipótese alguma"*. O híbrido saiu da entrega; o que foi entregue foi a revelação fiel à câmera
([[estudio-revelar-fiel-camera]]). **Regra nova:** para cliente de igreja/evento que pediu
"natural" alguma vez, a versão 100% real é SEMPRE a entrega-base; o híbrido só se o cliente pedir
explicitamente E só depois de aprovar 3–5 amostras — nunca gerar o lote inteiro antes disso. A
v2 do composite (textura real em alta frequência + 65% da luz IA em baixa frequência, raio 8px)
reduziu a "cara de IA", mas não bastou. Técnica fica documentada abaixo como opção.

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
