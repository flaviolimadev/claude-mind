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

**Lote 2 (2026-10-16, 115 quadros, 31 produtos) — o que mudou na receita:**
- Os **RAW ficam no cartão SD** (`/Volumes/Untitled/DCIM/100MSDCF/_DSCnnnn.ARW`); o Drive do dono
  (`CATALOGO_CHRONOSLAB`, 36 pastas) e `~/Downloads/chronoslab/{full,editadas,web}` tinham só JPGs
  escuros, com cast e **deitados** (129 dos 135 quadros têm `flip=5`; o rawpy põe em pé, o JPG não).
  Mapeie JPG→RAW por md5 e revele do RAW; nunca "trate" o JPG.
- Os nomes das pastas do Drive **erram marca/modelo** (Tudor que era Breitling, Tissot e IWC; Speedmaster
  "azul-branco" que era Worldtimer): identificar pela foto, com prancha de zoom × capas do catálogo.
- Mesma luz do lote 1 → os mesmos ganhos (R×1,302 B×1,165) serviram pros 7 cenários (caixa Rolex
  verde, Cartier vermelha, TAG cinza, Omega madeira, fundo roxo). Validar numa prancha de 8 antes do lote.
- **Recorte automático:** densidade de bordas (FIND_EDGES) na imagem reduzida a ~170 px de largura,
  blur gaussiano 10, margens de 6–8% ignoradas, pico = centro; lado = 0,78×min(W,H); ≈ 97% certo.
  Os 3% restantes (dobradiça de caixa, texto do estojo) saem na prancha de revisão → centro manual em
  fração do quadro revelado (`drive/centers_manual.json`) e refaz só esses.
- **Identificar antes de atribuir, com zoom no mostrador** — a miniatura engana: "Santos preto" era o
  Santos-Dumont (sem data, sem AUTOMATIC) e não o Santos de Cartier (data às 6, AUTOMATIC); o
  "Speedmaster dourado" tinha MICHAEL KORS escrito no mostrador. Prancha obrigatória: capa do dono ×
  recorte 1000 px de cada quadro novo, produto por produto, antes de subir.
- **Recorte centralizado com zoom (pedido do dono):** Hough de círculos no quadro revelado reduzido a
  1200 px (raio 11–27% do lado menor, param2 34→28→22), escolhendo o círculo mais perto do pico de
  detalhe; lado = 2r×1,55 (mín. 40% do lado menor), encolhido se preciso pra manter o centro. Acertou
  ~90%; o resto (pulseira dominante, fundo de caixa) lê-se numa prancha com **grade de 0,1** sobre o
  quadro inteiro — estimar fração "no olho" a partir de miniatura em célula com margem erra feio.
  Caixa quadrada (Santos, Panthère) o Hough ainda acha o aro interno; serviu.
- Cache dos quadros revelados em JPEG q94 (`drive/full/`) deixa refazer recortes em segundos sem
  redecodificar o RAW (9 s/quadro).
- `luma = f @ LUMA` em float32 num array 6024×4024 disparou overflow no BLAS do macOS: usar soma
  explícita por canal (corrigido no `revelar_raw.py`).
- Relógio sem cadastro → **rascunho oculto** (`active=false`, preço 0, nota com a origem) com as
  fotos, pro dono só pôr preço/linha/estoque; nunca inventar preço. Fotos antigas do dono ficam no fim.

Ver [[loja-vitrine-conversao]] (zoom), [[loja-previa-link]].
