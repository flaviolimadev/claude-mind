---
name: loja-dados-ao-vivo
description: O dono usa o painel ao vivo enquanto o assistente trabalha — nunca apagar, sobrescrever ou "corrigir" venda, produto, cliente ou estoque assumindo que é teste; mostrar, perguntar, e só então agir com log pra desfazer
metadata:
  type: feedback
---

Na Chronos Lab (2026-10-16) apaguei **7 vendas reais** (R$16.049,69) achando que eram sobra de
teste — sem cliente, Pix, data de hoje. Eram vendas que o dono tinha acabado de registrar pelo
painel. Tive que recriar uma a uma (e ainda faltou uma do histórico).

**Why:** o dono mexe no admin em paralelo; qualquer dado "estranho" pode ser dele e ter acabado
de nascer. Um registro apagado leva junto parcelas, custo congelado e o histórico do cliente.

**How to apply:**
- Operação destrutiva (delete, update em massa, "padronizar", "limpar") em dado ao vivo só com
  **confirmação explícita** depois de mostrar a lista exata do que vai mudar.
- Antes de qualquer lote, salvar o estado anterior em JSON (`wa/*_log.json`) pra poder desfazer.
- Alterar produto é `GET` + `PUT` do objeto inteiro (o `PUT` substitui), mudando só o campo
  pedido — e conferir no retorno que preço, estoque e vendidos continuam iguais.
- Esconder é melhor que apagar: `active=false` mantém histórico e relatórios.
- O que o dono montou (estoque atual, preços, nomes) é a verdade sobre qualquer fonte importada.

Ver [[loja-migracao-de-dados]], [[loja-admin-estoque-e-financeiro]].
