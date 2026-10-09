#!/usr/bin/env node
// Stop — antes de encerrar o turno, garante que a estrutura ficou calibrada.
// Com desvio devolve exit 2: o assistente continua e conserta em vez de deixar a casa torta.
// stop_hook_active evita laço infinito: na segunda passada, apenas libera.
// Node puro (sem bash) pra rodar igual em macOS, Linux e Windows.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const check = path.join(root, 'scripts', 'check.mjs');
if (!fs.existsSync(check)) process.exit(0);

// payload JSON no stdin; JSON.parse em vez de casar string — aguenta espaço e formatação
let payload = {};
try { payload = JSON.parse(fs.readFileSync(0, 'utf8')); } catch {}
if (payload.stop_hook_active === true) process.exit(0);

const r = spawnSync(process.execPath, [check], { cwd: root, encoding: 'utf8' });
if (r.status !== 0) {
  const text = (r.stdout || '') + (r.stderr || '');
  const lines = text.split('\n');
  const i = lines.findIndex((l) => l.includes('desvios:'));
  console.error('A estrutura claude-mind ficou COM DESVIOS — corrija antes de encerrar:');
  console.error(i >= 0 ? lines.slice(i).join('\n') : text);
  console.error('');
  console.error('Quem conserta: maestro (agentes em catalog.json + .claude/agents/) e librarian (memory/).');
  process.exit(2);
}
process.exit(0);
