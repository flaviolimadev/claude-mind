---
name: easypanel-armadilhas
description: Armadilhas do EasyPanel — bind em 0.0.0.0 na porta do serviço, filesystem efêmero (volume pra uploads), env no painel, DNS antes do SSL
metadata:
  type: feedback
---

- **O app tem que escutar em `0.0.0.0`**, na MESMA porta configurada no serviço. Bind em
  `127.0.0.1`/`localhost` deixa o proxy sem alcance: o serviço aparece "no ar" e responde **502**.
- **O filesystem do container é efêmero:** upload, `storage/`, cache em disco — tudo que não
  estiver num **volume montado** SOME no próximo deploy. Monte o volume antes do primeiro usuário
  real, não depois do primeiro arquivo perdido.
- **Env vive no painel, não no repo:** o `.env` do repositório não é lido (e não deve ser
  comitado). Mudou env no painel → **redeploy** pra valer.
- **Laravel:** sem `APP_KEY` é 500 na primeira tela; `php artisan migrate --force` entra no
  comando de deploy; `config:cache` só quando TODAS as env estiverem no painel — cachear config
  incompleta congela o erro.
- **DNS antes do SSL:** aponte o A record (apex **e** `www`) pro IP da VPS e só então adicione o
  domínio no painel — o Let's Encrypt falha se o DNS ainda não propagou, e a falha fica em cache
  por um tempo.

**Why:** todos esses erros dão sintoma genérico (502, 500, "arquivo sumiu") e queimam horas de
depuração; são exatamente a diferença entre "funciona local" e produção.

**How to apply:** diagnóstico pós-deploy começa POR esta lista, na ordem, antes de abrir log de
aplicação. Ver [[easypanel-fluxo-de-deploy]].
