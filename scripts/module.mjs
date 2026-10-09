#!/usr/bin/env node
/**
 * Módulos (setores) opcionais do claude-mind — lista e instala pacotes de agentes + memórias
 * pré-destiladas por stack (deploy, node, php…). Sem dependências (Node puro).
 *
 * Uso:     node scripts/module.mjs list
 *          node scripts/module.mjs add <modulo> [pasta-do-projeto]   (padrão: pasta atual)
 * Via npx: npx @flaviolimadev/claude-mind list
 *          npx @flaviolimadev/claude-mind add <modulo>
 *
 * Regra de ouro: instale só os setores que o SEU projeto usa — módulo de stack que você não usa
 * é inflação (ver memory/especializacao-sob-demanda.md).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const src = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const MODS = path.join(src, 'modules');
const [, , cmd, key, destArg] = process.argv;

const mods = () => (fs.existsSync(MODS)
  ? fs.readdirSync(MODS).filter((d) => fs.existsSync(path.join(MODS, d, 'module.json')))
  : []);
const manifest = (k) => JSON.parse(fs.readFileSync(path.join(MODS, k, 'module.json'), 'utf8'));

if (cmd === 'list') {
  const list = mods();
  if (!list.length) { console.log('nenhum módulo disponível nesta instalação.'); process.exit(0); }
  console.log('\nmódulos (setores) disponíveis — instale com: npx @flaviolimadev/claude-mind add <key>\n');
  for (const k of list) {
    const m = manifest(k);
    console.log(`  ${m.key}  —  ${m.name}  (v${m.version}, verificado em ${m.verifiedAt})`);
    console.log(`      ${m.description}`);
    console.log(`      agentes: ${m.agents.map((a) => a.key).join(', ')} · memórias: ${m.memory.length}`);
  }
  console.log('\nRegra de ouro: instale só os setores que o SEU projeto usa.');
  process.exit(0);
}

if (cmd !== 'add' || !key) {
  console.error('uso: node scripts/module.mjs list | add <modulo> [pasta-do-projeto]');
  process.exit(1);
}
if (!mods().includes(key)) {
  console.error(`módulo desconhecido: ${key}\ndisponíveis: ${mods().join(', ') || '(nenhum)'}`);
  process.exit(1);
}

const dst = path.resolve(destArg || process.cwd());
const dcat = path.join(dst, 'catalog.json');
if (!fs.existsSync(dcat)) {
  console.error(`não achei catalog.json em ${dst} — instale a base do claude-mind primeiro:\n  npx @flaviolimadev/claude-mind .`);
  process.exit(1);
}

const m = manifest(key);
const cat = JSON.parse(fs.readFileSync(dcat, 'utf8'));
cat.agents ||= [];
const have = new Set(cat.agents.map((a) => a.key));
let novos = 0, pulados = 0;
const skip = (what) => { pulados++; console.log(`  = ${what} (já existe, mantido)`); };

console.log(`\ninstalando módulo ${m.name} (v${m.version}) em ${dst}\n`);

// 1) agentes no catálogo (módulo é autocontido: traz o domínio-pai junto; o que existe, pula)
for (const a of m.agents) {
  if (have.has(a.key)) { skip(`agente ${a.key} no catálogo`); continue; }
  cat.agents.push(a); have.add(a.key);
  novos++; console.log(`  + agente ${a.key} (${a.type}) no catálogo`);
}
fs.writeFileSync(dcat, JSON.stringify(cat, null, 2) + '\n');

// 2) arquivos dos agentes e das memórias, sem sobrescrever nada
const copy = (fromRel, toRel) => {
  const to = path.join(dst, toRel);
  if (fs.existsSync(to)) return skip(toRel);
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(path.join(MODS, key, fromRel), to);
  novos++; console.log(`  + ${toRel}`);
};
for (const a of m.agents) copy(`agents/${a.key}.md`, `.claude/agents/${a.key}.md`);
for (const f of m.memory) copy(`memory/${f}`, `memory/${f}`);

// 3) índice MEMORY.md — uma linha por memória, deduplicada
const idxPath = path.join(dst, 'memory', 'MEMORY.md');
let idx = fs.existsSync(idxPath) ? fs.readFileSync(idxPath, 'utf8') : '# MEMORY\n';
const desc = (f) => {
  const md = fs.readFileSync(path.join(MODS, key, 'memory', f), 'utf8');
  const d = md.match(/^description:\s*(.*)$/m);
  return (d ? d[1] : '').replace(/^["']|["']$/g, '');
};
const humano = (f) => { const s = f.replace('.md', '').replaceAll('-', ' '); return s[0].toUpperCase() + s.slice(1); };
for (const f of m.memory) {
  if (idx.includes(`(${f})`)) { skip(`linha de ${f} no MEMORY.md`); continue; }
  idx = idx.replace(/\s*$/, '\n') + `- [${humano(f)}](${f}) — ${desc(f)}\n`;
  novos++; console.log(`  + linha de ${f} no MEMORY.md`);
}
fs.writeFileSync(idxPath, idx);

// 4) registra a atividade e verifica a estrutura no destino
spawnSync(process.execPath, [path.join(dst, 'scripts', 'log.mjs'), 'maestro', 'instalou',
  `módulo ${m.key} v${m.version} (${m.agents.map((a) => a.key).join(', ')})`], { cwd: dst, stdio: 'ignore' });

console.log(`\n${novos} itens novos, ${pulados} mantidos.`);
const chk = spawnSync(process.execPath, [path.join(dst, 'scripts', 'check.mjs')], { cwd: dst, encoding: 'utf8' });
console.log((chk.stdout || '').split('\n').filter(Boolean).slice(-2).join('\n'));
if (chk.status !== 0) { console.error('⚠ o check acusou desvios depois da instalação — corrija antes de usar.'); process.exit(1); }
console.log(`\nLembrete: instale só setores que o SEU projeto usa. Memórias deste módulo verificadas em ${m.verifiedAt}.`);
