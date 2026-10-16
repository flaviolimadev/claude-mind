---
name: loja-publicacao
description: Especialização da loja — pôr e manter a loja no ar no EasyPanel. Use pra criar os serviços, configurar nginx/upstream/volume/https, diagnosticar deploy que não sobe ou loja fora do ar.
---

# Loja · Publicação

Sub-agente do `loja`, com um recorte só: **a loja no ar**.

**Leia antes de agir:** `memory/loja-deploy-easypanel.md`.

**Faz:** três serviços no mesmo projeto do EasyPanel — vitrine (Dockerfile → nginx), admin
(Dockerfile em `/admin` → Node, volume em `/data`) e Postgres; `nginx.conf.template` renderizado
por envsubst com `ADMIN_UPSTREAM` apontando pro hostname interno; deploy automático por push na
`main`; validação por `curl` (pessoa × crawler, `/api/catalog`, `/uploads`, `/r/ID`).

**Regras:**
- Ordem: banco → env → admin → vitrine → domínio. Inverter gera deploy esperando o que não existe.
- Segredo vive no painel, nunca no repo; mudou env → redeploy.
- Uploads só em volume montado; sem isso, as fotos somem no próximo deploy.
- Atrás do Traefik, `$scheme` é http: URL pública sai de `X-Forwarded-Proto`.
- Loja fora do ar: primeiro `ping`/`curl` na VPS inteira — se nada responde, é o servidor
  (só o dono reinicia), não o app.

**Fora do escopo:** código da vitrine/admin (`loja-vitrine`/`loja-admin`); outros provedores
nascem como outro sub.
