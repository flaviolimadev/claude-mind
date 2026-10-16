---
name: loja-equipe-no-admin
description: O painel tem a página Equipe — o time de agentes da loja (organograma, o que cada um lê, memórias, atividade) vindo de /api/team; em produção lê a foto admin/server/seed/equipe.json, regenerada a cada commit pelo pre-commit
metadata:
  type: reference
---

Cada loja tem a sua própria equipe (o `catalog.json` + `.claude/agents/` + `memory/` do repositório
dela), e o dono vê essa equipe dentro do painel, em **Equipe** (2026-10-16):

- **Rota** `GET /api/team` (autenticada) → `admin/server/src/mind.js`: se acha o `catalog.json` na
  raiz do repositório (desenvolvimento), monta ao vivo; senão lê a **foto**
  `admin/server/seed/equipe.json`. A imagem do admin é construída com contexto `/admin`, então os
  arquivos da raiz **não existem em produção** — por isso a foto é comitada.
- **Foto:** `npm run mind:equipe` (`scripts/equipe.mjs`) gera o JSON (agentes com instruções,
  memórias com corpo e donos, últimas 40 atividades). O hook `.githooks/pre-commit` roda isso e
  faz `git add` a cada commit — só funciona com `git config core.hooksPath .githooks` ativado
  (mesmo comando que liga o post-commit). O KPI "Fonte" da página diz se está ao vivo ou na foto.
- **Página** `admin/web/src/pages/Team.jsx`: KPIs, organograma (governança → domínio → especialistas,
  cor por agente), detalhe do agente com "lê antes de agir" (chips que abrem a memória) e as
  instruções em markdown, lista de memórias (Collapse) com quem lê, e atividade recente.

**Why:** o dono quer saber quem cuida do quê na loja dele sem abrir o repositório; e lojas de
segmentos diferentes terão times diferentes (subs novos nascem onde o trabalho aparece).

**How to apply:** agente ou memória nova → commit normal já atualiza a foto (sem o hooks path,
rode `npm run mind:equipe` antes). Tudo que está em `memory/` **aparece no painel** para quem tem
login de admin: nunca escreva senha, token ou dado de cliente numa memória. Ver [[loja-blueprint]],
[[loja-admin-estoque-e-financeiro]].
