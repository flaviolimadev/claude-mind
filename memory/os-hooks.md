---
name: os-hooks
description: O loop é automático — três hooks do harness carregam a memória, impõem o protocolo e barram o encerramento com desvio
metadata:
  type: reference
---

Memória e agentes só funcionam se forem **lidos e mantidos sem depender de lembrança**. Como quem
executa hook é o harness (não o assistente), o loop vive em `.claude/settings.json`:

| Hook | Script | O que faz |
|---|---|---|
| `SessionStart` | `.claude/hooks/mind-load.sh` | injeta `memory/MEMORY.md` inteiro + os donos por domínio, uma vez por sessão; avisa se a sessão anterior deixou desvio |
| `UserPromptSubmit` | `.claude/hooks/mind-remind.sh` | a CADA mensagem, injeta o protocolo: rotear pelo dispatcher antes de agir; depois de entregar → memória, agente novo se faltou dono, `log.mjs`, `check.mjs` |
| `Stop` | `.claude/hooks/mind-verify.sh` | roda `check.mjs` antes de encerrar o turno; **com desvio devolve exit 2** e o assistente continua até consertar |

**Por que a divisão:** o conteúdo pesado (índice de memória) entra uma vez no SessionStart; o
lembrete do UserPromptSubmit é curto de propósito, para não inflar o contexto a cada mensagem.

**Proteção anti-laço:** o `Stop` lê `stop_hook_active` do payload — na segunda passada sai com 0 em
vez de bloquear de novo, então nunca entra em loop infinito.

**Sem os hooks, a estrutura vira documentação morta:** a memória existe mas ninguém lê, e o
verificador só roda quando alguém lembra. Ver [[the-loop]], [[the-check]].
