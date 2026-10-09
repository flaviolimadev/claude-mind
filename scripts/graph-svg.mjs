#!/usr/bin/env node
/**
 * Gera docs/graph.svg — o grafo REAL (catalog.json + memory/) como SVG animado,
 * pro README e pra landing. Determinístico, sem dependências (Node puro).
 * Uso: node scripts/graph-svg.mjs   (ou: npm run banner)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const R = (p) => { try { return fs.readFileSync(path.join(root, p), 'utf8'); } catch { return ''; } };

const cat = JSON.parse(R('catalog.json') || '{"agents":[]}');
const agents = cat.agents || [];
const memFiles = fs.readdirSync(path.join(root, 'memory')).filter((f) => f.endsWith('.md') && f !== 'MEMORY.md');
const owners = {};
for (const a of agents) for (const m of a.memory || []) (owners[m] ||= []).push(a.key);

const W = 1200, H = 630, CX = 600, CY = 345, KY = 0.66;
const rad = (deg) => (deg * Math.PI) / 180;
const at = (angle, r, ky = KY) => [CX + r * Math.cos(rad(angle)), CY + r * ky * Math.sin(rad(angle))];
const n1 = (x) => Math.round(x * 10) / 10;
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// ── posições: meta no anel interno, domínios no externo, subs perto do pai ──
const metas = agents.filter((a) => a.type === 'meta');
const domains = agents.filter((a) => a.type === 'domain');
const subs = agents.filter((a) => a.type === 'sub');
const pos = {}; // key → {x, y, angle, r (raio do nó), color, t (início da animação)}

metas.forEach((a, i) => {
  const angle = -90 + i * (360 / Math.max(metas.length, 1));
  const [x, y] = at(angle, 120);
  pos[a.key] = { x, y, angle, r: 17, color: a.color || '#8a8a8a', t: 0.15 + i * 0.12 };
});
domains.forEach((a, i) => {
  const angle = -90 + (i + 0.5) * (360 / Math.max(domains.length, 1));
  const [x, y] = at(angle, 265);
  pos[a.key] = { x, y, angle, r: 15, color: a.color || '#8a8a8a', t: 0.75 + i * 0.12 };
});
const byParent = {};
for (const s of subs) (byParent[s.parent] ||= []).push(s);
for (const [p, list] of Object.entries(byParent)) list.forEach((s, i) => {
  const base = pos[p]?.angle ?? -90;
  const angle = base + (i - (list.length - 1) / 2) * 20;
  const [x, y] = at(angle, 392);
  pos[s.key] = { x, y, angle, r: 11, color: s.color || '#8a8a8a', t: 1.3 + i * 0.12 };
});

// memórias orbitam o primeiro dono, viradas pra fora do centro
const memPos = {};
const byOwner = {};
for (const f of memFiles) { const o = (owners[f] || [])[0]; if (o) (byOwner[o] ||= []).push(f); }
for (const [o, list] of Object.entries(byOwner)) list.forEach((f, j) => {
  const p = pos[o]; if (!p) return;
  const angle = p.angle + (j - (list.length - 1) / 2) * 28;
  const x = p.x + 78 * Math.cos(rad(angle)), y = p.y + 78 * 0.8 * Math.sin(rad(angle));
  memPos[f] = { x, y, t: p.t + 0.35 };
});

// ── SVG ──
const edges = [], nodes = [];
const fade = (t) => `<animate attributeName="opacity" to="1" dur="0.45s" begin="${t}s" fill="freeze"/>`;

for (const s of subs) {
  const a = pos[s.key], b = pos[s.parent]; if (!a || !b) continue;
  edges.push(`<line x1="${n1(b.x)}" y1="${n1(b.y)}" x2="${n1(a.x)}" y2="${n1(a.y)}" stroke="#4a4a56" stroke-width="1.6" opacity="0">${fade(a.t)}</line>`);
}
for (const f of memFiles) {
  const m = memPos[f]; if (!m) continue;
  for (const o of owners[f] || []) {
    const p = pos[o]; if (!p) continue;
    edges.push(`<line x1="${n1(p.x)}" y1="${n1(p.y)}" x2="${n1(m.x)}" y2="${n1(m.y)}" stroke="#41414c" stroke-width="1.3" stroke-dasharray="3 3" opacity="0">${fade(m.t)}</line>`);
  }
}
for (const a of agents) {
  const p = pos[a.key]; if (!p) continue;
  const pulse = a.key === 'dispatcher'
    ? `<circle cx="${n1(p.x)}" cy="${n1(p.y)}" r="${p.r}" fill="none" stroke="${p.color}" stroke-width="1.5" opacity="0"><animate attributeName="r" values="${p.r};${p.r + 26}" dur="2.4s" begin="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.5;0" dur="2.4s" begin="2s" repeatCount="indefinite"/></circle>`
    : '';
  nodes.push(`<g opacity="0">${fade(p.t)}
    <circle cx="${n1(p.x)}" cy="${n1(p.y)}" r="${p.r + 7}" fill="${p.color}" opacity="0.14"/>
    <circle cx="${n1(p.x)}" cy="${n1(p.y)}" r="${p.r}" fill="${p.color}"/>${pulse}
    <text x="${n1(p.x)}" y="${n1(p.y + p.r + 17)}" text-anchor="middle" font-size="11.5" fill="#9a9aa6">${esc(a.key)}</text>
  </g>`);
}
for (const f of memFiles) {
  const m = memPos[f]; if (!m) continue;
  nodes.push(`<g opacity="0">${fade(m.t)}<rect x="${n1(m.x - 5.5)}" y="${n1(m.y - 5.5)}" width="11" height="11" rx="2.5" fill="#83838f"/></g>`);
}

const stats = `${agents.length} agentes · ${metas.length} meta · ${domains.length} domínio · ${subs.length} sub · ${memFiles.length} memórias`;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" font-family="-apple-system,'Segoe UI',Roboto,Ubuntu,sans-serif">
<title>claude-mind — grafo ao vivo: agentes (círculos) ligados às memórias (quadrados)</title>
<rect width="${W}" height="${H}" rx="14" fill="#0e0e11"/>
<rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="14" fill="none" stroke="#26262e"/>
<text x="28" y="44" font-size="21" font-weight="700" fill="#e7e7ea">claude-<tspan fill="#C9A96A">mind</tspan></text>
<text x="1046" y="43" text-anchor="end" font-size="12.5" fill="#8b8b95">${stats}</text>
<circle cx="1082" cy="38.5" r="4.5" fill="#6ac98a"><animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text x="1094" y="43" font-size="12.5" fill="#6ac98a">ao vivo</text>
<line x1="28" y1="60" x2="${W - 28}" y2="60" stroke="#26262e"/>
${edges.join('\n')}
${nodes.join('\n')}
<text x="${CX}" y="612" text-anchor="middle" font-size="11.5" fill="#8b8b95">node viewer/server.mjs  →  grafo interativo ao vivo em http://localhost:4173</text>
</svg>\n`;

fs.mkdirSync(path.join(root, 'docs'), { recursive: true });
fs.writeFileSync(path.join(root, 'docs', 'graph.svg'), svg);
console.log(`docs/graph.svg gerado — ${agents.length} agentes, ${memFiles.length} memórias, ${Math.round(svg.length / 1024)}kB`);
