# Revela no EasyPanel — como o `fabrica-kit` encaixa

> Fonte: https://github.com/flaviolimadev/fabrica-kit (clone local `~/Downloads/fabrica-kit`,
> commit `4c69a38`). Analisado em 29/out/2026 para decidir como subir o Revela.

## 1. O que o kit é (em uma frase por peça)

| Peça | O que faz | Serve ao Revela? |
|---|---|---|
| `scripts/provisionar-easypanel.mjs` | Cria no **EasyPanel** (via RPC `POST {EASYPANEL_URL}/api/rpc/<proc>`, `Authorization: Bearer <token>`, body `{json:{…}}`): projeto → Postgres (`services/postgres/createService` + `inspectService` para pegar senha) → app (`services/app/createService` → `updateSourceGithub` → `updateBuild {type:'dockerfile'}` → `updateEnv`) → domínio (`domains/createDomain`, host `<projeto>-app.<APPS_DOMAIN>`, porta do container) → `deployService`. Idempotente; lista de projetos protegidos; nunca chama `destroy*`. | **Sim, é a receita.** Só que está moldado para Laravel (porta 8000, `APP_KEY`, `DB_*`, PIX estático) e lê `api/.env`. Para o Revela escrevo `provisionar-revela.mjs` com a mesma API: app Next.js (porta 3000) + worker Python + Postgres + MinIO. |
| `.claude/agents/*` (56) | Equipe: `fabrica-provisionamento` (API do EasyPanel), `fabrica-deploy`, `fabrica-dominio` (domínio/CDN só com pedido do dono), `fabrica-banco`, `fabrica-qa`, `designer`, `fabrica-app` (PWA/push), segurança (`seg-*`), conciliação PIX, vídeo, maestro. Carregam ao abrir o repo no Claude Code. | Reaproveito os de infra/QA/PWA/segurança. Os de negócio (rendimentos, MLM, saque, Mega Admin) não se aplicam. |
| `memoria-seed/*` (55) | Leis e receitas: deploy só HTTP 200 conta, `autoDeploy` inconsistente, cert custom com `certificateResolver: ""`, Bunny/Cloudflare na frente (nunca cachear `/api`, IP real via `X-Visitor-IP`/`CF-Connecting-IP`), PWA + Web Push, Higgsfield CLI, gateways Vizzion/ApexPay com webhook fail-closed e idempotente, PIX estático conciliado pelo e-mail do C6, Resend. | **Sim** — são as regras de operação da sua infra. |
| `INSTALAR.md` / `instalar.mjs` | Valida o `.env` (EasyPanel URL/token/domínio, chaves, Anthropic), copia a memória para o Claude Code, testa a API, imprime o plano. | O `.env` do kit é o que eu preciso de você (seção 4). |
| Mega Admin + app-molde (Laravel) | O produto da Fábrica (plataformas white-label). | Não é o Revela. Opcional: cadastrar o Revela como **conexão** do Mega Admin depois, para monitorar banco/usuários/pagamentos no painel que você já usa. |

## 2. Leis do kit que o Revela passa a obedecer

1. **Deploy sai no subdomínio de teste** `revela-app.<painel>.easypanel.host`; domínio oficial (`revela.app`) é apontado **por você** depois de aprovar — e com `certificateResolver` vazio.
2. **Só HTTP 200 em `deployService` conta como disparo**; 502 é transiente (re-tentar um por vez); 400 "canceled" = esperar assentar. Confirmar pelo `commit.sha` do `inspectService`.
3. **Fez → QA testou → validou → deployou.** Prova de fogo do Revela = *cadastrar → publicar foto paga → comprar por Pix (sandbox) → baixar original* ponta a ponta.
4. **Segredos só no `.env` local** (fora do git); token do EasyPanel que passar pelo chat → **rotacionar**. Nunca `git add -A` em repo com fotos soltas (push bloqueado por arquivo grande).
5. **Nunca destruir serviço**; idempotência (checar antes de criar); payloads descobertos pelo **OpenAPI do painel** (`GET /api/openapi.json`) ou espelhando um serviço que já funciona, nunca chutados.
6. Env no EasyPanel: **só linhas `KEY=VALUE`** (comentário derruba o container com 502).
7. CDN/borda (Bunny ou Cloudflare) só quando você pedir, com o playbook do kit (Log antes de Block, nunca cachear `/api`, webhooks de gateway fora de qualquer bloqueio de datacenter).

## 3. Topologia do Revela no EasyPanel (projeto `revela`)

```
revela/
├── banco    Postgres (serviço nativo; URL interna postgres://postgres:<senha>@revela_banco:5432/revela)
├── app      Next.js 15 (Dockerfile, porta 3000) — site, API (route handlers), Auth.js, uploads assinados
├── worker   Python 3.11 (Dockerfile em worker/) — motor do estúdio; lê a tabela jobs (SKIP LOCKED), grava derivadas
└── storage  MinIO (imagem minio/minio, volume) — S3 interno para originais/prévias/derivadas nos testes
             → produção: Bunny Storage + CDN ou Cloudflare R2 (mesma API S3, troca por env)
```

Por que assim: mantém a regra do kit "tudo em Docker no EasyPanel, 1 Postgres por projeto", evita
contas externas para os primeiros testes (MinIO roda ali mesmo) e separa o processamento pesado
(worker) do site. Fila em Postgres (sem Redis) para não adicionar serviço antes de precisar.

**Build/Deploy:** fonte GitHub `flaviolimadev/revela` (`main`), build Dockerfile. `app` e `worker` são
dois serviços apontando para o **mesmo repo** com Dockerfiles diferentes (descobrir no OpenAPI como
`updateBuild` aceita o caminho do Dockerfile; senão, dois repos ou `docker build` com `--target`).

**Env do `app` (mínimo para rodar):** `DATABASE_URL`, `AUTH_SECRET`, `AUTH_URL`, `S3_ENDPOINT`,
`S3_BUCKET_*`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `PUBLIC_BASE_URL`, `ANTHROPIC_API_KEY`,
`PAYMENT_GATEWAY` (vizzion|apexpay|mercadopago), `PAYMENT_API_URL/KEY/SECRET`, `WEBHOOK_TOKEN`,
`RESEND_API_KEY` (opcional), `PLATFORM_FEE_PCT=10`.

**Pagamentos:** reaproveitar o gateway que a Fábrica já usa (**Vizzion/ApexPay**: cobrança Pix →
webhook com token fail-closed no body → crédito idempotente com `lockForUpdate`; saque = payout Pix pelo
mesmo gateway). Alternativa se o gateway não tiver sandbox: **Mercado Pago**. PIX estático + conciliação
C6 **não** serve ao Revela (precisa liberar o download na hora).

## 4. O que preciso de você para já começar (o `.env` do kit, adaptado)

| # | Item | Onde pegar | Para quê |
|---|---|---|---|
| 1 | `EASYPANEL_URL`, `EASYPANEL_API_TOKEN`, `EASYPANEL_APPS_DOMAIN`, `EASYPANEL_HOST_IP` | Painel → Settings → API; domínio-base dos apps (ex.: `rwi2ck.easypanel.host`) | Provisionar projeto/banco/app/worker/storage e entregar a URL de teste. **Rotacionar o token** se ele passar pelo chat. |
| 2 | Repositório GitHub `flaviolimadev/revela` (vazio) com o EasyPanel autorizado a lê-lo (mesma integração dos outros apps) | GitHub → New repository | O EasyPanel builda a partir do GitHub (`updateSourceGithub`). |
| 3 | Credenciais do gateway Pix (Vizzion ou ApexPay) — de **teste** se existir; senão as de produção com um valor de R$ 1,00 para a prova de fogo | Painel do gateway | Checkout real com webhook (fase 4). Até lá o checkout fica em modo simulado. |
| 4 | `ANTHROPIC_API_KEY` | console.anthropic.com | "Detalhes extras" do Estúdio, curadoria, QA, textos. |
| 5 | `RESEND_API_KEY` + remetente | resend.com | Recibos e avisos (fase 4). |
| 6 | Higgsfield: chave de API de servidor (o CLI no seu Mac usa OAuth da sua conta — não serve para o worker) | higgsfield.ai | Camadas de efeito/relight (fase 3; opcional nos primeiros testes). |
| 7 | Decisões: nome/domínio `revela.app`; taxa 10 %; Carteira com top-up sim/não; limites de upload | — | Entram como env/constantes. |

Com os itens **1 e 2** eu já provisiono e entrego a URL de teste no mesmo dia (telas de leitura com
dados de exemplo). O resto entra por fase.

## 4.1 O que foi feito de fato (29/10/2026, 20h–20h40)

- Painel real: **`https://6sudfz.easypanel.host`** (custom `chokito.ctrlser.com`), IP `187.127.37.248`,
  serviços novos em **`*.app.ctrlser.com`** (wildcard DNS resolve em qualquer nível). Padrão da casa:
  serviços `<projeto>-frontend/-backend/-db`, domínios com `certificateResolver: ""`, builds nixpacks.
- API: `POST /api/rpc/<grupo>/<proc>` (ex.: `services/app/createService`, `domains/createDomain`,
  `git/generateKey`, `actions/listActions`, `actions/getAction` → **log de build completo em `.log`**).
  Payloads no OpenAPI `GET /api/openapi.json` (377 paths, nomes planos `createAppService`…).
- Projeto **`revela`**: `revela-db` (postgres:17, interno `revela_revela-db:5432`, db `revela`),
  `revela-storage` (**RustFS** `rustfs/rustfs:latest`, S3 em :9000, volume `/data`, domínio
  `revela-s3.app.ctrlser.com`), `revela-app` (Dockerfile, :3000, domínio **`revela.app.ctrlser.com`**),
  `revela-worker` (Dockerfile `worker/Dockerfile`). Script: `revela/scripts/provisionar-revela.mjs`
  (idempotente; segredos em `revela/.env.deploy.local`, fora do git).
- **Fonte do código = git por SSH com deploy key por serviço** (`git/generateKey` → `git/getPublicKey`
  → `gh repo deploy-key add` somente leitura → `services/app/updateSourceGit` com
  `git@github.com:flaviolimadev/revela.git`). Motivo: o token GitHub gravado no painel está
  **inválido (401)** e os outros serviços embutem PAT na URL do repo (visível no `inspectService`).
- Pegadinhas: `minio/minio` **sumiu do Docker Hub** ("repository does not exist") e `quay.io/minio/minio`
  dá 401 → RustFS no lugar (mesma API S3, env `RUSTFS_ACCESS_KEY/SECRET_KEY/VOLUMES/ADDRESS`).
  Dockerfile do worker com contexto na raiz do repo → `COPY worker/...`. `gh repo deploy-key list --json`
  imprime vazio (não `[]`) sem chaves. Primeiro deploy do app falhou por falta de `package-lock.json`
  (`npm ci`); create-next-app `--skip-install` não gera o lock.
- Resultado: `https://revela.app.ctrlser.com/api/health` 200 (db/storage configurados); `/` → 307
  `/prototipo.html`; S3 responde `AccessDenied` XML (vivo). Cert Let's Encrypt emitido sozinho.

## 5. Como o `.env` fica (modelo)

```
EASYPANEL_URL=https://<painel>.easypanel.host
EASYPANEL_API_TOKEN=
EASYPANEL_APPS_DOMAIN=<painel>.easypanel.host
EASYPANEL_HOST_IP=
REVELA_REPO=flaviolimadev/revela
REVELA_BRANCH=main
AUTH_SECRET=            # node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
ANTHROPIC_API_KEY=
PAYMENT_GATEWAY=        # vizzion | apexpay | mercadopago (vazio = simulado)
PAYMENT_API_URL=
PAYMENT_API_KEY=
PAYMENT_API_SECRET=
WEBHOOK_TOKEN=          # gerar como AUTH_SECRET
RESEND_API_KEY=
RESEND_FROM=Revela <no-reply@revela.app>
HIGGSFIELD_API_KEY=
```
