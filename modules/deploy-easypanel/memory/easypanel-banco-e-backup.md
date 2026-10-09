---
name: easypanel-banco-e-backup
description: Banco no EasyPanel — conexão interna pelo nome do serviço, porta externa fechada, backup antes de migration destrutiva
metadata:
  type: reference
---

- Crie o Postgres/MySQL como serviço do **mesmo projeto** no painel. O app conecta pela **rede
  interna, usando o nome do serviço como host** — não `localhost`, não IP público.
- **Porta externa só pra inspecionar** com um cliente local — e **feche depois**. Banco exposto na
  internet é convite; a conexão de produção nunca precisa dela.
- **Backup antes de toda migration destrutiva** (drop, rename, alteração de tipo): dump pelo
  painel ou `pg_dump` por uma porta externa temporária. Guarde o dump **fora da VPS** — backup no
  mesmo servidor morre junto.
- Credenciais ficam no painel e chegam ao app por env (`DATABASE_URL`/variáveis) — nunca no
  repositório.

Ver [[easypanel-fluxo-de-deploy]], [[easypanel-armadilhas]].
