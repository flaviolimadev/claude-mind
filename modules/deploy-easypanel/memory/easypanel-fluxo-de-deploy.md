---
name: easypanel-fluxo-de-deploy
description: Fluxo de deploy no EasyPanel — banco primeiro, app via GitHub (Nixpacks ou Dockerfile), env, domínio por último; monorepo exige caminho de build explícito
metadata:
  type: reference
---

**Ordem que evita retrabalho:** (1) serviço de **banco** → (2) **env vars** do app → (3) **app**
conectado ao GitHub → (4) **domínio/SSL**. Inverter essa ordem gera deploy quebrado esperando
coisa que ainda não existe.

- **Build:** o Nixpacks detecta o stack sozinho (Node, PHP, estáticos…). Passe a um `Dockerfile`
  explícito quando precisar de controle — extensão de PHP, build multi-stage, binário extra.
- **Monorepo/subpasta:** configure o caminho de build do serviço e garanta que `nixpacks.toml`,
  `Dockerfile` e `.dockerignore` apontem pro subprojeto certo. Senão o build roda da raiz do
  repositório: falha ou carrega o resto junto (armadilha vivida num monorepo real — custou um
  ciclo de deploys até o caminho `metabox/ryepecripto` ficar explícito nos três arquivos).
- **Deploy contínuo:** push na branch conectada dispara rebuild. Mudança só de env **também**
  exige redeploy — env não é lida "ao vivo".

Ver [[easypanel-armadilhas]], [[easypanel-banco-e-backup]].
