#!/bin/bash
# UserPromptSubmit — a cada mensagem, impõe o protocolo: rotear antes de fazer, destilar depois.
# Curto de propósito: o conteúdo da memória já entrou no SessionStart (mind-load.sh).
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
[ -f catalog.json ] || exit 0

cat <<'TXT'
═══ claude-mind · protocolo obrigatório ═══
ANTES DE AGIR (dispatcher):
 a. Decomponha o pedido em AÇÕES (verbos), não em assuntos.
 b. Para cada ação, ache o dono em catalog.json e desça até o SUB do recorte
    (ex.: "revisar segurança deste endpoint" → reviewer → security-review).
 c. Não existe o especialista do recorte? CRIE ANTES de executar (catalog.json +
    .claude/agents/<key>.md, nascendo como sub do domínio certo). Nenhuma ação sem dono.
 d. Carregue de memory/ os fatos relevantes — não repita erro já registrado.
DEPOIS DE ENTREGAR (sem pedir permissão):
 1. MEMÓRIA — aprendeu algo que se perderia? memory/<slug>.md + linha no MEMORY.md.
 2. AGENTES — domínio sem dono ou especialização recorrente? crie (catalog + .md juntos).
 3. REGISTRE — node scripts/log.mjs <agente> <tipo> "<resumo>"
 4. VERIFIQUE — node scripts/check.mjs precisa fechar com 0 desvios.
TXT
exit 0
