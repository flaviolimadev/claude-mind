# Revela — análise do template e plano para colocar no ar

> Template: `Revela.html` (Claude Design, 29/out/2026) → desempacotado em `template/`.
> Spec de produto: `ESPECIFICACAO.md`. Motor de edição: `../estudio-fotografia/`.
> Objetivo deste documento: dizer exatamente **o que o protótipo faz hoje**, **o que falta para
> cada tela funcionar de verdade** e **em que ordem construir** para ter uma versão online de
> testes o mais cedo possível.

---

## 1. O que é o arquivo que você me mandou

`Revela.html` é um **"bundled page"**: um empacotador que, ao abrir no navegador, desempacota 6
assets (gzip + base64) e monta a página. Dentro dele:

| Peça | O que é | Uso no produto |
|---|---|---|
| `template.html` (112 KB) | O markup das 8 telas, com **binding próprio** do Claude Design: `{{ expr }}`, `<sc-if value>`, `<sc-for list as>`, `sc-camel-on-click/change/key-down`, `style-hover`, `style-focus`, `<image-slot>` | **É a fonte do visual.** Vira componentes React/JSX por conversão mecânica. |
| `<script type="text/x-dc">` (376 linhas) | Uma classe `Component extends DCLogic` com **toda a lógica e todos os dados simulados**: usuários, fotos, pastas, presets, carteira, compras; `renderVals()` devolve o dicionário que o template lê. | **É a especificação funcional.** Cada campo de `renderVals()` vira estado/consulta real. |
| `dc-runtime.js` (69 KB) | Runtime do Claude Design que interpreta o template (sc-if/sc-for, `DCLogic`). | Só protótipo. Não vai para produção. |
| `image-slot.js` (65 KB) | Web component de "imagem arrastável" (placeholder que aceita drop de arquivo). | Vira `<img>` real com URL assinada + upload real. |
| React 18.3.1 + ReactDOM | Dependências. | Mantidas (Next.js). |
| Sora 600/700 (woff2) | Fonte do logo "revela". | Mantida (Google Fonts). |

**Props do protótipo** (painel do Claude Design): `startScreen` ∈ {profile, explore, photo,
studio, auth, checkout, upload, purchases}, `startLoggedIn` (false), `walletBalance` (R$ 40),
`previewBlur` (8 px). Confirmam as 8 telas e duas regras: visitante navega sem conta; foto paga
tem prévia borrada.

**Identidade visual (manter 1:1):** teal `#0f9d8a` (hover `#0b7a6b`, fundo claro `#e6f5f2`),
branco, cinzas `#efefef / #e5e5e5 / #dcdcdc / #737373 / #8e8e8e`, vermelho de erro `#c0392b`,
coração `#e0245e`; logo "revela" em **Sora 700**, corpo em fonte do sistema 14 px; raios 8–16 px;
largura máxima 975 px (telas de leitura) e 560 px (formulários); **breakpoint 760 px**: desktop
mostra ícones no header, celular mostra **tab bar fixa de 5 itens** (Início, Publicar, Estúdio,
Compras, Perfil); grade de fotos **3 colunas quadradas** (estilo Instagram); avatares/cores de
placeholder em `oklch` derivadas do nome (`tint()`).

---

## 2. Tela por tela: o que faz hoje → o que precisa para funcionar

### 2.1 Header + tab bar (`showNav`, `showTabs`)
- **Hoje:** visitante vê "Entrar / Criar conta"; logado vê ícones (desktop) ou tab bar (mobile), saldo da carteira e avatar.
- **Precisa:** sessão real (Supabase Auth), saldo vindo do ledger, avatar vindo do storage. Rotas reais em vez de `screen` em estado: `/` (explorar), `/@handle`, `/p/[id]`, `/studio`, `/upload`, `/compras`, `/entrar`, `/checkout/[id]`.

### 2.2 Auth (`isAuth`)
- **Hoje:** cadastro (nome, e-mail, senha ≥ 6) ou login; validação local; `gate()` manda o visitante para o cadastro com um aviso ("Crie uma conta grátis para baixar…") e **volta para onde estava** (`authReturn`); "Continuar sem conta".
- **Precisa:** Supabase Auth (e-mail+senha, Google, Apple), criação de `profiles` no signup (nome → `handle` por `handleOf()`), `returnTo` via query string, e-mail de confirmação opcional.

### 2.3 Explorar (`isExplore`)
- **Hoje:** busca por criador/categoria/título; carrossel de criadores; grade cronológica de todas as mídias com selos (preço, vídeo+duração, cadeado).
- **Precisa:** `GET /api/explore?q=` (full-text em título/categoria/nome), paginação infinita, miniaturas 400 px servidas por CDN, ordenação por `created_at`. Visitante vê tudo exceto o próprio perfil (regra do protótipo).

### 2.4 Perfil (`isProfile`)
- **Hoje:** capa + avatar (arrastar imagem), contadores (publicações, seguidores, downloads), bio, botões (meu perfil: Editar/Publicar; outro: Seguir/Compartilhar), **categorias como "destaques" circulares**, grade filtrada por categoria, modal Editar perfil (nome, bio).
- **Precisa:** `profiles` (nome, handle, bio, avatar_url, cover_url), `follows`, contagens materializadas (ou view), upload de avatar/capa com crop, categorias = `galleries` do perfil, compartilhar = `navigator.share`/copiar `https://<dominio>/@handle`.

### 2.5 Publicação / Foto (`isPhoto`)
- **Hoje:** mídia grande (proporção real), autor + seguir, título, meta (resolução, formato, duração, downloads), data, ações (curtir, baixar/comprar, compartilhar), preço, curtidas (simuladas = downloads × 1,7), **estados:** grátis (baixar), paga e não comprada (prévia borrada + "Desbloquear por R$"), comprada (baixar), minha (alternar "Cobrar R$ 15 / Tornar grátis" + "Baixar original" + "recebidos"), vídeo (play simulado com barra de progresso).
- **Precisa:** `GET /api/media/:id`; **prévia gerada no servidor** (1080 px, borrada ou com marca-d'água se paga — o original nunca chega ao cliente antes do pagamento); download = URL assinada curta para o original, registrado em `downloads`; `likes` reais; vídeo com player HLS e prévia 480 p; edição de preço pelo dono.

### 2.6 Checkout (`isCheckout`)
- **Hoje:** resumo da mídia, três métodos: **Pix** (QR + código copia-e-cola simulado, "expira em 30 min"), **Cartão** (validação de 16 dígitos/MM/AA/CVV), **Carteira Revela** (saldo, "após a compra", "Adicionar R$ 50"); "Confirmando pagamento…" 1,6 s; tela de sucesso com "Baixar em alta resolução" e "Ver minhas compras".
- **Precisa:** provedor de pagamento com **Pix real** (Mercado Pago / Asaas / Pagar.me) ou Stripe: criar cobrança → QR e copia-e-cola reais → **webhook** confirma → `orders.status = paid` → `purchases` liberada → repasse (90 %) para o saldo do autor; cartão via checkout do provedor (não guardar dados de cartão); carteira = tabela `ledger` (créditos por venda/top-up, débitos por compra), top-up também via Pix. A tela de "confirmando" vira polling/Realtime do status do pedido.

### 2.7 Publicar / Upload (`isUpload`)
- **Hoje:** alterna Foto/Vídeo, área de arrastar, título, categoria (com chips das minhas categorias), toggle "Cobrar pelo download" com preço e "Você recebe R$ X (taxa de 10 %)", validações, botão "Do Estúdio" (vem com `fx` da edição IA).
- **Precisa:** upload direto para o storage por URL assinada (multipart/retomável para 50 MB de foto e 500 MB de vídeo), job de ingestão (EXIF, dimensões, miniatura, prévia, duração/transcode), criação da `media` com preço e categoria; quando vem do Estúdio, a mídia publicada é a **derivada** (não o original do drive).

### 2.8 Estúdio (`isStudio`) — o diferencial
- **Hoje:** drive com pastas e arquivos (seleção múltipla, "Selecionar toda a pasta", "Nova pasta", "Enviar arquivos" simulado); painel "Editar com IA" com **6 presets** (Retoque natural, P&B editorial, Cores vivas, Luz dourada, Cinema frio, Vintage — implementados como **CSS filter**) + campo "Detalhes extras"; progresso por arquivo; resultados com **comparar antes/depois** (toque), Publicar um a um ou "Publicar todas" (grátis, categoria = nome da pasta), Descartar, Nova edição; texto-chave: "Os originais não são alterados. Você revisa cada edição antes de publicar."
- **Precisa:** `folders`/`files` reais; **jobs** na fila processados pelos **workers Python do estúdio**; presets mapeados para modelos reais (tabela abaixo); "Detalhes extras" interpretado pelo Claude em ajustes de parâmetros; **prévia obrigatória em amostras antes do lote** (regra da spec); resultados = `derivatives` com antes/depois servidos como imagens reais; publicar cria `media` apontando para a derivada.

| Preset do protótipo | Modelo real do estúdio | Observação |
|---|---|---|
| Retoque natural | **Correção natural** (+ Revelação fiel à câmera quando houver RAW+JPG) | aprovado por clientes |
| P&B editorial | **P&B granulado** | aprovado |
| Cores vivas | `grade_cine` saturação alta (novo preset leve) | |
| Luz dourada | **Low-key quente** (variação clara: sem escurecer tanto) | o look mais aprovado |
| Cinema frio | `cine_teal_orange` (sombras frias, pele quente) | "Duotone frio" puro foi reprovado — não usar |
| Vintage | `sepia` / film matte | |
| (novo) Spin blur | **Spin blur** centrado no rosto | 15/15 aprovado — merece entrar como preset |
| (novo) Posts com identidade | layouts `posts.*` | depende de paleta/logo no perfil (fase 5) |

### 2.9 Compras (`isPurchases`)
- **Hoje:** cartão da carteira (saldo + "Adicionar R$ 50"), resumo (n arquivos · n compras · gastos), lista de compras pagas e downloads grátis com botão baixar.
- **Precisa:** `purchases` + `downloads` + `ledger`; para o autor, uma aba **Vendas** (o protótipo mostra "recebidos" na foto, mas não tem tela de vendas/saque — adicionar).

### 2.10 Toast, modal, acessibilidade
- Toasts informativos, modal de perfil, `aria-label` em todos os controles: manter.

---

## 3. Modelo de dados (derivado do estado do protótipo + spec)

```
profiles      id, user_id, name, handle (único), bio, avatar_key, cover_key,
              kind (photographer|institution|person), palette jsonb, logo_key, created_at
follows       follower_id, followed_id, created_at
galleries     id, profile_id, name (= categoria), visibility, created_at
media         id, profile_id, gallery_id, kind (photo|video), title, price_cents (0 = grátis),
              original_key, preview_key, thumb_key, width, height, duration_s, bytes,
              derivative_id (quando veio do Estúdio), downloads_count, likes_count, created_at
likes         profile_id, media_id
folders       id, profile_id, name
files         id, folder_id, original_key, name, width, height, bytes, exif jsonb, faces jsonb,
              sharpness, thumb_key, created_at
models        id, name, description, engine (local|higgsfield), params_schema, requires_credits,
              enabled_default, order
jobs          id, profile_id, model_id, mode (preview|batch), params jsonb, prompt text,
              status (queued|running|done|failed), progress, cost_credits, created_at
job_items     job_id, file_id, status, derivative_id, error
derivatives   id, file_id, job_id, model_id, key, width, height, params jsonb, created_at
orders        id, buyer_id, media_id, amount_cents, fee_cents, method (pix|card|wallet),
              provider, provider_ref, pix_qr, pix_code, expires_at, status, paid_at
purchases     buyer_id, media_id, order_id, created_at
downloads     profile_id, media_id, created_at
ledger        id, profile_id, kind (sale|purchase|topup|payout|fee), amount_cents, order_id, created_at
taste_profiles profile_id, kept jsonb, rejected jsonb, rules jsonb
```

Regras do protótipo que viram constraints: taxa da plataforma **10 %** (`fee_cents = round(amount × 0,10)`); download grátis exige conta; comprador baixa quantas vezes quiser; "Publicar todas" = grátis + categoria da pasta; preço mínimo > 0 quando pago.

---

## 4. Decisões técnicas para "deixar funcionando"

> **Revisado em 29/10 após ler o `fabrica-kit`** (ver `INFRA-EASYPANEL.md`): a infra passa a ser o
> **EasyPanel do dono**, com o método e as leis da Fábrica. Vercel/Supabase saem.

| Decisão | Escolha | Por quê |
|---|---|---|
| Frontend | **Next.js 15 (App Router) + React 18 + TypeScript**, convertendo o template tela a tela com os mesmos estilos (CSS Modules com os mesmos valores inline) | O dc-runtime é um runtime de protótipo. Precisamos de rotas reais, SEO para galerias públicas (`/@handle`), upload real e PWA. A conversão é mecânica: `sc-if` → `{cond && …}`, `sc-for` → `.map`, `{{ }}` → JSX, `style-hover/focus` → classes. |
| Infra | **EasyPanel** (Docker) do dono, provisionado pela API RPC como no `fabrica-kit`: projeto `revela` com `banco` (Postgres), `app` (Next.js, porta 3000), `worker` (Python) e `storage` (MinIO) | É onde os outros 20+ apps do dono rodam; método, scripts e leis já existem; zero conta nova para os primeiros testes. |
| Banco e auth | **Postgres** nativo do EasyPanel (URL interna) + **Auth.js** (e-mail/senha, Google) com Drizzle | 1 Postgres por projeto (regra do kit); sem BaaS externo. |
| Storage | **MinIO** no EasyPanel (S3) nos testes → **Bunny Storage + CDN** ou **Cloudflare R2** em produção (mesma API S3, troca por env) | Egresso de downloads é o custo que explode; a Fábrica já opera Bunny/Cloudflare. |
| Workers | **Python 3.11** (motor do estúdio) em contêiner no mesmo projeto, lendo `jobs` no Postgres (`SKIP LOCKED`) e gravando `derivatives`; progresso por SSE/polling | Reaproveita os 17 pipelines; sem Redis até precisar. |
| Pagamentos | **Gateway Pix que a Fábrica já usa (Vizzion/ApexPay)**: cobrança → webhook fail-closed e idempotente → libera download; payout Pix ao fotógrafo pelo mesmo gateway. Alternativa: Mercado Pago. | Integração e armadilhas já conhecidas (memórias `conc-gateway`, `fabrica-deposito-fixes`). PIX estático não serve (precisa liberar na hora). |
| IA | **Claude API** (`claude-sonnet-5-5`) para "Detalhes extras" → parâmetros, curadoria visual e QA; **Higgsfield API** só para camadas de efeito/relight opt-in | Conforme a spec (§4). |
| Deploy | `provisionar-revela.mjs` (mesma API do kit) → URL de teste `revela-app.<painel>.easypanel.host`; domínio oficial apontado pelo dono depois (`certificateResolver: ""`) | Lei do kit: teste no subdomínio, domínio é manual do dono. |
| Borda/segurança | Bunny ou Cloudflare só quando o dono pedir, com o playbook do kit (Log antes de Block, nunca cachear `/api`, IP real por header) | Duas quedas totais da Fábrica vieram da borda. |
| PWA/push | Kit `fabrica-app` (manifest, sw, InstallBanner, Web Push com VAPID) adaptado ao Next | Já resolvido no Get Taxi; iPhone só PWA. |
| Observabilidade | Sentry (web + worker) + tabela `jobs` como trilha de auditoria | Cada lote tem rastro e custo. |

---

## 5. Plano de execução (ordem e critérios de pronto)

| Fase | Entrega | Pronto quando | Estimativa |
|---|---|---|---|
| **0 · Fundação** | Repo `revela` (Next.js + TS + Drizzle + Auth.js + Dockerfile; `worker/` Python com Dockerfile), `provisionar-revela.mjs` cria no EasyPanel o projeto `revela` com `banco`, `storage` (MinIO), `app` e `worker`, env gerado e salvo, domínio de teste, deploy; migrações no boot; seed com fotos reais. | `https://revela-app.<painel>.easypanel.host` abre Explorar com dados de exemplo; login funciona. | 2 dias |
| **1 · Telas de leitura** | Converter Explorar, Perfil, Foto, Auth, header/tab bar, toast, modal; dados reais via Supabase; seguir/curtir; busca. | Você cria conta, edita perfil, vê perfis e fotos de teste (semeadas com as fotos do Betfage). | 4 dias |
| **2 · Upload e publicação** | Upload assinado (foto/vídeo), job de ingestão (dimensões, EXIF, miniatura 400, prévia 1080 borrada/marca-d'água quando paga, duração), tela Publicar completa, download grátis com URL assinada e registro. | Publica uma foto grátis e outra paga; a paga aparece borrada para outro usuário; o download grátis exige conta e baixa o original. | 4 dias |
| **3 · Estúdio + workers** | Drive (pastas/arquivos/upload em lote), fila de jobs, worker Python com 7 presets (6 do protótipo + Spin blur), **prévia em 3–5 amostras → lote**, comparar antes/depois, publicar uma/todas, "Detalhes extras" via Claude. | Seleciona 20 fotos, roda "Luz dourada", vê progresso em tempo real, compara, publica. Originais intactos. | 6 dias |
| **4 · Pagamentos** | Mercado Pago sandbox: Pix (QR + código), cartão (checkout do provedor), webhook → liberação; carteira/ledger com top-up via Pix; tela Compras; aba Vendas do autor; e-mails de recibo (Resend). | Compra uma foto por Pix no sandbox, é liberada, baixa; autor vê saldo 90 %. | 4 dias |
| **5 · Acabamento para testes públicos** | PWA (instalável, offline básico), compartilhar nativo, SEO/OG das galerias, notificações, perfil institucional com paleta/logo, posts com identidade (primeiros 3 layouts), métricas. | Grupo de teste (uma igreja + dois fotógrafos) usa por uma semana sem suporte manual. | 5 dias |
| **6 · Depois** | Vídeo HLS completo, app nativo (Capacitor/Expo), relight opt-in, perfil de gosto, planos pagos. | | — |

Total até os testes públicos: **~5 semanas** de trabalho contínuo. As fases 1–2 já dão algo para você mostrar; a 3 é o diferencial; a 4 destrava receita.

---

## 6. O que preciso de você para começar (nesta ordem)

> Revisado após o `fabrica-kit` — detalhe em `INFRA-EASYPANEL.md`.

1. **EasyPanel:** `EASYPANEL_URL`, `EASYPANEL_API_TOKEN` (Settings → API), `EASYPANEL_APPS_DOMAIN`, `EASYPANEL_HOST_IP` — no `.env` local, nunca no chat (se passar, rotacionar).
2. **GitHub:** repositório `flaviolimadev/revela` vazio, com o EasyPanel autorizado a lê-lo (mesma integração dos outros apps) — ou autorização para eu criar.
3. **Gateway Pix da Fábrica (Vizzion/ApexPay):** credenciais de teste, ou de produção para uma prova de fogo de R$ 1,00 (fase 4; até lá o checkout fica simulado). Alternativa: Mercado Pago sandbox.
4. **Anthropic:** chave da Claude API com limite mensal.
5. **Higgsfield:** chave de API de servidor (o CLI do Mac usa OAuth da sua conta e não serve para o worker) — fase 3, opcional nos primeiros testes.
6. **Domínio:** o protótipo usa `revela.app`; até você apontar, o teste vive em `revela-app.<painel>.easypanel.host`.
7. **Resend** (e-mails transacionais) — fase 4.

Com os itens 1 e 2 eu provisiono e entrego a URL de teste no mesmo dia.
9. **Decisões:** taxa da plataforma (o protótipo diz **10 %**; a spec sugeria 15–20 %); manter "Carteira Revela" com top-up (exige pagamento real para adicionar saldo); preço mínimo por foto; categorias livres (como no protótipo) ou pré-definidas; limites de upload (protótipo: foto 50 MB, vídeo 500 MB/3 min).

---

## 7. Riscos e cuidados vistos no template

- **IA "de mentira":** os presets são `CSS filter`; no produto a edição é no servidor e demora segundos por foto — a interface já prevê progresso por arquivo, basta ligar ao Realtime.
- **Prévia borrada no cliente é insegura:** o protótipo aplica `blur` por CSS sobre a imagem; na versão real a prévia **nasce** em baixa resolução no servidor e o original só sai por URL assinada após compra.
- **Pix e carteira simulados:** "Adicionar R$ 50" e o código Pix são fixos; precisam de provedor real e webhook (sem isso não há como liberar compra com segurança).
- **Vídeo:** reprodução simulada por timer; o real exige transcodificação (ffmpeg) e player HLS; vale deixar vídeo para a fase 5 e lançar com fotos.
- **Imagens arrastáveis (`image-slot`)** viram upload real com crop para avatar/capa.
- **Contagem de curtidas** é derivada de downloads; no real é tabela própria.
- **Sem tela de vendas/saque** para o autor — acrescentar (aba em Compras ou no Perfil).
- **Sem termos/privacidade/consentimento de imagem** — necessário antes de testes públicos (LGPD).

---

## 8. Como vou converter o template (método)

1. Para cada `data-screen-label` gero um componente em `app/(telas)/…` mantendo o HTML e os estilos inline convertidos em classes (mesmos px, cores e raios).
2. `renderVals()` vira: estado de servidor (consultas Supabase por rota) + estado de cliente (seleções, formulários) + ações (server actions / rotas de API).
3. `<image-slot>` → componente `<Media>` que recebe `thumb_key`/`preview_key` e resolve URL (pública para thumbs, assinada para originais).
4. Fluxos com temporizador (pagamento, IA) → assinaturas Realtime nas tabelas `orders` e `jobs`.
5. Os dados simulados viram **seed** de desenvolvimento (4 perfis, 18 mídias) usando fotos reais já editadas do Betfage, para a demo não ficar com quadrados coloridos.
