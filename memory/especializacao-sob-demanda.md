---
name: especializacao-sob-demanda
description: Recorte novo cria especialista novo — o sistema ganha agentes conforme encontra trabalho que ninguém domina
metadata:
  type: feedback
---

Existe um dono de revisão (`reviewer`); chega um pedido de **revisão de acessibilidade**; o sistema
verifica se há especialista nisso — **se não houver, cria** — e só então revisa.

**Vale para qualquer domínio:** um runtime novo cria um sub de build; um provedor novo cria um
domínio; um tipo de conteúdo novo cria um especialista de conteúdo.

**Como criar (o `maestro` executa, o `dispatcher` aciona):**
1. Entrada em `catalog.json` com **função única** e `parent` correto (especialista nasce `sub`).
2. Arquivo `.claude/agents/<key>.md` com: função única, o que ler antes, regras duras e o que está
   fora do escopo.
3. Ligar a memória relevante em `memory[]`.
4. `node scripts/check.mjs` tem que fechar zerado.

**Critério para NÃO criar:** se o recorte é usado uma vez só e não tem regra própria, ele é
parâmetro — não agente. Especialista existe quando há **conhecimento reaproveitável** naquele recorte.
Sem esse critério a estrutura incha de agentes vazios.

**Nomenclatura:** `<dominio>-<recorte>` (ex.: `reviewer-a11y`, `builder-migrations`).

Ver [[roteamento-de-tarefas]], [[how-it-works]].
