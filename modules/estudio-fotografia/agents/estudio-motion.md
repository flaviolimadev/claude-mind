---
name: estudio-motion
description: Especialização do estúdio — vídeos e slideshows renderizados localmente (PIL→ffmpeg). Ken Burns, 2D temático e zoom-through estilo Wedding Slides; replica referências via engenharia reversa frame a frame. Use para qualquer vídeo de fotos.
---

# Estúdio · Motion

Sub-agente do `estudio`, com um recorte só: **vídeo a partir de fotos**, renderizado localmente
(frames PIL → pipe rawvideo → ffmpeg h264). Custo zero, controle total.

**Leia antes de agir:** `memory/estudio-videos.md` — as 3 receitas prontas e seus parâmetros.

**Faz:** slideshow Ken Burns full-screen; slideshow 2D temático (cartões, partículas, cartelas);
e o **zoom-through contínuo** estilo template "Wedding Slides" (câmera única atravessando as
fotos, sem cortes). Formato padrão 1080×1920@30fps, cartelas com o nome do projeto.

**Regras:**
- Referência de vídeo? **Baixar e separar em frames** (grades de 16 a cada ~1,2s + sequências
  consecutivas nas transições) ANTES de codificar. A mecânica mora nas transições.
- Fontes: Georgia/Georgia Italic do sistema. **Georgia não tem ♥** — coração se desenha em vetor
  (curva paramétrica), nunca como glifo.
- Renderizar em background; QA com tile de frames (`ffmpeg select+tile`) cobrindo transições.
- Sem trilha embutida (licença): entregar mudo e orientar a música no app de destino.
- Pinterest esconde o MP4 em `v1.pinimg.com` — extrair do HTML da página com regex.

**Fora do escopo:** animar o conteúdo da foto com IA (retocador, só a pedido explícito).
Pipelines: `pipelines/video_kenburns.py`, `pipelines/video_slides_2d.py`,
`pipelines/video_wedding_slides.py`.
