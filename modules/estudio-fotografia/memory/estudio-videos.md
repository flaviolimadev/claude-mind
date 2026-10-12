---
name: estudio-videos
description: As 3 receitas de vídeo locais (PIL→ffmpeg) — Ken Burns, 2D temático e zoom-through Wedding Slides — com parâmetros calibrados e o método de engenharia reversa de referência
metadata:
  type: learning
---

**Infra comum:** frames numpy → pipe rawvideo rgb24 → ffmpeg libx264 crf18 yuv420p 1080×1920@30.
ffmpeg do usuário em `~/.local/bin/ffmpeg`. Render em background; QA com
`-vf "select='eq(n\,X)+…',tile=Nx1"`. Georgia/Georgia Italic do sistema; **Georgia não tem ♥**
(desenhar coração via curva paramétrica `16sin³t / 13cost-5cos2t-2cos3t-cos4t`). Sem música
embutida (licença) — entregar mudo.

**Método para replicar referência de vídeo (ordem obrigatória):**
1. Pinterest esconde o MP4: extrair `v1.pinimg.com/videos/.../*.mp4` do HTML via regex no
   browser (login-wall não bloqueia o CDN). 2. Baixar. 3. Fatiar: grade 4×4 a cada ~1,2s do
   início ao fim + frames CONSECUTIVOS da transição. 4. A mecânica mora NA TRANSIÇÃO — descrever
   antes de codificar. 5. Calibrar com tiles comparando com a referência.

**Receita 1 — Ken Burns simples** (`video_kenburns.py`): 2,7s/foto, zoom 1.09 alternando
in/out, pan aleatório suave, crossfade 0,6s por buffer de cauda, cartelas com fade.

**Receita 2 — 2D temático** (`video_slides_2d.py`): fundo papel+moldura dourada (match do
álbum), cartões polaroid entrando com rotação que assenta (ease-out 0,55s), partículas douradas,
divisórias de capítulo, seção escura. Para quando o cliente quer "a cara do álbum em vídeo".

**Receita 3 — zoom-through "Wedding Slides"** (`video_wedding_slides.py`) — a profissional:
- SEM cortes: câmera única em push contínuo. Foto nasce pequena, cresce, câmera a ATRAVESSA
  (estoura o quadro, desfoca, dissolve em clarão rosê) e a próxima já está nascendo atrás.
- Push exponencial `s = S0·e^(K·t)` com S0=0.40, S1=2.65 (velocidade de câmera constante).
- Pass-through: blur progressivo a partir de s=1.35 (3 níveis pré-renderizados 0/7/22 blended),
  fade de s=1.85→2.65, flash radial rosê gaussiano (σ=0.26s, pico 0.9) no limite entre fotos;
  próxima foto entra em tn>0.70 com s≈0.34→0.40 (continuidade com o S0 do slide seguinte).
- Texto ancorado NA CENA: label pré-renderizado ("NOME" caps espaçado + linha + capítulo)
  escala junto com o cartão, alternando lado; clamp nas bordas.
- Fundo = a própria foto em cover ultra-blur 42% + lavagem blush; fios de brilho verticais com
  ponta luminosa caindo; bokeh grande; light leak respirando.
- Calibração que errei primeiro: fade cedo demais deixa "buraco" entre fotos — a foto grande
  deve PREENCHER o quadro antes de sumir.

**Why:** a receita 3 foi comparada frame a frame com o template comercial e aprovada.

**How to apply:** escolher a receita pela referência do cliente; adaptar D (2,9s) ao número de
fotos vs duração-alvo. Ver [[estudio-workflow]], [[estudio-higgsfield]] (i2v NÃO é slideshow).
