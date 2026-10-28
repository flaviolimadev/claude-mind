---
name: estudio-workflow
description: O fluxo mestre de um projeto de fotos — entrada (fotos+título+referências), as 6 etapas na ordem, estrutura de pastas e regras de entrega
metadata:
  type: project
---

**Entrada de todo projeto:** o cliente manda (1) a pasta de fotos da câmera, (2) o título/tema
(ex.: nome do bebê, do casal), (3) referências visuais do resultado. Nada de começar sem os três.

**As 6 etapas, SEMPRE nesta ordem:**
1. **Referências** → abrir cada uma e traduzir em termos técnicos (paleta, contraste, textura,
   elementos, movimento). Vídeo de referência: baixar e fatiar em frames do início ao fim.
2. **Culling** (`estudio-curador`) → melhores por cena; rejeitadas em `duplicadas/` (JPG+RAW).
3. **Cor** (`estudio-colorista`) → correção natural PRIMEIRO, grade estilizado DEPOIS. Com
   RAW+JPG da câmera, a base é a revelação fiel à câmera ([[estudio-revelar-fiel-camera]]):
   a conversão do macOS sai escura/lavada — casar com o JPG da câmera antes de qualquer gosto.
4. **IA** (`estudio-retocador`) → passe de fidelidade Higgsfield + upscale 4K (checar créditos).
   **CONDICIONAL:** se o cliente exigir "rosto intocado" ([[estudio-regra-rosto]]), pular esta
   etapa para fotos com pessoas — efeitos só locais (PIL): grade, grão, blur em máscara fora do
   sujeito, recorte por segmentação (rembg), colagem e tipografia.
5. **Diagramação** (`estudio-diagramador`) → `album_final/` numerado, PDF, cortes 4:5/9:16.
6. **Motion** (`estudio-motion`) → vídeo(s) replicando a referência.

**Estrutura de pastas do projeto:**
`raiz/` originais · `duplicadas/` rejeitadas · `editadas/` versões de trabalho com sufixo
(`_cor`, `_cine`, `_hf4k`, `_pb`, `_sepia`) · `editadas/posts/feed_4x5|stories_9x16/` cortes ·
`album_final/` numerado narrativo + PDF + vídeos.

**Why:** foi a ordem que produziu o resultado aprovado no caso Ismael; pular a correção de cor ou
a leitura de referência gerou retrabalho TODAS as vezes.

**How to apply:** ao receber um projeto, criar a estrutura, ler [[estudio-caso-ismael]] como
régua de qualidade, e despachar cada etapa pro sub dono. Entregar parciais cedo (SendUserFile) e
transformar todo feedback em memória. Ver [[estudio-culling]], [[estudio-cor-e-grade]],
[[estudio-higgsfield]], [[estudio-album-e-cortes]], [[estudio-videos]].
