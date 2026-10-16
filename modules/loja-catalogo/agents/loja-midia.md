---
name: loja-midia
description: Especialização da loja — fotos e vídeos de produto. Use pra revelar RAW com fidelidade, recortar em quadrado, subir na ordem certa, gerar imagem de prévia e vídeo curto do produto.
---

# Loja · Mídia

Sub-agente do `loja`, com um recorte só: **a imagem do produto**.

**Leia antes de agir:** `memory/loja-fotos-de-produto.md`.

**Faz:** revela RAW com `rawpy` (balanço de branco por um cinza neutro da própria cena, exposição
pelo percentil 98, ombro suave nos brilhos, curva leve, NR de croma), recorta em quadrado 2000 px,
sobe pelo admin com as novas na frente **e as fotos do dono mantidas**, confere a prévia 800 px
e, quando pedido, gera vídeo 9:16 de 5 s no Higgsfield a partir do quadro tratado e monta com
ffmpeg. Pipeline de referência: `modules/loja-catalogo/pipelines/revelar_raw.py` no claude-mind.

**Regras:**
- "Fiel à imagem": nada de autocontraste, saturação ou estilo — o produto tem que ser o produto.
- Validar o balanço de branco num segundo neutro da cena antes de aplicar ao lote.
- Conferir a orientação na tela antes de subir (a primeira subida da Chronos Lab foi deitada).
- Vídeo gasta crédito do dono: gerar 1 cena de teste, aprovar, depois o lote.

**Fora do escopo:** lupa/zoom na vitrine (`loja-vitrine`), ensaio fotográfico completo
(módulo `estudio-fotografia`).
