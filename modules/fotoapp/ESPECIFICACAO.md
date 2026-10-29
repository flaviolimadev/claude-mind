# FotoApp (nome provisório) — do estúdio ao produto

> Especificação funcional e técnica de uma **rede social para publicar e comercializar fotos**,
> cujo diferencial é um **drive interno com edição por IA em "modelos" prontos** — os mesmos
> modelos que o estúdio já aplica hoje, destilados de 4 projetos reais (Ensaio Gabi/Ismael,
> ChronosLab, Aviva Senhoras, Mocidade Betfage). Cada decisão abaixo traz o **porquê**: ou é uma
> dor observada no trabalho real, ou um feedback literal de cliente, ou um custo/limite medido.

Versão 0.1 · 29/out/2026 · fonte da verdade: `claude-mind/modules/fotoapp/` · motor:
`claude-mind/modules/estudio-fotografia/`

---

## 0. Resumo em um parágrafo

Fotógrafos, igrejas e ministérios sobem suas fotos e vídeos para um **drive dentro do app**,
escolhem um **modelo de edição** (ex.: *Revelação fiel à câmera*, *Low-key quente*, *Spin blur*,
*Posts com a identidade do evento*), a IA edita em lote **sem alterar as pessoas**, e o resultado
vai direto para a **galeria pública do perfil**, onde qualquer pessoa pode **baixar grátis ou
pagar** para baixar a foto/arte em tamanho original. O app junta, no mesmo lugar, o que hoje é
feito em quatro ferramentas separadas (câmera → computador → editor → Drive/WhatsApp) e
monetiza o que hoje é entregue de graça.

---

## 1. Por que este produto (as dores vistas de perto)

| Dor observada no estúdio | Evidência | O que o app resolve |
|---|---|---|
| **Entrega é gargalo.** A última entrega do Betfage foram **15 GB** (1.340 arquivos de câmera + 642 editadas + 128 posts) arrastados **manualmente** para o Google Drive, porque o Drive web bloqueia upload automatizado de pastas. | Sessões de 28/10: duas vezes a saída foi "você arrasta manualmente". | Upload único para o drive interno; publicação e distribuição acontecem no mesmo lugar. |
| **Cliente quer a foto REAL, no tamanho original.** Qualquer "filtro", corte ou IA que mude pessoa ou ambiente é reprovado na hora. | "Não modifique a foto em hipótese alguma", "sem IA", "você recortou as imagens? deveria ter mantido o tamanho original". | Modelos que só revelam/estilizam **sem tocar em pessoas** e sempre entregam **6000×4000**; cortes só em artes/posts. |
| **Cliente oscila e aprova por amostra.** Gastamos ~37 créditos de IA num lote inteiro ("amei") que foi descartado no mesmo dia ("sem IA"). | Betfage, 28/10. | Fluxo obrigatório: **prévia em 3–5 fotos → aprovar → lote**. Nunca lote antes de aprovar. |
| **Posts precisam da identidade do evento**, não da cor da referência. | "Algumas ficaram com tons verde; mantenha a paleta e a identidade; use a arte da camisa como textura." | Perfil do evento guarda **paleta + logo/arte** e os modelos de post usam isso automaticamente. |
| **Curadoria é visual e por número.** O cliente revisa em pranchas numeradas e cita "foto 01, 02…"; apaga o que não gosta e o que foi apagado **nunca pode voltar**. | "Reúna tudo em um único lugar"; lista de rejeitados. | Galeria com índice, aprovação/rejeição por clique, rejeitados ficam fora para sempre. |
| **O "gosto" do cliente é aprendível.** Em uma noite ficou claro: movimento ao redor de um rosto nítido = sim; anéis/molduras/perspectiva = não; boca escancarada = não; primeiro plano tampando = não. | 46 mantidos de 75 → padrão explícito. | Perfil de gosto por cliente alimenta sugestões (quais fotos, quais modelos). |
| **Trabalho pesado é local e frágil.** Pastas de trabalho (`hf/`, `full/`) foram apagadas no meio do processo por limpeza de espaço. | 28/10, noite. | Processamento em servidor com fila; originais e derivadas em storage de objetos, nada depende do disco do fotógrafo. |

---

## 2. O produto

### 2.1 Quem usa

| Persona | O que faz no app | Como ganha/paga |
|---|---|---|
| **Fotógrafo profissional** | Sobe o evento, edita por modelos, publica galeria, define preço por foto/pacote, divulga portfólio. | Recebe pelas vendas (menos a comissão da plataforma). Pode assinar plano com cota de edições IA. |
| **Igreja / ministério / conjunto** | Perfil institucional com **identidade** (paleta, logo, arte da camisa); publica cultos e eventos; libera fotos **grátis** para os membros; encomenda posts prontos. | Grátis ou plano institucional (armazenamento + edições). |
| **Membro / visitante** | Segue perfis, vê galerias, **baixa grátis** ou **compra** fotos em tamanho original, salva favoritas. | Paga por foto/pacote quando o autor cobra. |

### 2.2 Objetos principais

- **Perfil** (pessoa, fotógrafo, instituição) com identidade visual opcional: paleta (hex), logo/arte (PNG com alpha), tipografia, "regras" (ex.: sem texto, sem IA em pessoas).
- **Evento/Galeria**: conjunto de mídias de um dia/culto/ensaio; privacidade (pública, só seguidores, link); política de download (grátis / pago por foto / pacote).
- **Mídia**: original (RAW/JPG/vídeo) + derivadas (revelada, estilizadas por modelo, cortes, miniaturas, prévia com marca-d'água).
- **Modelo de edição**: receita versionada (parâmetros + código) com nome, descrição para leigo, exemplo antes/depois, custo (0 ou créditos IA), restrições ("não altera pessoas").
- **Job**: aplicação de um modelo a N mídias (prévia ou lote), com progresso e QA.
- **Pedido/Download**: compra ou download gratuito; recibo; licença de uso.

### 2.3 Jornada principal (fotógrafo)

1. **Upload** para o drive (arrasta pasta; aceita CR3/RAW + JPG + MP4). *Por quê:* a câmera grava RAW+JPG e o JPG da câmera é a referência de cor que o cliente reconhece (§3.1).
2. **Organização automática**: miniaturas, agrupamento por cena, nota de nitidez, detecção de rostos, sugestão de culling. *Por quê:* 670 fotos viraram 642 entregues só depois de culling + pedido do cliente; o app sugere, o humano decide.
3. **Escolher modelo** → o app gera **prévia em 3–5 fotos representativas** (uma por tipo de cena). *Por quê:* lição dos 37 créditos.
4. **Aprovar → lote** em servidor (fila). Progresso visível; cada foto sai **no tamanho original**.
5. **Revisar em grade numerada**, apagar o que não gostou (vai para "rejeitados", nunca volta), pedir "mais 20 assim" (o app usa o perfil de gosto).
6. **Publicar** na galeria com política de download; opcionalmente gerar **posts** (modelos de layout com a identidade do perfil) e **stories 9:16**.
7. **Vender/entregar**: membros baixam; fotógrafo acompanha vendas e downloads.

### 2.4 Jornada do comprador

Descobre o perfil → galeria → vê prévias (marca-d'água discreta se pago) → baixa grátis ou paga
(Pix/cartão) → recebe o arquivo original + recibo → pode seguir o perfil e ser avisado de novos
eventos.

---

## 3. O motor: catálogo de modelos que já existem (e o porquê de cada um)

Tudo abaixo já roda hoje como pipelines Python (PIL + numpy, sem GPU) em
`modules/estudio-fotografia/pipelines/`. Marcado **✔ aprovado** = passou pelo crivo de cliente
real; **✖ reprovado** = existe, mas não deve ser oferecido como padrão.

### 3.1 Revelação (a base de tudo)

| Modelo | O que faz | Por quê | Origem |
|---|---|---|---|
| **Revelação fiel à câmera** ✔ | Casa o RAW convertido (full-res) com o JPG que a própria câmera gravou (histogram-matching global por canal) + abertura mínima de sombras em cenas escuras. Saída 6000×4000. | A conversão RAW padrão sai escura e lavada; o cliente quer "a foto como foi batida". Régua = a câmera, não um alvo numérico. QA automático: brilho dentro de ±0,06 do JPG da câmera. | `revelar_fiel_camera.py` · memo `estudio-revelar-fiel-camera` |
| **Correção natural** ✔ | Exposição com trava de highlight, balanço de branco por neutros, contraste mínimo. Sem grão/vinheta. | Feedback literal em dois projetos: "filtro horrível, deixe natural", "só ajustar as cores, o mais real possível". | `correcao_cores.py` |

### 3.2 Estilos sobre a foto inteira (sem corte, sem tocar nas pessoas)

| Modelo | O que faz | Por quê | Status |
|---|---|---|---|
| **Low-key quente** | Escurece (gamma 1,3), pretos profundos, S-curve, leve quente, bloom nas luzes, poeira dourada e feixe (camadas IA em screen), vinheta centrada no rosto. | É o look das referências de "igreja cinematográfica"; o cliente manteve 14 de 18 e pediu +60. Saída no tamanho original. | ✔ aprovado |
| **Spin blur** | Rotação média (±7°) ao redor do **rosto principal**, que fica 100 % nítido; quente leve; poeira. | Manteve 15 de 15 — "amei". Rosto nítido + movimento é a assinatura do gosto deste público. | ✔ aprovado |
| **P&B granulado** | Luminância com S-curve forte, grão 0,05. | Referência de "multidão de jovens de preto"; mantido no post de bandas. | ✔ |
| **Anéis de prisma** | Anéis de luz/prisma (camada IA) centrados no rosto + grade film quente. | Bonito nas referências, mas o cliente apagou 16 de 17: **enfeite por cima da pessoa** incomoda. | ✖ opcional, desligado por padrão |
| **Duotone frio** | Monocromático azul-petróleo. | "O efeito azul ficou feio, exclua." | ✖ não oferecer |
| **Relight híbrido (cenário IA + pessoas reais)** | IA re-ilumina a cena; pessoas voltam dos pixels originais por máscara. | Tecnicamente funciona (prova por mapa de diferença), mas o cliente quer "sem IA" e sente "cara de IA" no ambiente. Custa 0,25 cr/foto. | ✖ experimental, só com aviso |

**Regra de ouro (vale para todos):** pessoas e ambiente são pixels originais; a IA, quando entra,
entra como **camada de efeito em fundo preto** (anéis, poeira, feixe, névoa) aplicada por screen.
Seis camadas geradas uma única vez (1,5 crédito) servem para o projeto inteiro → **custo marginal
zero por foto**.

### 3.3 Enquadramento por rosto

Todo corte, vinheta, centro de blur e posição de anel usa o **rosto principal** detectado, pontuado
por tamanho × nitidez × não-cortado × proximidade do centro (o maior rosto pode ser alguém
desfocado em primeiro plano). *Por quê:* "as fotos ficaram mal enquadradas, deveria mostrar o
rosto" — o centro da máscara de pessoa cai em mãos erguidas. Hoje usa o Vision do macOS
(`faces_vision.swift`); no servidor vira MediaPipe/InsightFace (§5.3).

### 3.4 Posts e artes (aqui sim há corte e composição)

| Família | O que faz | Por quê |
|---|---|---|
| **17 layouts de igreja** (`posts_igreja_tema.py`) | Cards arredondados, fatias verticais, bandas, grade em papel, polaroid, radial/spin com frase, mosaico, split, leque, countdown, editorial… | Destilados de 19 referências estudadas elemento a elemento (`ESTUDOS.md`). Texto só quando o cliente libera o conteúdo. |
| **7 layouts "refs 2"** (`posts_refs_paleta.py`) | Mesmos princípios + **paleta e arte oficial do cliente como textura de fundo**, enquadramento por rosto. | "Mantenha a paleta do aniversário; use a arte da camisa com textura no background." |
| **Artes com título** (M1–M4) | "33 ANOS", "REVESTIDOS DE AUTORIDADE": título branco pesado, levemente inclinado, foto real low-key como fundo, pessoa por cima/por baixo do texto via máscara. | Aprendido na marra: perspectiva/trapézio, fundo preto artificial e parede clara foram reprovados; "texto igual da referência" = sólido, pesado, pouco efeito. |
| **Álbum PDF, cortes 4:5 / 9:16, vídeos** (`album_pdf.py`, `crop_posts.py`, `video_*.py`) | Diagramação, stories e slideshows (Ken Burns, zoom-through). | Entregas dos projetos Ismael/Gabi. |

### 3.5 Regras de gosto aprendidas (viram "lint" do app)

1. Rosto e ambiente **nunca** alterados; foto com efeito **sempre** no tamanho da câmera.
2. Prévia em amostras antes de qualquer lote (IA ou não).
3. Evitar boca escancarada em close/solo; preferir olhos fechados, mãos erguidas, oração. Coral cantando **em grupo** é aceito.
4. Sem primeiro plano tampando, sem plano aberto vazio.
5. Geometria reta e ordenada; nada de molduras, números, recortes ou formas **sobre** as pessoas.
6. Cor vem da identidade do cliente, não da referência; verde/laranja/petróleo fora quando a paleta é navy + dourado.
7. O que o cliente apagou não volta (lista de rejeitados por projeto).

---

## 4. Como a IA entra (e o que cada API faz)

### 4.1 Claude API — o "cérebro" do fluxo

| Uso | Modelo sugerido | Por quê |
|---|---|---|
| **Interpretar o pedido do usuário** em linguagem natural ("quero as fotos do coral orando, estilo escuro") → escolher modelo, parâmetros e quais fotos. | `claude-sonnet-5-5` | É exatamente o que fiz nas sessões: traduzir "mais natural", "sem cara de IA", "preserve o ambiente" em parâmetros. |
| **Curadoria assistida com visão**: descrever cada foto (quem, expressão, boca aberta/olhos fechados, mãos erguidas, nitidez, primeiro plano tampando) e pontuar contra as regras de gosto (§3.5). | `claude-sonnet-5-5` (visão) em miniaturas 1400 px; `claude-haiku-5-5` para volume. | O culling por nitidez não vê "boca escancarada"; o cliente vê. |
| **QA antes/depois**: comparar original × editada e sinalizar alteração de rosto/ambiente, corte indevido, texto cortado. | `claude-sonnet-5-5` | Todo erro grave desta semana teria sido pego por um olhar antes de enviar. |
| **Textos**: legendas, títulos de galeria, hashtags, descrição do evento, mensagens ao comprador. | `claude-haiku-5-5` | Barato e suficiente. |
| **Prompts para o Higgsfield** (camadas de efeito, relight experimental) e **leitura de referências** novas enviadas pelo usuário (desconstruir layout/efeito em parâmetros). | `claude-sonnet-5-5` / `claude-opus-5-5` para referências complexas | Foi o processo de `ESTUDOS.md`: referência → termos técnicos → receita. |
| **Assistente do fotógrafo** (chat dentro do app) e **suporte**. | `claude-sonnet-5-5` | Mesma conversa que temos hoje, dentro do produto. |

Custo típico: miniaturas de 1400 px ≈ 1,5k tokens de imagem cada → curadoria visual de 600 fotos ≈ 1M tokens de entrada (centavos de dólar por evento no Haiku, poucos dólares no Sonnet).

### 4.2 Higgsfield API — o gerador de camadas/plates

| Uso | Modelo | Custo medido |
|---|---|---|
| **Camadas de efeito** em fundo preto (anéis, prisma, poeira, feixe, névoa, light leaks) — geradas **uma vez por estilo**, reutilizadas em todas as fotos. | `gpt_image_2_5`, 2:3 ou 3:2 | 0,25 cr cada; 6 camadas = 1,5 cr |
| **Relight experimental** (cenário IA + pessoas reais) — opt-in com aviso. | `gpt_image_2_5` com a foto como `image_references`, 1 por request, lotes de 12. | 0,25 cr/foto |
| **Upscale 4K** de plates/artes geradas (saída nativa ~1024 px). | bytedance 4K | 2 cr |
| **Imagem → vídeo** (dar vida a foto) — só a pedido, rostos derivam. | `seedance1_5` 4 s/1080p | 12 cr |
| Texturas/fundos sem pessoas para artes (couro, papel, luz) quando o cliente não fornece. | `gpt_image_2_5` | 0,25 cr |

Hoje o acesso é via **MCP** (ferramentas `media_upload` → PUT → `media_confirm` → `generate_image_batch` → `jobs_wait` → download do CDN). No produto precisa ser **API REST/SDK com chave de servidor** — item nº 1 da lista do §6.

### 4.3 O que roda **sem** IA paga (custo zero por foto)

Revelação, correção, low-key, spin blur, P&B, posts/colagens, cortes, álbum, vídeos, detecção de
rosto, máscara de pessoa (rembg/u2net, aberto), culling. Isso é a maior parte do valor — e é o que
o cliente aprovou. Tempos medidos num Mac M-series: revelação ~1–2 s/foto; estilo em 6000×4000
~20–30 s/foto (3 em paralelo → 109 fotos em ~25 min); máscara ~5 s/foto; rosto 0,3 s/foto.

---

## 5. Arquitetura proposta

### 5.1 Visão geral

```
[App web/PWA (template Claude Design)]
        │  HTTPS / WebSocket (progresso)
[API] ──┼── Auth ── Banco (Postgres) ── Pagamentos (webhooks)
        │
        ├── Storage de objetos (originais, derivadas, prévias) + CDN
        │
        └── Fila de jobs ──► Workers Python (motor do estúdio: PIL/numpy/rembg)
                              ├── Claude API (curadoria, QA, textos, interpretação)
                              └── Higgsfield API (camadas, relight opt-in, upscale)
```

*Por quê separar workers:* o processamento é pesado (6000×4000, minutos por lote) e não pode
depender do computador do fotógrafo nem travar a API. A fila dá progresso, reprocessamento e
paralelismo.

### 5.2 Componentes e escolhas recomendadas

| Camada | Recomendação | Por quê |
|---|---|---|
| Frontend | **Next.js/React** a partir do template do Claude Design, PWA (instala no celular). | Um código para web e celular no MVP; app nativo depois, quando houver tração. |
| API | **Node (NestJS/Fastify)** ou **Python (FastAPI)**. Se os workers são Python, FastAPI simplifica compartilhar o motor. | O motor já é Python. |
| Workers | **Python 3.11 + PIL + numpy + rembg (onnxruntime) + rawpy/LibRaw**; fila **Redis + RQ/Celery**; 1 worker por núcleo. | Reaproveita 17 pipelines existentes. |
| Banco | **Postgres** (Supabase ou Neon). | Relacional simples: perfis, galerias, mídias, jobs, pedidos. |
| Auth | **Supabase Auth** ou **Clerk** (e-mail, Google, Apple). | Pronto, seguro, com login social que igreja/membro já usa. |
| Storage | **Cloudflare R2** (S3-compatível, **sem taxa de egresso**) + CDN. | O produto **vende downloads**: egresso é o custo que explode no S3. |
| Pagamentos | **Stripe** (cartão, Pix via Stripe BR) ou **Mercado Pago / Asaas / Pagar.me** (Pix nativo, split para o fotógrafo). | Público brasileiro paga por Pix; split automatiza o repasse. |
| Vídeo | Transcodificação com **ffmpeg** nos workers; HLS para reprodução. | Igrejas publicam vídeos; já usamos ffmpeg nos slideshows. |
| E-mail/notificações | Resend/Postmark + push do PWA. | Avisar "suas fotos do culto saíram", recibo de compra. |
| Observabilidade | Sentry + logs por job (entrada, parâmetros, saída, custo IA). | Cada lote precisa de rastro: o que foi gerado, quanto custou, quem aprovou. |

### 5.3 Substituições obrigatórias (o motor hoje é macOS)

| Hoje (Mac) | No servidor Linux | Observação |
|---|---|---|
| `sips` converte CR3 → JPEG | **rawpy (LibRaw)** ou `dcraw`/`darktable-cli` | Testar suporte ao CR3 da câmera do cliente (Canon). Alternativa: **Mac mini como worker** (mantém sips e Vision, custo baixo, ótimo para MVP). |
| **Vision** (`VNDetectFaceRectanglesRequest`) | **MediaPipe Face Detector** ou **InsightFace/RetinaFace** (ONNX) | Manter a mesma pontuação do rosto principal (§3.3). |
| rembg/u2net | igual (onnxruntime CPU) | Já roda em Linux. |
| Fontes do macOS (Avenir Next Condensed, Impact, Snell) | Fontes livres equivalentes (Bebas Neue/Anton, Oswald, Great Vibes) ou licença | Os layouts dependem de condensadas pesadas e de uma script. |
| Caminhos fixos `~/Downloads/<projeto>/…` | Biblioteca `estudio/` com funções puras (bytes/paths de entrada, parâmetros, saída) + registro de modelos por id/versão | Refatoração necessária antes de plugar no app. |

### 5.4 Modelo de dados (resumo)

`users` · `profiles` (type, identity: palette[], logo_url, fonts, rules) · `galleries` (profile_id,
title, date, visibility, download_policy, price) · `media` (gallery_id, kind, original_key,
camera_jpg_key, width, height, sharpness, faces[], rejected_at) · `derivatives` (media_id,
model_id, model_version, key, width, height, params, cost_credits) · `models` (id, name, desc,
params_schema, requires_ai, default_enabled, examples[]) · `jobs` (profile_id, model_id,
media_ids[], mode: preview|batch, status, progress, cost) · `taste_profiles` (profile_id, kept[],
rejected[], derived_rules) · `orders`, `payments`, `downloads`, `follows`, `likes`, `comments`.

### 5.5 Fluxo técnico de um lote

1. Upload direto do navegador para o storage (URL assinada), em paralelo, com retomada.
2. Worker `ingest`: miniaturas (400/1400 px), EXIF, nitidez, agrupamento de cena, rostos, máscara sob demanda.
3. Usuário escolhe modelo → `job preview` (3–5 fotos escolhidas por cena/rosto) → grade antes/depois.
4. Aprovação → `job batch` → N tarefas na fila → derivadas no storage → QA automático (tamanho = original, Δ brilho, rosto intacto) → grade numerada.
5. Publicação → prévias com marca-d'água (se pago) → downloads servem o original via URL assinada após pagamento/gratuidade.

### 5.6 Monetização (proposta inicial)

- Comissão da plataforma sobre venda de fotos (ex.: 15–20 %) + taxa do meio de pagamento.
- Plano **Pro** para fotógrafos: mais armazenamento, edições IA incluídas, domínio/portfólio.
- Plano **Instituição** para igrejas: perfil verificado, membros ilimitados, posts com identidade.
- Créditos avulsos para modelos que consomem Higgsfield (relight, upscale, vídeo).

### 5.7 Legal e conteúdo

LGPD (fotos de pessoas identificáveis: termo de uso + remoção a pedido); direito de imagem em
eventos (igreja como responsável pelo consentimento dos membros); licença de uso da foto vendida
(pessoal × comercial); moderação de conteúdo; DMCA/retirada.

---

## 6. O que eu preciso de você

### 6.1 Chaves e contas (em ordem de urgência)

1. **Higgsfield — chave de API de servidor** (não o MCP) e confirmação de que a API expõe `gpt_image_2_5`, batch e upscale; plano/créditos para produção.
2. **Anthropic — chave da Claude API** (console.anthropic.com) com limite de gasto definido; usaremos `claude-sonnet-5-5` (visão/orquestração), `claude-haiku-5-5` (volume) e `claude-opus-5-5` (referências complexas).
3. **Pagamentos**: conta **Stripe** ou **Mercado Pago/Asaas/Pagar.me** (decisão: Pix nativo + split para o fotógrafo pesa a favor dos nacionais) — chaves de teste primeiro.
4. **Storage + CDN**: conta **Cloudflare** (R2) — ou AWS S3 + CloudFront se preferir.
5. **Banco + Auth**: projeto **Supabase** (Postgres + Auth + storage temporário) — ou Neon + Clerk.
6. **Hospedagem**: Vercel (frontend) + servidor para API/workers (Railway/Fly.io/Render/Hetzner) — **ou um Mac mini** como worker inicial (mantém sips/Vision, zero refatoração de RAW/rosto).
7. **Domínio** e remetente de e-mail (Resend/Postmark).
8. Contas de **loja de apps** (Apple Developer, Google Play) só quando formos para nativo.

### 6.2 Decisões suas

- Nome do produto e domínio.
- Web/PWA primeiro (recomendo) ou nativo desde o início.
- Comissão (%) e preços dos planos; preço mínimo por foto; o que fica grátis.
- Suporte a RAW no upload (sim, recomendo: é o que torna a *Revelação fiel à câmera* possível) e limite de tamanho por arquivo/evento.
- Quais modelos ficam **ativos por padrão** (sugestão: Revelação fiel, Correção natural, Low-key, Spin blur, P&B, Posts com identidade) e quais são **opt-in com aviso** (Relight híbrido, Anéis).
- Termos de uso / política de imagem (posso redigir o rascunho).

### 6.3 O que você vai me entregar

- O **layout do Claude Design** (template): a partir dele eu mapeio telas → rotas → componentes → endpoints e digo o que falta.
- Acesso ao repositório do app (ou crio um novo `fotoapp` dentro do seu GitHub).

### 6.4 O que eu faço com isso (plano de trabalho)

| Fase | Entrega | Prazo estimado |
|---|---|---|
| **0 — Motor como biblioteca** | Refatorar os 17 pipelines em `estudio/` (funções puras, registro de modelos, testes com as fotos do Betfage), substituir sips/Vision, Dockerfile do worker. | 1–2 semanas |
| **1 — MVP** | Auth, perfis, upload para drive, galerias, 6 modelos padrão com prévia → lote, grade de curadoria, download grátis, posts com identidade. | 3–4 semanas |
| **2 — Vendas** | Pagamentos (Pix/cartão), marca-d'água, pedidos, repasse, recibos, planos. | 2 semanas |
| **3 — Social + IA assistiva** | Seguir/curtir/comentar, feed, assistente Claude no app (curadoria visual, "mais 20 assim", textos), perfil de gosto. | 2–3 semanas |
| **4 — Vídeo e nativo** | Upload/transcode/HLS, stories 9:16 em lote, app nativo (Capacitor/Expo). | depois da tração |

---

## 7. Anexos

### 7.1 Mapa pipeline → módulo do app

| Pipeline (estúdio) | Módulo do app |
|---|---|
| `culling.py` | `ingest.cull` (nitidez, cenas, sugestão) |
| `rostos_vision.py` + `faces_vision.swift` | `ingest.faces` (server: MediaPipe/InsightFace) |
| `revelar_fiel_camera.py` | modelo `reveal_camera` |
| `correcao_cores.py` | modelo `natural_correction` |
| `efeitos_camada_ia.py` (A/C/D) | modelos `lowkey_warm`, `spin_blur`, `prism_rings` (opt-in) + `fx_layers` (gera/cacheia camadas via Higgsfield) |
| `grade_cine.py` | modelos `cine_teal_orange`, `bw_grain`, `sepia` (galeria de looks) |
| `hibrido_cenario_ia.py` | modelo experimental `relight_hybrid` (aviso + prévia obrigatória) |
| `posts_igreja_tema.py`, `posts_refs_paleta.py`, `posts_colagens.py`, `arte_composicao.py` | `posts.*` (layouts parametrizados por identidade do perfil; texto opcional) |
| `crop_posts.py` | `export.crops` (4:5, 9:16, 1:1 por rosto) |
| `album_pdf.py` | `export.album_pdf` |
| `video_kenburns.py`, `video_slides_2d.py`, `video_wedding_slides.py` | `video.slideshow` (ffmpeg) |

### 7.2 Memórias do estúdio que embasam esta spec

`estudio-workflow`, `estudio-regra-rosto`, `estudio-revelar-fiel-camera`, `estudio-rostos-vision`,
`estudio-efeitos-camada-ia`, `estudio-hibrido-cenario`, `estudio-higgsfield`, `estudio-culling`,
`estudio-cor-e-grade`, `estudio-album-e-cortes`, `estudio-videos`, casos Ismael/Aviva/Betfage.
