#!/usr/bin/env node
// SessionStart — carrega a memória e o mapa de agentes UMA vez por sessão.
// Sem isso, a memória existe mas ninguém lê: o assistente começa a sessão cego.
// Node puro (sem bash) pra rodar igual em macOS, Linux e Windows.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const R = (p) => { try { return fs.readFileSync(path.join(root, p), 'utf8'); } catch { return ''; } };

const idx = R('memory/MEMORY.md');
if (!idx) process.exit(0);

console.log('═══ claude-mind · memória do projeto (carregada automaticamente) ═══');
console.log('');
console.log(idx);
console.log('── donos por domínio (catalog.json) ──');
try {
  const c = JSON.parse(R('catalog.json'));
  const by = (t) => c.agents.filter((a) => a.type === t).map((a) => a.key).join(', ');
  console.log('meta:   ' + by('meta'));
  console.log('domain: ' + by('domain'));
  console.log('sub:    ' + by('sub'));
} catch {}

const check = path.join(root, 'scripts', 'check.mjs');
if (fs.existsSync(check)) {
  const r = spawnSync(process.execPath, [check], { cwd: root, stdio: 'ignore' });
  if (r.status !== 0) {
    console.log('');
    console.log("⚠ A estrutura está COM DESVIOS. Rode 'node scripts/check.mjs' e corrija antes de seguir.");
  }
}
process.exit(0);
