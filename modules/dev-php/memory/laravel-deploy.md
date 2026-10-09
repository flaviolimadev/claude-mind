---
name: laravel-deploy
description: Sequência de release Laravel — composer sem dev, migrate --force, caches por último com TODAS as env; APP_KEY, storage:link e worker/schedule separados do web
metadata:
  type: reference
---

**Sequência de release (nessa ordem):**

```
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan config:cache && php artisan route:cache && php artisan view:cache
```

Caches por ÚLTIMO e só com **todas** as env já presentes — cachear config incompleta congela o
erro até o próximo deploy.

- **`APP_KEY` ausente = 500 na primeira tela.** Gere uma vez (`key:generate --show`) e guarde no
  provedor; trocar a chave invalida dados criptografados.
- **`storage:link`** pra upload público aparecer; em container, `storage/` precisa ser volume
  persistente (filesystem é efêmero).
- **Permissões:** `storage/` e `bootstrap/cache/` graváveis pelo usuário do PHP.
- **Web no ar ≠ fila rodando:** worker de fila e `schedule:run` (cron) são PROCESSOS próprios —
  e-mail "que não sai" em produção quase sempre é worker que ninguém subiu.
- Em painel tipo EasyPanel, essa sequência entra no comando de deploy do serviço (o painel em si
  é assunto do módulo `deploy-easypanel`).

**Why:** release Laravel tem ordem certa; fora dela o site sobe "funcionando" com config velha,
migration faltando ou fila morta.

Ver [[laravel-armadilhas]], [[laravel-convencoes]].
