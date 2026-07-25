#!/usr/bin/env node
/**
 * Viewer AO VIVO da estrutura — servidor local, sem dependências (Node puro).
 * Serve o grafo de agentes ↔ memória e atualiza em tempo real (SSE) quando você edita os arquivos.
 * Uso: node viewer/server.mjs   →   abre http://localhost:4173
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, '..');
const PORT = process.env.PORT || 4173;
const R = (p) => { try { return fs.readFileSync(path.join(root, p), 'utf8'); } catch { return ''; } };
const ls = (d) => { try { return fs.readdirSync(path.join(root, d)); } catch { return []; } };

/** Lê o frontmatter simples (name/description) de um markdown. */
function front(md) {
  const m = md.match(/^---\n([\s\S]*?)\n---/);
  const out = {};
  if (m) for (const line of m[1].split('\n')) { const kv = line.match(/^(name|description):\s*(.*)$/); if (kv) out[kv[1]] = kv[2].replace(/^["']|["']$/g, ''); }
  return out;
}

/** Monta o objeto do grafo: agentes, memórias (com donos), atividade e stats. */
function graph() {
  const cat = JSON.parse(R('catalog.json') || '{"agents":[]}');
  const agents = (cat.agents || []).map((a) => ({ key: a.key, name: a.name || a.key, type: a.type, parent: a.parent ?? null, color: a.color || '#8a8a8a', description: a.description || '', memory: a.memory || [] }));
  const memFiles = ls('memory').filter((f) => f.endsWith('.md') && f !== 'MEMORY.md');
  const owners = {};
  for (const a of agents) for (const m of a.memory) (owners[m] ||= []).push(a.key);
  const memory = memFiles.map((f) => { const fm = front(R(`memory/${f}`)); return { file: f, name: fm.name || f.replace('.md', ''), description: fm.description || '', owners: owners[f] || [] }; });
  const activity = R('memory/.activity.jsonl').trim().split('\n').filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean).reverse().slice(0, 50);
  const bytes = memFiles.reduce((s, f) => s + Buffer.byteLength(R(`memory/${f}`)), 0);
  return {
    agents, memory, activity,
    stats: { agents: agents.length, meta: agents.filter((a) => a.type === 'meta').length, domain: agents.filter((a) => a.type === 'domain').length, sub: agents.filter((a) => a.type === 'sub').length, memoria: memFiles.length, bytes },
  };
}

const clients = new Set();
const send = (res, ev, data) => res.write(`event: ${ev}\ndata: ${JSON.stringify(data)}\n\n`);

// observa os arquivos e avisa os clientes (debounced)
let timer = null;
const watch = (dir) => { try { fs.watch(path.join(root, dir), { recursive: true }, () => { clearTimeout(timer); timer = setTimeout(() => { for (const c of clients) send(c, 'reload', { t: Date.now() }); }, 150); }); } catch {} };
watch('.claude/agents'); watch('memory'); try { fs.watch(path.join(root, 'catalog.json'), () => { clearTimeout(timer); timer = setTimeout(() => { for (const c of clients) send(c, 'reload', {}); }, 150); }); } catch {}

http.createServer((req, res) => {
  if (req.url === '/api/graph') { res.writeHead(200, { 'content-type': 'application/json' }); return res.end(JSON.stringify(graph())); }
  if (req.url === '/api/stream') {
    res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive' });
    res.write('retry: 2000\n\n'); clients.add(res); req.on('close', () => clients.delete(res)); return;
  }
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(R('viewer/index.html'));
}).listen(PORT, () => console.log(`\n  claude-mind viewer  →  http://localhost:${PORT}\n  (edite os arquivos e veja o grafo atualizar ao vivo)\n`));
