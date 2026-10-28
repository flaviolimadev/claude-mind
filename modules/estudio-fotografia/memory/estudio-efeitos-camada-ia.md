---
name: estudio-efeitos-camada-ia
description: Como usar IA para "efeito" sem tocar na foto — Higgsfield gera só CAMADAS (anéis de luz/prisma, poeira, feixe, névoa) em fundo preto, aplicadas por screen; grade global + spin blur fora do rosto; paleta do cliente nos fundos; textura do logo oficial
metadata:
  type: decision
---

**Pedido (Betfage, 28/out/2026):** "fazer esse estilo de edição [4 refs: low-key quente, duotone
azul, spin blur, anéis de prisma] usando Higgsfield, sem alterar o cenário ou as pessoas, apenas
o efeito usando a foto original" — logo depois de ter proibido IA na foto ([[estudio-regra-rosto]]).

**Solução — `pipelines/efeitos_camada_ia.py`:**
- Foto = pixels da entrega. IA entra SÓ como camada: `gpt_image_2_5` 2:3, prompt "… on a PURE
  BLACK background … nothing else: no objects, no people, no text" → anéis concêntricos âmbar
  com prisma, círculos de luz, anel fino de prisma, poeira/bokeh, feixe volumétrico, névoa.
  0,25 cr cada; 6 camadas cobrem um projeto inteiro. Antes do screen: tirar nível de preto
  `(a − 0,06)/0,94`; o anel "vetorial" fica crível com GaussianBlur 10 + opacidade 0,7.
- Estilos: **low-key quente** (gamma 1,3, pretos −0,025, S 0,14, sat 0,8, quente leve, bloom
  0,18, poeira 0,2 + feixe 0,13, vinheta 0,58) · **spin blur** (média de 26 rotações ±7° em 1600px
  com pad reflect, centro = rosto nítido via `mask_radial` 0,16→0,5) · **anéis de prisma** (spin
  ±3° leve, matte 0,035, sat 0,88, anel centrado no rosto, bloom 0,12).
- **Duotone frio foi reprovado** ("o efeito azul ficou feio, exclua") — manter quente/P&B.
- Saída 4:5 3200×4000 centrada no rosto ([[estudio-rostos-vision]]).

**Posts a partir de referências (`pipelines/posts_refs_paleta.py`, 7 layouts):** cards
inclinados, grade 6 em papel, 3 fatias verticais, cúpula (pieslice) + recorte, 3 fatias
arredondadas, 3 bandas P&B, colagem fundida com elipses + zoom blur + moldura clara. Lições:
(1) a referência dá COMPOSIÇÃO/EFEITO; a COR vem da paleta oficial do cliente (hex dos arquivos
dele — "algumas ficaram com tons verde" = reprovado); (2) a arte/logo oficial entra como
TEXTURA esmaecida (screen 0,2 da arte sem o fundo; leão em alpha como marca-d'água lavanda);
(3) recorte rembg pega todo mundo — cortar a caixa pra isolar uma pessoa; (4) elipse de fusão
tem que ficar dentro do retângulo colado senão funde com preto.

**Why:** entrega o "look" das referências e o uso do Higgsfield que o cliente pediu, com a foto
100 % intacta — a IA vira textura, não retoque.

**How to apply:** cliente "sem IA na foto" + refs com efeito → camadas em fundo preto + grade
global + efeitos fora do rosto; sempre na paleta dele. Ver [[estudio-hibrido-cenario]] (o que
NÃO fazer), [[estudio-revelar-fiel-camera]].
