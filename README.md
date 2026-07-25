# 🧠 claude-mind

> Uma **memória persistente + time de agentes + auto-aprendizado** para assistentes de código
> (Claude Code e afins), com um **grafo ao vivo** pra você ver a "mente" crescer. Sem dependências.
>
> *A persistent memory + agent team + self-learning loop for coding assistants, with a live graph. Zero dependencies.*

O problema: o assistente **perde o contexto** entre sessões. Você explica tudo, ele resolve, e na sessão
seguinte começa do zero. Esta estrutura dá a ele uma **memória de longo prazo** e um **time de agentes**
que se mantêm em sincronia — e um verificador que garante que nada se perde.

## As 6 peças

| Peça | O quê |
|---|---|
| `catalog.json` | A **fonte única** do time de agentes (key, tipo, pai, descrição, memória que ele lê). |
| `.claude/agents/*.md` | Os **agentes** que o Claude Code usa (um por domínio/meta; os `sub` vivem no pai). |
| `memory/` | A **memória**: um arquivo markdown por fato, indexado em `MEMORY.md`. |
| `scripts/check.mjs` | O **verificador**: cruza catálogo ↔ agentes ↔ memória e aponta o que saiu de sincronia. |
| `viewer/` | O **grafo AO VIVO**: abre no navegador e atualiza em tempo real quando você edita os arquivos. |
| `.claude/hooks/` | Os **hooks** que fazem o loop rodar sozinho — sem eles, a estrutura vira documentação morta. |

## Começar

**Instalar no SEU projeto** (não sobrescreve nada, funde o `settings.json` que você já tem):

```bash
git clone https://github.com/SEU-USUARIO/claude-mind.git
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
só roda quando alguém lembra.

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

## Licença

MIT. Use, copie, adapte à vontade.
