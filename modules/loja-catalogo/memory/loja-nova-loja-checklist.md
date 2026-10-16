---
name: loja-nova-loja-checklist
description: Ordem de criação de uma loja nova a partir do molde Chronos Lab — perguntas de entrada, renomear o produto pro segmento, settings, seed, fotos, EasyPanel, WhatsApp, prévia de link e os testes finais
metadata:
  type: reference
---

**Antes de escrever código, cinco respostas do dono:** nome da loja · segmento e linhas/qualidades
(ex.: Premium/ETA/Super Clone) · WhatsApp com DDI+DDD (só dígitos) · cidades de pronta entrega ·
lista de produtos com preço à vista, no cartão e custo (+ fotos). Sem isso, não há loja.

**Ordem (cada passo tem dono):**
1. `loja` — clonar o molde (repo `flaviolimadev/chronoslab-loja`), renomear pacote/título/OG
   da home (`index.html`), trocar `src/data/store.json` e `admin/server/seed/store.json`.
2. `loja-admin` — adaptar o produto ao segmento: colunas em `admin/server/src/db.js`, parse em
   `routes/watches.js`, `watch-query.js` (público × privado), `admin/web/src/pages/WatchForm.jsx`
   e `Watches.jsx`; `meta.js` devolve os valores distintos pros filtros e pro cadastro rápido.
3. `loja-vitrine` — `src/lib/catalog.js` (filtros, cores conhecidas, ordenação),
   `WatchCard.jsx`/`ProductSheet.jsx` (quais atributos mostrar), `whatsapp.js` (texto da mensagem),
   `design-system.css` (cor da marca). Conferir em 375 px.
4. `loja-dados` — importar o catálogo pela API (não por SQL), com fotos; log do lote.
5. `loja-midia` — fotos quadradas 2000 px fiéis; primeira foto é a capa e a prévia de link.
6. `loja-publicacao` — EasyPanel: Postgres → env do admin → admin (`/admin`, volume `/data`) →
   vitrine (`ADMIN_UPSTREAM=http://<projeto>_<admin>:3000`) → domínio. Push na `main` = deploy.
7. `loja-vitrine` — testar a prévia: `curl -A WhatsApp/2.23.20.0 https://<loja>/r/1` tem que
   devolver OG com `https://`; sem o UA, a SPA.
8. `loja` — teste de ponta a ponta no celular: filtrar, abrir produto, zoom, sacola → WhatsApp
   abre com a mensagem certa e o número certo. Só então "está no ar".

**Depois do ar:** `npx @flaviolimadev/claude-mind .` + `… add loja-catalogo` no projeto novo, e
uma memória `<<loja>>-loja.md` com URLs, serviços e o que o dono decidiu (modelo:
[[loja-caso-chronoslab]]). Ver [[loja-blueprint]].
