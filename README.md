# 🧠 claude-mind

> Uma **memória persistente + time de agentes + auto-aprendizado** para assistentes de código
> (Claude Code e afins), com um **grafo ao vivo** pra você ver a "mente" crescer. Sem dependências.
>
> *A persistent memory + agent team + self-learning loop for coding assistants, with a live graph. Zero dependencies.*

O problema: o assistente **perde o contexto** entre sessões. Você explica tudo, ele resolve, e na sessão
seguinte começa do zero. Esta estrutura dá a ele uma **memória de longo prazo** e um **time de agentes**
que se mantêm em sincronia — e um verificador que garante que nada se perde.

## As 5 peças

| Peça | O quê |
|---|---|
| `catalog.json` | A **fonte única** do time de agentes (key, tipo, pai, descrição, memória que ele lê). |
| `.claude/agents/*.md` | Os **agentes** que o Claude Code usa (um por domínio/meta; os `sub` vivem no pai). |
| `memory/` | A **memória**: um arquivo markdown por fato, indexado em `MEMORY.md`. |
| `scripts/check.mjs` | O **verificador**: cruza catálogo ↔ agentes ↔ memória e aponta o que saiu de sincronia. |
| `viewer/` | O **grafo AO VIVO**: abre no navegador e atualiza em tempo real quando você edita os arquivos. |

## Começar

```bash
git clone https://github.com/SEU-USUARIO/claude-mind.git
cd claude-mind

node scripts/check.mjs      # verifica a estrutura (deve dar 0 desvios)
node viewer/server.mjs      # abre o grafo ao vivo em http://localhost:4173
```

Não precisa `npm install` — é tudo Node puro (>=18). Abra a pasta no seu assistente de código: ele lê
`.claude/agents/` e a `memory/` e passa a trabalhar com contexto.

## O grafo ao vivo

`node viewer/server.mjs` sobe um servidor local que desenha os **agentes** (círculos, coloridos por tipo)
ligados às **memórias** (quadradinhos) que cada um lê. Arraste pra mover, scroll pra zoom, clique num nó
pra ver o detalhe. Edite qualquer arquivo e o grafo **atualiza sozinho** (SSE). O painel lateral mostra a
**atividade recente** — o crescimento da mente.

## O loop de auto-aprendizado

Toda mudança passa por este fluxo **por padrão** (ver `memory/the-loop.md`):

1. **Memória primeiro** — leia o que já foi aprendido; registre decisões/armadilhas na hora.
2. **Roteie pelo agente** de domínio e registre: `node scripts/log.mjs <agente> <tipo> "<resumo>"`.
3. **Verifique** — `node scripts/check.mjs`, zere os desvios.
4. **Não quebre** o que já funciona.

Dá pra automatizar o registro por commit:

```bash
git config core.hooksPath .githooks   # cada commit vira uma atividade no grafo
```

## Estrutura

```
claude-mind/
├── catalog.json           # fonte única dos agentes
├── .claude/agents/        # maestro, librarian, calibrator (meta) + architect, builder, reviewer, docs
├── memory/                # MEMORY.md (índice) + um arquivo por fato
├── scripts/
│   ├── check.mjs          # verificador (só lê)
│   └── log.mjs            # registra atividade (auto-aprendizado)
├── viewer/
│   ├── server.mjs         # servidor local + tempo real (SSE)
│   └── index.html         # o grafo (autocontido, sem CDN)
└── .githooks/post-commit  # registra cada commit no grafo
```

## Adaptar ao seu projeto

O conteúdo em `memory/` e alguns agentes de domínio são **exemplos genéricos** — troque pelos seus.
Adicione um agente novo em `catalog.json` + `.claude/agents/<key>.md` (o `maestro` faz isso), registre
fatos em `memory/` (o `librarian`), e rode o `check` (o `calibrator`). O grafo mostra o resto.

## Os 3 agentes meta

- **maestro** — cria e governa os agentes.
- **librarian** — dono da memória; destila e indexa.
- **calibrator** — roda o verificador e mantém tudo alinhado.

## Licença

MIT. Use, copie, adapte à vontade.
