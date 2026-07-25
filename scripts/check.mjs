#!/usr/bin/env node
/**
 * Verificador da estrutura — cruza catalog.json ↔ .claude/agents/ ↔ memory/ e aponta os DESVIOS.
 * Só LÊ. Sem dependências (Node puro). Uso: node scripts/check.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const R = (p) => { try { return fs.readFileSync(path.join(root, p), 'utf8'); } catch { return ''; } };
const ls = (d) => { try { return fs.readdirSync(path.join(root, d)); } catch { return []; } };
const exists = (p) => fs.existsSync(path.join(root, p));

const fails = [];
let total = 0;
const check = (cond, label, detail = '') => {
  total++;
  if (cond) console.log(`  \x1b[32m✓\x1b[0m ${label}`);
  else { console.log(`  \x1b[31m✗\x1b[0m ${label}${detail ? ` — ${detail}` : ''}`); fails.push(`${label}${detail ? ` — ${detail}` : ''}`); }
};

console.log('═══════════ CHECK — memory + agents ═══════════\n');

const cat = JSON.parse(R('catalog.json') || '{"agents":[]}');
const agents = cat.agents || [];
const keys = new Set(agents.map((a) => a.key));

// memória disponível
const memFiles = ls('memory').filter((f) => f.endsWith('.md') && f !== 'MEMORY.md');
const memSet = new Set(memFiles);
const idx = R('memory/MEMORY.md');

// A) agentes ↔ arquivos
const mdFiles = ls('.claude/agents').filter((f) => f.endsWith('.md')).map((f) => f.replace('.md', ''));
const semMd = agents.filter((a) => (a.type === 'domain' || a.type === 'meta') && !exists(`.claude/agents/${a.key}.md`)).map((a) => a.key);
check(semMd.length === 0, 'todo agente domain/meta tem .claude/agents/<key>.md', semMd.join(', '));
const orfaos = mdFiles.filter((m) => !keys.has(m));
check(orfaos.length === 0, 'nenhum .md órfão (sem entrada no catálogo)', orfaos.join(', '));
const parentQuebrado = agents.filter((a) => a.parent && !keys.has(a.parent)).map((a) => `${a.key}→${a.parent}`);
check(parentQuebrado.length === 0, 'todo parent existe', parentQuebrado.join(', '));

// B) agentes ↔ memória
const memQuebrada = agents.flatMap((a) => (a.memory || []).filter((m) => !memSet.has(m)).map((m) => `${a.key}→${m}`));
check(memQuebrada.length === 0, 'todo memory[] do catálogo aponta pra arquivo real', memQuebrada.join(', '));
const donas = new Set(agents.flatMap((a) => a.memory || []));
const orfaMem = memFiles.filter((m) => !donas.has(m));
check(orfaMem.length === 0, 'toda memória tem ao menos um agente dono', orfaMem.join(', '));

// C) memória ↔ índice
const foraIndice = memFiles.filter((m) => !idx.includes(`(${m})`));
check(foraIndice.length === 0, 'toda memória está no MEMORY.md', foraIndice.join(', '));
const linksIdx = [...idx.matchAll(/\(([a-z0-9-]+\.md)\)/g)].map((m) => m[1]);
const linkMorto = linksIdx.filter((l) => !memSet.has(l));
check(linkMorto.length === 0, 'todo link do índice aponta pra arquivo real', linkMorto.join(', '));

// D) links [[nome]] entre memórias resolvem (ignora exemplos dentro de código)
const nomes = new Set(memFiles.map((f) => f.replace('.md', '')));
const stripCode = (c) => c.replace(/```[\s\S]*?```/g, '').replace(/`[^`]*`/g, '');
const wikilinkQuebrado = [];
for (const f of memFiles) for (const m of stripCode(R(`memory/${f}`)).matchAll(/\[\[([a-z0-9-]+)\]\]/g)) if (!nomes.has(m[1])) wikilinkQuebrado.push(`${f}→[[${m[1]}]]`);
check(wikilinkQuebrado.length === 0, 'todo link [[nome]] entre memórias resolve', wikilinkQuebrado.join(', '));

console.log('\n═══════════════════ RESUMO ═══════════════════');
console.log(`itens: ${total} · ok: ${total - fails.length} · desvios: ${fails.length}`);
if (!fails.length) console.log('\x1b[32m✅ tudo calibrado — memória e agentes em sincronia.\x1b[0m');
else { console.log('\x1b[31m⚠ desvios:\x1b[0m'); fails.forEach((d, i) => console.log(`  ${i + 1}. ${d}`)); }
process.exit(fails.length ? 1 : 0);
