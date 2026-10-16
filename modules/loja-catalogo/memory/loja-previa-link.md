---
name: loja-previa-link
description: Prévia de link no WhatsApp/Instagram sem SSR — nginx manda crawler ao admin (/r/:id com Open Graph, /og-image 800 px via sharp) e pessoa à SPA; atrás do Traefik o protocolo vem de X-Forwarded-Proto
metadata:
  type: reference
---

Crawler de prévia (WhatsApp, Facebook, Instagram, Telegram, X, LinkedIn, Slack, Discord, Google)
**não roda JavaScript**. A vitrine é SPA, então a prévia vem do admin (Chronos Lab, 2026-10-16):

- **Link canônico:** `https://<loja>/r/ID` (o botão Compartilhar gera esse). `/?relogio=ID`
  continua aceito.
- **nginx da vitrine** (`nginx.conf.template`): `map $http_user_agent $is_bot` com a lista de
  crawlers; em `location ^~ /r/`, `if ($is_bot) { proxy_pass $admin; }` senão `try_files
  /index.html`; em `location = /` com `?relogio=N` de crawler, `rewrite ^ /r/$arg_relogio? last`.
  `/og-image/` é sempre proxy pro admin.
- **Admin** `routes/share.js` (montado ANTES de `/api`, público): `GET /r/:id` devolve HTML com
  `og:title` (marca + modelo), `og:description` ("R$ 830 à vista · 10x de R$ 89,99 no cartão sem
  juros · Linha Premium · Pronta entrega em Natal/RN"), `og:image` = `/og-image/ID.jpg`,
  `og:url`, e `meta refresh` pra `/?relogio=ID`. Produto inexistente ou oculto → 404 com OG da home.
  `GET /og-image/:key.jpg` gera **800×800 JPEG q78** com `sharp` (≈50–60 KB — o WhatsApp ignora
  imagem grande), cache em `uploads/og/`, `home` = primeiro banner ou primeiro produto com foto.
- **Armadilha do protocolo:** atrás do Traefik do EasyPanel, dentro do container `$scheme` é
  `http`. O nginx repassa `X-Forwarded-Proto` com `map $http_x_forwarded_proto $fwd_proto {
  default $scheme; }` e o `share.js` monta a base com esse header (default `https`), nunca
  `req.protocol`. Sem isso o OG sai `http://` e a prévia não aparece.
- **Home:** `index.html` leva OG estático com `og:image` apontando pra `/og-image/home.jpg`.

**Validar:** `curl -A "WhatsApp/2.23.20.0" https://<loja>/r/54 | grep og:` (tem que ter `https`)
e sem o UA (tem que vir a SPA). Não dá pra `nginx -t` sem docker local; o Swarm mantém o
container antigo se o novo não subir. Ver [[loja-deploy-easypanel]], [[loja-vitrine-conversao]].
