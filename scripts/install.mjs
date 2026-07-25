#!/usr/bin/env node
/**
 * Instala o claude-mind em OUTRO projeto, sem sobrescrever nada.
 * Copia a estrutura (catalog, agentes meta, memória-base, scripts, hooks, viewer),
 * funde o .claude/settings.json existente em vez de substituir, e não toca no que já existe.
 *
 * Uso, de dentro do claude-mind:  node scripts/install.mjs /caminho/do/seu/projeto
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const src = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const dst = path.resolve(process.argv[2] || '');
if (!process.argv[2]) { console.error('uso: node scripts/install.mjs <pasta-do-projeto>'); process.exit(1); }
if (!fs.existsSync(dst)) { console.error(`pasta não existe: ${dst}`); process.exit(1); }
if (path.resolve(src) === dst) { console.error('destino é o próprio claude-mind'); process.exit(1); }

const META = ['maestro', 'librarian', 'calibrator', 'dispatcher'];
const MEM_BASE = ['how-it-works.md', 'memory-format.md', 'the-check.md', 'the-loop.md',
  'os-hooks.md', 'roteamento-de-tarefas.md', 'especializacao-sob-demanda.md'];

let criados = 0, pulados = 0;
const copy = (rel, transform) => {
  const from = path.join(src, rel), to = path.join(dst, rel);
  if (fs.existsSync(to)) { pulados++; console.log(`  = ${rel} (já existe, mantido)`); return; }
  fs.mkdirSync(path.dirname(to), { recursive: true });
  let body = fs.readFileSync(from);
  if (transform) body = Buffer.from(transform(body.toString('utf8')));
  fs.writeFileSync(to, body);
  if (rel.endsWith('.sh') || rel.endsWith('.mjs')) fs.chmodSync(to, 0o755);
  criados++; console.log(`  + ${rel}`);
};

console.log(`\ninstalando claude-mind em ${dst}\n`);

// scripts, hooks e viewer vão inteiros
for (const f of ['scripts/check.mjs', 'scripts/log.mjs', 'scripts/install.mjs',
                 'viewer/server.mjs', 'viewer/index.html',
                 '.claude/hooks/mind-load.sh', '.claude/hooks/mind-remind.sh', '.claude/hooks/mind-verify.sh',
                 '.githooks/post-commit']) copy(f);

// agentes meta + memória-base (os agentes de DOMÍNIO são do seu projeto, não vêm de exemplo)
for (const k of META) copy(`.claude/agents/${k}.md`);
for (const m of MEM_BASE) copy(`memory/${m}`);

// catálogo só com os meta — os domínios nascem do seu projeto
copy('catalog.json', (txt) => {
  const c = JSON.parse(txt);
  c.agents = c.agents.filter((a) => META.includes(a.key));
  c._doc = c._doc + ' Instalado por scripts/install.mjs: adicione aqui os domínios REAIS do seu projeto.';
  return JSON.stringify(c, null, 2) + '\n';
});

// índice de memória só com a base
copy('memory/MEMORY.md', (txt) =>
  txt.split('\n').filter((l) => !l.startsWith('- [') || MEM_BASE.some((m) => l.includes(`(${m})`))).join('\n'));

// settings.json: FUNDE os hooks em vez de sobrescrever
const st = path.join(dst, '.claude/settings.json');
const novo = JSON.parse(fs.readFileSync(path.join(src, '.claude/settings.json'), 'utf8'));
if (fs.existsSync(st)) {
  const atual = JSON.parse(fs.readFileSync(st, 'utf8'));
  atual.hooks ||= {};
  for (const [evt, blocos] of Object.entries(novo.hooks)) {
    atual.hooks[evt] ||= [];
    for (const bloco of blocos) {
      const cmds = bloco.hooks.map((h) => h.command);
      const jaTem = JSON.stringify(atual.hooks[evt]).includes(cmds[0]);
      if (!jaTem) atual.hooks[evt].push(bloco);
    }
  }
  fs.writeFileSync(st, JSON.stringify(atual, null, 2) + '\n');
  console.log('  ~ .claude/settings.json (hooks fundidos, config existente preservada)');
} else copy('.claude/settings.json');

fs.mkdirSync(path.join(dst, 'memory'), { recursive: true });
const act = path.join(dst, 'memory/.activity.jsonl');
if (!fs.existsSync(act)) fs.writeFileSync(act, '');

console.log(`\n${criados} arquivos criados, ${pulados} mantidos.\n`);
console.log('próximos passos:');
console.log('  1. liste os DOMÍNIOS reais do seu projeto e crie um agente para cada (o maestro faz)');
console.log('  2. registre em memory/ os fatos que já se sabe (convenções, decisões, armadilhas)');
console.log('  3. node scripts/check.mjs   → tem que fechar com 0 desvios');
console.log('  4. node viewer/server.mjs   → veja o grafo em http://localhost:4173\n');
