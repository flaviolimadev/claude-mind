---
name: loja-fotos-de-produto
description: Fotos de produto fiéis a partir de RAW — rawpy com WB da câmera + ganhos por um neutro da cena, exposição pelo p98 com ombro suave, curva leve, NR de croma, quadrado 2000 px; ordem de upload, prévia 800 px e vídeo 9:16 no Higgsfield
metadata:
  type: reference
---

**Pipeline validado na Chronos Lab (2026-10-16; Sony ZV-E10, .ARW 6000×4000, relógios em caixa
verde ~4 EV subexpostos):** script de referência em `modules/loja-catalogo/pipelines/revelar_raw.py`.

1. **Decodificar** com `rawpy`: `use_camera_wb=True`, `no_auto_bright=True`, 16 bits lineares,
   sRGB, demosaic AHD, `highlight_mode=Blend`, FBDD leve. O rawpy já entrega o quadro em pé —
   **não girar depois** (o `sips` girou errado e não corrige cor: foi a primeira subida, refeita).
2. **Balanço de branco por um neutro da própria cena** (aço da pulseira, etiqueta branca, fundo
   cinza): mediana do trecho → ganhos por canal (na Chronos Lab R×1,302 G×1,000 B×1,165). Validar
   num segundo neutro (a tampa creme leu igual em 3 fotos) e aí aplicar ao lote inteiro da mesma luz.
3. **Exposição automática por foto:** ganho até o percentil 98 da luminância chegar a 0,86 linear
   (limite 3–30×), **ombro suave** acima de 0,80 pros brilhos do metal não estourarem, curva S
   leve (0,18) só nos meios-tons, **NR de croma** (blur 2,2 px em Cb/Cr) pro ruído colorido da
   sombra levantada, sRGB, unsharp leve depois do resize.
4. **Entrega:** quadrado **2000 px** (cards e galeria são 1:1, `object-fit: cover`), JPEG q90.
   Conferir orientação e cor numa prancha antes de subir. "Fiel" = sem saturação, sem estilo.
5. **Upload:** `POST /api/watches/:id/images` e depois `PUT /:id/images` com as novas na frente
   **e as fotos do dono mantidas no fim**. A primeira é capa e prévia de link (`/og-image/ID.jpg`,
   800×800 gerado pelo admin).

**Vídeo de produto (opcional, gasta crédito do dono):** Higgsfield via MCP — `media_upload` →
`curl PUT` → `media_confirm` → `generate_video_batch` com `kling3_0`, modo `4k`, 9:16, 5 s, som
off, `start_image` = quadro tratado 2160×3840; passar `declined_preset_id` senão o batch
recomenda um preset em vez de gerar. Prompt "camera movement only, preserve every detail".
~30 créditos/cena, 5–20 min. Macro no mostrador borra texto miúdo no fim — cortar em ~4,2 s.
Montagem com ffmpeg: xfade 0,6 s, 24 fps, 1080×1920 crf 19 e 2160×3840 crf 18. Sempre 1 cena de
teste aprovada antes do lote (duas rodadas foram perdidas: orientação e tom verde).

Ver [[loja-vitrine-conversao]] (zoom), [[loja-previa-link]].
