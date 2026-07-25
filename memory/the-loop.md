---
name: the-loop
description: O loop de auto-aprendizado — toda mudança passa por memória + agentes + verificação, por padrão
metadata:
  type: feedback
---

**Este ciclo não depende de lembrança: ele é disparado pelos hooks do harness** — ver [[os-hooks]].

Toda funcionalidade/mudança passa por este fluxo **por padrão, sem precisar pedir**:

1. **Memória primeiro:** consulte a memória relevante antes de agir; ao decidir algo, descobrir uma
   armadilha ou aprender algo não óbvio, **registre na hora** (ver [[memory-format]]).
2. **Roteie pelo agente de domínio** correspondente e **registre a atividade** com
   `node scripts/log.mjs <agente> <tipo> "<resumo>"` — isso alimenta o histórico/crescimento do grafo.
3. **Verifique:** rode `node scripts/check.mjs` e zere os desvios (ver [[the-check]]).
4. **Não quebre o que já funciona:** mudança segura e incremental.

**Why:** sem esse loop, o conhecimento fica só na cabeça da sessão atual e some no fim dela; os agentes
ficam desatualizados e o assistente repete erros. Com ele, cada sessão deixa a "mente" um pouco melhor.

**How to apply:** ao receber qualquer pedido, já assuma este fluxo. Um git hook (`.githooks/post-commit`)
pode chamar `scripts/log.mjs` automaticamente a cada commit, para o crescimento se registrar sozinho.
