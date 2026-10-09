# Changelog

Todas as mudanças relevantes do claude-mind, da mais nova pra mais antiga.
Nas aulas e tutoriais, referencie a versão (tag) — assim o material não quebra quando o projeto evoluir.

## [0.4.0] — 2026-10-09

### Adicionado
- **Três módulos de tecnologia** (F2 do plano de setores), todos compartilhando o domínio-pai
  `dev` (instalado uma vez, pulado nos demais):
  - **`dev-node`** — ESM vs CJS (os erros clássicos e a saída de cada um), `process.env` sempre
    string + `--env-file` nativo, scripts npm como interface, critério de três perguntas antes de
    qualquer dependência.
  - **`dev-php`** — convenções que o Laravel premia, armadilhas de produção (N+1 incl. MorphTo,
    `env()` nulo com config cacheada, timezone deslocando relatório, Model serializado na fila) e
    a sequência de release completa.
  - **`dev-postgres`** — migrations sem lock em tabela viva (NOT NULL em 3 passos, INDEX
    CONCURRENTLY fora de transação), otimização guiada por EXPLAIN (FK sem índice automático) e
    tipos certos (timestamptz, numeric, bigint identity).

## [0.3.0] — 2026-10-09

### Adicionado
- **Módulos (setores) opcionais**: pacotes de agentes + memórias pré-destiladas por stack, em
  `modules/<key>/` (manifesto `module.json` + `agents/` + `memory/`). Comandos:
  `npx @flaviolimadev/claude-mind list` e `… add <modulo>` (roteados pelo `install.mjs`;
  motor em `scripts/module.mjs`). O `add` funde agentes no `catalog.json`, copia memórias,
  atualiza o `MEMORY.md`, registra no log e fecha com o check — idempotente, nunca sobrescreve.
- **Módulo piloto `deploy-easypanel`**: domínio `deploy` + sub `deploy-easypanel`, com 3 memórias
  de armadilhas reais (bind `0.0.0.0`, filesystem efêmero/volumes, env no painel, DNS antes do
  SSL, conexão interna de banco, backup antes de migration).
- Seção "Módulos (setores) opcionais" no README.

### Mudado
- `install.mjs` virou roteador (`<pasta>` instala a base; `add`/`list` delegam aos módulos) e
  passou a copiar `scripts/module.mjs` pro projeto destino.

## [0.2.0] — 2026-10-09

### Adicionado
- **Instalação em um comando via npx**: `npx @flaviolimadev/claude-mind@latest .` (campo `bin`
  no `package.json`; o pacote leva scripts, hooks, viewer, agentes meta e memória-base).
- **Sub-agentes com arquivo próprio** (`.claude/agents/security-review.md` e
  `performance-review.md`) — viram subagentes invocáveis de verdade pelo Claude Code; a
  hierarquia (`parent`) continua no catálogo.
- **Banner do grafo em SVG animado** (`docs/graph.svg`), gerado dos dados reais por
  `scripts/graph-svg.mjs` (`npm run banner`) — usado no README e na landing; regenere quando o
  time de agentes mudar.
- Este CHANGELOG.

### Mudado
- **Hooks portados de bash para Node puro** (`.claude/hooks/*.mjs`): rodam igual em macOS, Linux
  e Windows, resolvem caminhos por `CLAUDE_PROJECT_DIR` e leem `stop_hook_active` com
  `JSON.parse` (antes, casamento de string frágil no payload).
- `check.mjs` passa a exigir `.claude/agents/<key>.md` de **todo** agente do catálogo (antes, só
  `domain`/`meta`).
- Viewer escuta só em `127.0.0.1` (antes `0.0.0.0`) e o watch deixou de usar `recursive`, que
  quebrava no Node 18 em Linux.

### Corrigido
- `install.mjs` dá permissão de execução ao `.githooks/post-commit` no destino (antes o git hook
  chegava sem `+x` em macOS/Linux e nunca rodava).
- `log.mjs` devolve exit 1 em erro de uso (antes, 0).
- README com a URL real do clone; landing não limita mais Windows a WSL.

## [0.1.0] — 2026-07-25

- Estrutura inicial: memória persistente (`memory/` + `MEMORY.md`), catálogo de agentes
  (`catalog.json`), agentes meta (maestro, librarian, calibrator, dispatcher) e de domínio,
  loop automático por três hooks (`SessionStart`, `UserPromptSubmit`, `Stop` com exit 2),
  verificador (`scripts/check.mjs`), registro de atividade (`scripts/log.mjs` +
  `.githooks/post-commit`), grafo ao vivo (`viewer/`), instalador não-destrutivo
  (`scripts/install.mjs`) e landing no GitHub Pages.
