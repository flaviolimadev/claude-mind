---
name: node-zero-deps
description: Critério antes de npm install — o Node já faz (fetch, node:test, crypto.randomUUID, fs.watch, --env-file); dependência que entra é custo permanente
metadata:
  type: feedback
---

Antes de QUALQUER `npm install`, três perguntas:

1. **O Node já faz?** `fetch` nativo, `node:test` (runner com watch), `crypto.randomUUID()`,
   `node:crypto` pra hash, `fs.watch`, `--env-file`, `AbortController`. A stdlib de hoje cobre o
   que em 2019 pedia axios, jest, uuid e dotenv.
2. **A dep é pequena e mantida?** Veja o que ela puxa (`npm ls` depois de instalar assusta).
3. **O custo permanente se paga?** Cada dependência é código de terceiro rodando com os seus
   privilégios + um breaking change futuro + superfície de supply chain.

Quando entra: versão travada pelo lockfile **comitado**, e o porquê registrado (que problema ela
resolve que a stdlib não resolvia).

**Why:** projeto que instala em um comando, sem `npm install`, elimina uma classe inteira de
fricção e risco — é a razão de o próprio claude-mind ser zero-deps.

**How to apply:** na revisão, toda dependência nova exige a resposta às três perguntas no PR/commit.
Ver [[node-env-e-scripts]].
