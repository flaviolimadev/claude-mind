---
name: estudio-album-e-cortes
description: Receita do álbum PDF temático (capa com nome, fundos aquarela, duplas inclinadas, seção escura, corações vetoriais) e dos cortes 4:5/9:16 com proteção de rosto
metadata:
  type: learning
---

**Álbum PDF** (PIL `save_all`, páginas 2232×3157 ≈ A4 270dpi, `pipelines/album_pdf.py`):
- **Capa**: foto-arte full-bleed + faixa de gradiente escuro embaixo + nome do projeto em
  Georgia Italic dourado com sombra deslocada + subtítulo.
- **Fundo liso = "básico"** (feedback literal do cliente). Fundo temático: a própria foto da
  seção em cover 1/3-res, blur 70, blend 14–34% com papel creme + vinheta + grão de papel +
  moldura dourada dupla + coração vetorial no topo.
- **Duplas**: fotos inclinadas ±2,4° com borda branca e sombra desfocada, dispostas em
  diagonal, coração dourado entre elas, legenda com filetes laterais.
- **Seção dramática** (silhuetas/P&B) em páginas ESCURAS (base ~(24,20,18), tinta creme).
- Estrutura: capa → folha de rosto → [divisória + páginas]×N seções → contracapa assinada com
  data. Legendas afetivas curtas ("oi, <nome>", "primeiro beijo").
- QA por previews JPG das páginas-chave (reexecutar o script com bloco de preview).
- ♥ de fonte vira tofu — coração é SEMPRE vetorial.

**Cortes sociais** (`pipelines/crop_posts.py`): 4:5 mantém largura e corta altura; 9:16 mantém
altura e corta largura. Automático (centro no facho de luz) funciona para lote; para seleção
final, janela POR FOTO em dict manual. Regras: nunca cortar >5% do topo (cabeças!); close com
mãos na barriga embaixo → cortar só do topo é erro, equilibrar; gerar cortes A PARTIR da versão
editada final (regenerar quando a edição mudar).

**Álbum final**: pasta `album_final/` com numeração narrativa + rótulo
(`08_beijo-barriga.png`) — vídeos e PDF leem dela, uma fonte só.

**Why:** a v1 de fundo liso foi rejeitada; a v2 temática foi aprovada no mesmo dia.

**How to apply:** adaptar nomes/sequência de seções ao projeto; capa usa a arte-herói do
projeto. Ver [[estudio-workflow]], [[estudio-caso-ismael]].
