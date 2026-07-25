---
name: the-check
description: O verificador scripts/check.mjs — cruza catálogo, agentes e memória e aponta os desvios
metadata:
  type: reference
---

`node scripts/check.mjs` é a rede de segurança. Só LÊ. Rode no começo de toda manutenção e sempre que
adicionar um agente ou uma memória. Ele confere:

- **Agentes ↔ arquivos:** todo agente `domain`/`meta` do catálogo tem `.claude/agents/<key>.md`;
  nenhum `.md` órfão (sem entrada no catálogo); todo `parent` existe.
- **Agentes ↔ memória:** todo `memory[]` do catálogo aponta pra arquivo real; toda memória tem ao menos
  um agente dono (senão é conhecimento que ninguém lê).
- **Memória ↔ índice:** todo arquivo de `memory/` está no `MEMORY.md` e vice-versa; links `[[nome]]`
  resolvem.

Saída: lista de **desvios**. **0 desvios** = tudo calibrado. Qualquer desvio → corrija e rode de novo.
Dono da rotina: o agente **calibrator**. É o mesmo princípio de um lint, mas para a sua "mente".
