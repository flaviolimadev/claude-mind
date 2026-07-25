#!/usr/bin/env node
/**
 * Registra uma atividade em memory/.activity.jsonl — alimenta o histórico/crescimento no grafo.
 * Uso: node scripts/log.mjs <agente> <tipo> "<resumo>"
 * Ex.:  node scripts/log.mjs builder executou "adicionei o endpoint X"
 * Pode ser chamado por um git hook (.githooks/post-commit) pra registrar cada commit sozinho.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const [, , agent, type, ...rest] = process.argv;
const summary = rest.join(' ').trim();
if (!agent || !type || !summary) {
  console.error('uso: node scripts/log.mjs <agente> <tipo> "<resumo>"');
  process.exit(0);
}
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const file = path.join(root, 'memory', '.activity.jsonl');
const line = JSON.stringify({ at: new Date().toISOString(), agent, type, summary }) + '\n';
fs.appendFileSync(file, line);
console.log(`registrado: ${agent} · ${type} · ${summary}`);
