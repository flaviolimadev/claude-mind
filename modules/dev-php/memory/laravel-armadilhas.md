---
name: laravel-armadilhas
description: Armadilhas Laravel — N+1 (e o caso MorphTo), env() nulo com config cacheada, timezone deslocando relatório em 1 dia, Model serializado na fila
metadata:
  type: feedback
---

- **N+1:** loop com `$pedido->cliente` dispara uma query POR VOLTA. Eager load com
  `with('cliente')`. Caso real vivido: eager load genérico de **MorphTo** não resolveu e precisou
  virar consulta dirigida por ciclo — relação polimórfica merece desconfiança redobrada. Em dev,
  ligue `Model::preventLazyLoading()` e o N+1 explode na sua cara, não na do usuário.
- **`env()` fora de `config/` retorna `null` com config cacheada.** Em produção
  (`config:cache` ligado), `env('X')` no meio do código simplesmente para de funcionar. Regra:
  `env()` SÓ dentro de `config/*.php`; o código lê `config('...')`.
- **"Mudei o `.env` e nada aconteceu":** a config vem do cache — `php artisan config:cache` de
  novo (ou `config:clear`). Vale depois de TODA mudança de env em produção.
- **Timezone:** banco em UTC, conversão na borda de exibição. `today()`/`yesterday()` no fuso
  errado desloca relatório em 1 dia — bug vivido: cálculo de "hoje" com dado UTC deu um dia de
  diferença em relatório financeiro.
- **Fila serializa o Model por id:** entre o `dispatch` e o `handle`, o dado pode ter mudado (ou
  sumido — `ModelNotFoundException` no worker). Passe ids/valores primitivos quando o job não
  precisar do estado fresco.

**Why:** são os buracos que mais queimam horas em produção Laravel, e todos dão sintoma genérico.

**How to apply:** bug estranho em produção → esta lista primeiro, na ordem. Ver
[[laravel-convencoes]], [[laravel-deploy]].
