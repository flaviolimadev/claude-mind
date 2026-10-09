---
name: postgres-tipos-e-fusos
description: Tipos certos — timestamptz sempre (UTC no banco, fuso na borda), dinheiro em numeric nunca float, bigint identity pra id, text em vez de varchar(n) arbitrário
metadata:
  type: feedback
---

- **`timestamptz`, SEMPRE.** `timestamp` sem fuso não guarda o fuso — ele "assume" um e corrompe
  silenciosamente quando app e banco discordam. Padrão: gravar em UTC, converter pro fuso do
  usuário só na borda de exibição. Relatório de "hoje/ontem" calculado no fuso errado desloca um
  dia inteiro — bug clássico e já vivido em relatório financeiro.
- **Dinheiro é `numeric(12,2)`** (ou escala da moeda). NUNCA `float`/`real`/`double`
  (0.1 + 0.2 ≠ 0.3) e nem o tipo `money` (acopla locale do servidor).
- **id: `bigint GENERATED ALWAYS AS IDENTITY`.** `int` de 32 bits estoura (2,1 bi parece muito
  até a tabela de eventos chegar lá); `serial` é o jeito legado — identity é o padrão atual.
  UUID (`gen_random_uuid()`) quando a geração é distribuída ou o id vaza pra URL.
- **`text` em vez de `varchar(n)` arbitrário.** No Postgres não há ganho de performance em
  varchar(255); limite de tamanho só quando é regra de negócio real (e aí é CHECK documentado).

**Why:** tipo errado é bug latente — não aparece em teste, aparece com dado real: o centavo que
some, o fuso que desloca, o id que estoura num domingo.

**How to apply:** revisão de schema novo confere coluna a coluna contra esta lista.
Ver [[postgres-migrations-seguras]], [[postgres-indices-e-explain]].
