---
name: loja-deploy-easypanel
description: Como a loja fica no ar no EasyPanel — três serviços (vitrine nginx, admin Node com volume, Postgres), nginx por template com ADMIN_UPSTREAM interno, https atrás do Traefik, deploy por push, e o que checar quando cai
metadata:
  type: reference
---

**Layout (Chronos Lab, projeto `chronoslab`, 2026-10-15):**
- `catalogo` — vitrine. Source GitHub `main`, build **Dockerfile** da raiz (node:20-alpine
  `npm ci && npm run build` → nginx:1.27-alpine servindo `dist/` na porta 80). `.dockerignore`
  exclui `admin`, `.claude`, `memory`, `scripts`, `viewer`.
- `admin` — painel + API. Mesmo repo, **build path `/admin`**, Dockerfile em `admin/` (compila
  `web/`, roda `server/`), porta 3000, **volume `data` em `/data`** (`UPLOAD_DIR=/data/uploads`),
  env `DATABASE_URL`, `JWT_SECRET`, `ADMIN_USER`/`ADMIN_PASSWORD` (só criam o 1º usuário), `PORT`.
- `catalogo-db` — Postgres interno; URL `postgres://…@<projeto>_catalogo-db:5432/catalogo`.
- Hostnames internos seguem `<projeto>_<serviço>`; domínios gerados
  `<projeto>-<serviço>.<id>.easypanel.host`. Push na `main` dispara rebuild dos dois serviços.

**nginx da vitrine** (`nginx.conf.template`, renderizado pelo `envsubst` da imagem — só nomes
que existem no ambiente são trocados, então `$host`/`$scheme` ficam intactos):
`resolver 127.0.0.11 valid=10s ipv6=off; set $admin ${ADMIN_UPSTREAM}; proxy_pass $admin;` —
a variável evita o nginx morrer na subida se o admin ainda não resolve. Proxy de `/api/catalog`,
`/uploads/`, `/og-image/`, e `/r/` só pra crawler (ver [[loja-previa-link]]). `ENV
ADMIN_UPSTREAM=http://chronoslab_admin:3000` no Dockerfile, sobrescrevível no painel.
`X-Forwarded-Proto` do Traefik repassado por `map` — sem isso a URL pública sai `http`.

**Armadilhas vividas:**
- App escuta em `0.0.0.0` na porta do serviço; `trust proxy` ligado no Express (cookie secure).
- Uploads fora de volume somem no deploy seguinte. Monte antes da primeira foto.
- Binário nativo (`sharp`) precisa do lockfile com o pacote `linuxmusl-x64` pro `npm ci` no alpine.
- Mudança só de env também exige redeploy.
- Sem docker local não há `nginx -t`: o Swarm mantém o container antigo se o novo não sobe —
  validar com `curl` depois do deploy (asset hash novo no HTML = deploy entrou).
- **Painel/VPS inteira fora do ar** (2026-10-16): `ping` 100% de perda em `89.116.74.42` — não é
  o app, é o servidor; só o dono reinicia pela hospedagem. Não gastar tempo em log de aplicação.
- MCP do EasyPanel: respostas truncadas em 20k chars — consultar um projeto (`inspectProject`),
  não listar todos; `search_procedures` aceita `limit` ≤ 5.

Ver [[loja-blueprint]], [[loja-nova-loja-checklist]].
