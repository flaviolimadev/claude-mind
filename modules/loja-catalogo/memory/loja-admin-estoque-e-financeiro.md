---
name: loja-admin-estoque-e-financeiro
description: As contas do painel — estoque = Σentradas − Σvendas, custo congelado na venda, lucro/investido/valor em estoque/previsão, venda a prazo com parcelas e A Receber, relatórios, e as armadilhas da API (PUT substitui o registro, cadastro rápido)
metadata:
  type: reference
---

**Modelo (Chronos Lab, 2026-10-15/16):**
- **Estoque** de um produto = Σ `purchases.qty` − Σ `sales.qty`. Não existe coluna de estoque:
  é derivado, então nunca "desatualiza". Produto novo com `initialQty` gera a primeira entrada.
- **Custo**: `watches.cost_price` é o custo unitário atual (uma entrada nova atualiza); cada venda
  **congela** o custo do momento em `sales.unit_cost`. Lucro = preço de venda − custo congelado.
- **Financeiro por período:** receita (vendas), custo (COGS congelado), lucro, investido
  (entradas pela data da compra), **capital em estoque** = Σ estoque × custo, **previsão de
  receita** = Σ estoque × preço. Consistência: investido = COGS + valor em estoque (o sistema
  antigo do dono não fechava em R$580 — o novo fecha).
- **Venda à vista ou a prazo:** `installments` (sale_id, n, kind `entrada`|`parcela`, amount,
  due_date, paid, paid_at). Entrada é n=0 já paga; N parcelas mensais a partir da primeira data.
  Vendas listam `installment:{count,paid,due,next,overdue}`.
- **A Receber:** `/api/receivables` com status `pending|overdue|paid|all`, por cliente e período;
  `/summary` (a receber, atrasado, este mês, devedores, por cliente); `/:id/pay` e `/unpay`.
  No `GROUP BY` use colunas explícitas — alias ambíguo com `c.name` deu 500.
- **Relatórios:** `/reports/summary`, `/products` (comprado, vendido, estoque, investido, receita,
  lucro, margem, dias médios pra vender), `/breakdown` (vendas e entradas por semana/mês),
  `/advisor` (alocação determinística: score = max(0, roi×30/dias)×√unidades, guloso com teto
  de 40% por marca; `/advisor/insight` usa a API da Anthropic só se `ANTHROPIC_API_KEY` existir).

**Armadilhas da API:**
- `PUT /api/watches/:id` passa o corpo inteiro por `parseWatch`: campo ausente vira vazio/zero.
  **Sempre `GET` o produto e mande o objeto inteiro de volta** mudando só o que quer. Fotos não
  passam pelo PUT (`/:id/images`).
- Cadastro rápido ("Marca Modelo" + preço + custo + qtd): a marca é reaproveitada se o texto
  começa com uma existente (qualquer caixa, duas palavras — "tag heuer carrera" → TAG Heuer);
  sem isso o dono cria "Tag", "Tudro", "BvlgaRI" e a faixa de marcas da vitrine se parte.
- Esgotado continua visível (com "Avise-me"); produto criado só pra registrar venda (preço 0,
  sem foto) deve ficar `active=false` — senão aparece na vitrine como "R$ 0 esgotado".

Ver [[loja-dados-ao-vivo]], [[loja-blueprint]].
