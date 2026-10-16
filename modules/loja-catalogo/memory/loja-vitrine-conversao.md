---
name: loja-vitrine-conversao
description: O pacote de conversão da vitrine e as regras de UX que ficaram — última unidade sem expor estoque, economia à vista, botão fixo com preço, banners com destino interno, zoom/lupa, URL limpa ao fechar
metadata:
  type: feedback
---

O dono escolheu, entre várias ideias, o **pacote de conversão** (Chronos Lab, 2026-10-16). O que
entrou e as regras que valem pra toda loja:

- **Última unidade:** a API pública manda `lastUnit` (estoque = 1) e `soldOut`, **nunca a
  quantidade**. Etiqueta só quando `lastUnit && !soldOut`. Em loja de peça única quase tudo é
  "última" — é verdade, e funciona.
- **Economize R$ X à vista:** `cardPrice − price`, arredondado; aparece no card e na página.
  Sem `cardPrice` maior que `price`, não aparece (nada de desconto inventado).
- **Botão fixo "Pedir no WhatsApp"** na página do produto (`position: sticky`) com duas linhas:
  ação em cima, "R$ 830 à vista · 10x de R$ 89,99" embaixo. Um botão só, nada de barra extra.
- **Banners com destino:** campo `title` vira a pílula "… →"; `link` começando com `?` é roteado
  dentro da loja (`?marca=`, `?promo=true`, `?pronta=true`, `?relogio=ID`, `?q=`); link externo
  abre em nova aba. Banner pra `?promo=true` sem promoção cadastrada leva a lista vazia — avisar.
- **Fotos:** lupa no desktop (lente 180 px, 2,6×) e visualizador em tela cheia no celular
  (pinch, duplo toque, swipe, miniaturas), aberto com `pushState` pra o gesto de voltar fechar
  só o zoom; `Escape` tratado em fase de captura com `stopPropagation` pra não fechar o produto.
- **URL limpa:** fechar o produto por qualquer caminho (X, Esc, voltar) faz `history.replaceState`
  pra `/` — senão o link `/r/54` fica preso na barra.
- **Promoção** só existe com `oldPrice`; **Novo** com `isNew`; **Esgotado** troca o botão por
  "Avise-me".

**Why:** cada elemento tem um dado real por trás; etiqueta sem dado vira ruído e mina a confiança
na loja.

**How to apply:** ao adicionar qualquer chamada nova, pergunte "qual campo sustenta isso?". Ver
[[loja-previa-link]] (compartilhar), [[loja-blueprint]].
