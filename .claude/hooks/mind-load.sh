#!/bin/bash
# SessionStart — carrega a memória e o mapa de agentes UMA vez por sessão.
# Sem isso, a memória existe mas ninguém lê: o assistente começa a sessão cego.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
[ -f memory/MEMORY.md ] || exit 0

echo "═══ claude-mind · memória do projeto (carregada automaticamente) ═══"
echo
cat memory/MEMORY.md
echo
echo "── donos por domínio (catalog.json) ──"
node -e '
try {
  const c = require("./catalog.json");
  const by = t => c.agents.filter(a => a.type === t).map(a => a.key).join(", ");
  console.log("meta:   " + by("meta"));
  console.log("domain: " + by("domain"));
  console.log("sub:    " + by("sub"));
} catch (e) {}
' 2>/dev/null

if ! node scripts/check.mjs >/dev/null 2>&1; then
  echo
  echo "⚠ A estrutura está COM DESVIOS. Rode 'node scripts/check.mjs' e corrija antes de seguir."
fi
exit 0
