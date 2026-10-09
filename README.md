# 🧠 claude-mind — memória persistente e agentes para o Claude Code

> **O assistente de código esquece tudo entre uma sessão e outra.** Você explica a arquitetura, ele
> resolve, e no dia seguinte começa do zero. O `claude-mind` dá a ele **memória de longo prazo**, um
> **time de agentes e sub-agentes** que se especializam sozinhos, e um **loop automático por hooks**
> que mantém tudo em sincronia. Sem dependências, Node puro.

<p align="center">
  <a href="#começar"><b>Instalar em 1 comando</b></a> ·
  <a href="#o-loop-de-auto-aprendizado-automático">Como funciona</a> ·
  <a href="#um-agente-por-ação-e-especialistas-que-nascem-sozinhos">Agentes</a> ·
  <a href="https://flaviolimadev.github.io/claude-mind/">Site</a>
</p>

**Persistent memory + self-specializing agents for Claude Code.** Your AI coding assistant loses
context between sessions: you explain the codebase, it delivers, and tomorrow it starts from zero.
`claude-mind` gives it long-term memory (one fact per file), a team of domain agents and sub-agents,
an automatic loop wired through Claude Code hooks, a consistency checker, and a live graph. Zero
dependencies, pure Node — works in any project, any language.

### O que muda na prática

| Sem memória | Com o claude-mind |
|---|---|
| Você reexplica a arquitetura toda sessão | Ele abre a sessão já sabendo o que foi decidido e por quê |
| A mesma armadilha é repetida meses depois | A armadilha virou um fato registrado, lido antes de agir |
| "Faz aí" vira improviso | A ação vai para o agente **dono** dela — e se não existe, ele é criado antes |
| O aprendizado depende de você lembrar de anotar | Três hooks fazem o loop rodar sozinho |

## As 6 peças

| Peça | O quê |
|---|---|
| `catalog.json` | A **fonte única** do time de agentes (key, tipo, pai, descrição, memória que ele lê). |
| `.claude/agents/*.md` | Os **agentes** que o Claude Code usa — um arquivo por agente (meta, domínio e sub); a hierarquia (`parent`) fica no catálogo. |
| `memory/` | A **memória**: um arquivo markdown por fato, indexado em `MEMORY.md`. |
| `scripts/check.mjs` | O **verificador**: cruza catálogo ↔ agentes ↔ memória e aponta o que saiu de sincronia. |
| `viewer/` | O **grafo AO VIVO**: abre no navegador e atualiza em tempo real quando você edita os arquivos. |
| `.claude/hooks/` | Os **hooks** que fazem o loop rodar sozinho — sem eles, a estrutura vira documentação morta. |

## Começar

**Instalar no SEU projeto** (não sobrescreve nada, funde o `settings.json` que você já tem):

```bash
git clone https://github.com/flaviolimadev/claude-mind.git
cd claude-mind
node scripts/install.mjs /caminho/do/seu/projeto
```

Ele leva os scripts, os hooks, o viewer, os **4 agentes meta** e a memória-base. Os agentes de
**domínio** não vêm prontos de propósito: eles têm que ser os domínios REAIS do seu projeto.

**Ou explorar aqui mesmo:**

```bash
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

## O loop de auto-aprendizado (automático)

Memória só serve se for **lida e mantida sem depender de lembrança**. Quem garante isso são três
hooks — o harness os executa, não o assistente (ver `memory/os-hooks.md`):

| Hook | Quando | O que faz |
|---|---|---|
| `SessionStart` | ao abrir a sessão | injeta o índice de memória e os donos por domínio; avisa se ficou desvio pendente |
| `UserPromptSubmit` | a **cada mensagem** | impõe o protocolo: rotear pelo dispatcher antes de agir; ao terminar, destilar memória, criar agente que faltou, registrar e verificar |
| `Stop` | ao fechar o turno | roda o verificador e, **com desvio, devolve exit 2** — o assistente continua até consertar (com trava anti-laço) |

Já vêm ligados em `.claude/settings.json`. Sem eles a memória existe mas ninguém lê, e o verificador
só roda quando alguém lembra. Os três hooks são Node puro (sem bash) — rodam igual em macOS, Linux
e Windows.

O fluxo que os hooks impõem:

1. **Rotear antes de fazer** — o `dispatcher` decompõe o pedido em ações e acha o dono de cada uma.
2. **Faltou dono? Cria-se o especialista** antes de executar (ver abaixo).
3. **Memória** — o que se perderia entre sessões vira um fato em `memory/`.
4. **Registrar** — `node scripts/log.mjs <agente> <tipo> "<resumo>"`.
5. **Verificar** — `node scripts/check.mjs`, zerando os desvios.

## Um agente por ação, e especialistas que nascem sozinhos

Duas regras que mudam a qualidade do resultado:

**Nenhuma ação sem dono.** Um pedido raramente é uma ação só — "subir uma feature" é desenhar +
implementar + revisar + documentar, cada uma com um responsável diferente. Se o assistente está
prestes a fazer algo "por conta própria", falta um agente.

**Recorte novo cria especialista novo.** Existe um `reviewer`; chega "revisar acessibilidade"; o
`dispatcher` procura um sub especializado nisso e, se não houver, **manda criar antes de revisar**.
Assim o time cresce exatamente onde o trabalho aparece, e cada agente vira especialista de um recorte
estreito — com regra própria, memória própria e resultado previsível.

O critério para **não** criar está em `memory/especializacao-sob-demanda.md`: recorte usado uma vez só
e sem regra própria é parâmetro, não agente. Sem esse freio a estrutura incha de agentes vazios.

Dá pra automatizar o registro por commit:

```bash
git config core.hooksPath .githooks   # cada commit vira uma atividade no grafo
```

## Estrutura

```
claude-mind/
├── .claude/hooks/          # o loop automático (load · remind · verify)
├── scripts/install.mjs     # instala em outro projeto sem sobrescrever
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

## Os 4 agentes meta

- **dispatcher** — a porta de entrada: recebe todo pedido, roteia para o dono da ação e manda criar o
  especialista quando falta.
- **maestro** — cria e governa os agentes.
- **librarian** — dono da memória; destila e indexa.
- **calibrator** — roda o verificador e mantém tudo alinhado.

Os agentes de **domínio** são os do seu projeto — o `install.mjs` não os inventa de propósito.

## Perguntas frequentes

**Como dar memória persistente ao Claude Code?**
Instale a estrutura no seu projeto (`node scripts/install.mjs /seu/projeto`). A memória vira arquivos
markdown em `memory/`, indexados em `MEMORY.md`, e o hook de `SessionStart` os carrega sozinho no
começo de cada sessão.

**Por que o Claude Code perde o contexto entre sessões?**
Porque o contexto vive na janela da conversa, não em disco. O que não estiver em arquivo se perde.
O `claude-mind` transforma o que foi aprendido em fatos versionados no repositório.

**Isso substitui o `CLAUDE.md`?**
Não — complementa. O `CLAUDE.md` diz *como trabalhar aqui*; a `memory/` guarda *o que já foi
aprendido*, um fato por arquivo, com dono e verificação.

**Funciona com outros assistentes?**
A memória e o catálogo são markdown e JSON — qualquer assistente lê. Os hooks são o formato do
Claude Code; em outro harness, o mesmo loop pode ser disparado por outro gatilho.

**Serve para projetos que não são de código?**
Sim. Aqui nasceu num projeto de produção de vídeo — os domínios eram roteiro, geração, montagem.
Domínio é o que o *seu* projeto faz.

**Does it work in English / other languages?**
Yes. The structure is language-agnostic; the shipped memory files are in Portuguese and can be
replaced by your own in any language.

## Licença

MIT. Use, copie, adapte à vontade.
