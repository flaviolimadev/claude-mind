#!/bin/bash
# Stop — antes de encerrar o turno, garante que a estrutura ficou calibrada.
# Com desvio devolve exit 2: o assistente continua e conserta em vez de deixar a casa torta.
# stop_hook_active evita laço infinito: na segunda passada, apenas libera.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
[ -f scripts/check.mjs ] || exit 0

payload=$(cat 2>/dev/null)
case "$payload" in *'"stop_hook_active":true'*) exit 0 ;; esac

out=$(node scripts/check.mjs 2>&1)
if [ $? -ne 0 ]; then
  {
    echo "A estrutura claude-mind ficou COM DESVIOS — corrija antes de encerrar:"
    echo "$out" | sed -n '/desvios:/,$p'
    echo
    echo "Quem conserta: maestro (agentes em catalog.json + .claude/agents/) e librarian (memory/)."
  } >&2
  exit 2
fi
exit 0
