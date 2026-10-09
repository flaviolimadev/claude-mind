---
name: postgres-migrations-seguras
description: Migration em tabela viva sem downtime — NOT NULL em 3 passos, tipo novo = coluna nova + backfill, CREATE INDEX CONCURRENTLY, destrutivo só com backup e em duas versões
metadata:
  type: feedback
---

- **NOT NULL em tabela viva é operação em 3 passos:** coluna nullable → backfill em lotes →
  constraint. Direto, você trava a tabela e ainda falha na primeira linha antiga sem valor.
- **Mudar tipo de coluna reescreve a tabela inteira** (lock até acabar). Em tabela grande: coluna
  nova → backfill → troca de nome. O mesmo vale pra DEFAULT volátil em coluna nova em versões
  antigas do Postgres.
- **Índice em produção é `CREATE INDEX CONCURRENTLY`** — não bloqueia escrita. Detalhe que
  derruba pipeline: não roda dentro de transação (migration frameworks embrulham em transação por
  padrão; desligue para essa migration).
- **DROP/RENAME destrutivo: backup antes + deploy em duas versões.** Versão 1: código aceita
  esquema velho E novo. Versão 2: remove o velho. Pular a etapa intermediária = janela de erro
  500 entre migration e deploy.

**Why:** migration que trava tabela em produção é downtime auto-infligido — e os três sintomas
(lock, timeout, 500 em janela de deploy) parecem "instabilidade" quando são sequência errada.

**How to apply:** toda migration em tabela com dados passa por esta lista ANTES de ir pra main.
Ver [[postgres-indices-e-explain]], [[postgres-tipos-e-fusos]].
