---
name: how-it-works
description: A estrutura em uma página — catálogo, agentes, memória, verificador e grafo, e como se ligam
metadata:
  type: reference
---

Esta estrutura dá ao seu assistente de código uma **memória persistente** e um **time de agentes**
que não perde o contexto entre sessões. São cinco peças que se alimentam:

1. **`catalog.json`** — a fonte única do time de agentes. Cada agente tem `key`, `type`
   (`meta` | `domain` | `sub`), `parent`, `description` e `memory[]` (quais fatos ele lê antes de agir).
2. **`.claude/agents/*.md`** — os agentes de verdade que o Claude Code usa (um arquivo por agente de
   domínio/meta). Os `sub` vivem dentro do `.md` do pai.
3. **`memory/`** — a base de conhecimento: um arquivo markdown por fato, indexado em `MEMORY.md`.
   É a memória de longo prazo — o que ficou decidido, aprendido, convencionado.
4. **`scripts/check.mjs`** — o verificador: cruza catálogo ↔ arquivos ↔ memória e aponta o que saiu de
   sincronia (agente sem arquivo, memória sem dono, link quebrado, item fora do índice).
5. **`viewer/`** — o grafo AO VIVO: abre no navegador e mostra agentes ↔ memória, com atualização em
   tempo real quando você edita os arquivos.

A regra de ouro (ver [[the-loop]]): **toda mudança passa por memória + agentes + verificação, por
padrão** — sem isso, o conhecimento se perde e os agentes ficam desatualizados.
