---
name: loja-pixel-trafego
description: Pixel de rastreamento (Meta/Google) na vitrine Vite para rodar tráfego/anúncios — o script vai no <head> do index.html, mas o <noscript><img> tem que ir no <body> (Vite/parse5 recusa img dentro de noscript no head)
metadata:
  type: reference
---

Pra começar a fazer tráfego (anúncios Meta/Google), o pixel vai no `index.html` da vitrine — ele é
estático e carrega em toda página, antes do React. Validado na Chronos Lab (2026-10-20).

- **Meta Pixel:** o `<script>` do `fbq('init', ID); fbq('track','PageView')` vai no `<head>`. O
  `<noscript><img ...facebook.com/tr...>` **tem que ir no `<body>`**, não no head: o build do Vite
  (parse5) quebra com `disallowed-content-in-noscript-in-head` porque `<img>` não é conteúdo válido
  de `<noscript>` dentro do `<head>`. Como a loja é SPA (só funciona com JS), o noscript é quase
  inútil aqui, mas mantê-lo no body é o certo.
- **Conferir no ar:** no console, `typeof fbq === 'function'`, `fbq.version`, e um beacon pra
  `facebook.com/tr?...ev=PageView` na aba Network. `connect.facebook.net/en_US/fbevents.js` carrega.
- **Eventos de conversão (feito na Chronos Lab, 2026-10-20):** numa SPA, dispare `fbq('track', ...)`
  nas ações, ANTES de abrir o `wa.me`. Mapa usado: **ViewContent** ao abrir o produto (`openProduct`),
  **AddToCart** ao guardar na sacola (`toggleBag`, só ao adicionar), **InitiateCheckout** ao enviar a
  sacola no WhatsApp, **Contact** ao "Pedir no WhatsApp"/perguntar/geral, **Lead** ao agendar visita
  e no "Avise-me". Helper `track(ev, params)` com `try/catch` e `typeof window.fbq === 'function'` —
  **no-op seguro** se o pixel estiver bloqueado/ausente. Params: `content_type:'product'`,
  `content_ids` (array de **string**), `content_name`, `value` (número), `currency:'BRL'`; na sacola,
  somar o `value` e passar `num_items`. O `wa()` recebe um `ev` opcional e dispara antes de abrir o chat.
- **Google Analytics/Ads** seguem o mesmo padrão (gtag no head). Um pixel por rede; ID é do dono.

Ver [[loja-vitrine-conversao]], [[loja-caso-chronoslab]].
