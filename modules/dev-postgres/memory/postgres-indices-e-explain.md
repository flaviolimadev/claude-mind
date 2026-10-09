---
name: postgres-indices-e-explain
description: Otimização começa no EXPLAIN ANALYZE — FK não ganha índice sozinha no Postgres, ordem do índice composto importa, índice morto cobra em cada write
metadata:
  type: feedback
---

- **Antes de otimizar qualquer coisa: `EXPLAIN ANALYZE`.** Achismo erra o alvo; o plano mostra.
  Seq scan em tabela grande com WHERE seletivo = índice faltando — é 90% dos casos de "banco
  lento".
- **FK NÃO ganha índice automático no Postgres** (diferente do MySQL/InnoDB). Toda FK usada em
  JOIN ou com `ON DELETE CASCADE` precisa de índice explícito — sem ele, deletar o pai varre a
  tabela filha inteira.
- **Índice composto tem ordem:** colunas de igualdade primeiro, range/ordenação depois.
  `(status, created_at)` atende `WHERE status = ? ORDER BY created_at`; o inverso não.
- **Índice que ninguém usa cobra em CADA write.** Ache os mortos em `pg_stat_user_indexes`
  (idx_scan = 0 há meses) e remova.
- **N+1 se resolve na aplicação** (eager load) — índice nenhum salva de 500 queries de 1ms.

**Why:** otimização sem medir vira cargo cult; com EXPLAIN, o problema aparece em um comando.

**How to apply:** consulta lenta → EXPLAIN ANALYZE → só então decidir entre índice, reescrita ou
eager load. Ver [[postgres-migrations-seguras]].
