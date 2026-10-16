---
name: loja-migracao-de-dados
description: Como importar catálogo, histórico de sistema antigo e contatos do WhatsApp sem estragar a loja — validar a fonte, histórico vira venda oculta, o estoque do dono manda, lote reversível, marcas padronizadas por mapa explícito
metadata:
  type: feedback
---

**O que aconteceu na Chronos Lab (2026-10-16) e virou regra:**

1. **Validar a fonte antes de importar.** A planilha `controle-estoque.xlsx` estava corrompida
   (278 movimentações todas marcadas "Venda", muitas eram compras) e a migração inflou receita e
   investido ~2×. A verdade estava no sistema antigo online (Lovable) na seção "Relatório por
   Produto": 113 produtos com comprado/vendido/estoque/investido/receita. Confira totais e tipos
   antes; se dois números da fonte não fecham entre si, registre a diferença (R$580 lá).
2. **Histórico antigo entra como venda oculta, não como estoque.** A primeira migração lançou o
   histórico nos produtos do catálogo e mudou o estoque que o dono tinha montado. Ele pediu pra
   reverter: *a peça vendida no sistema antigo pode ser outra, diferente da que está na loja*.
   Resultado certo: catálogo de volta a 1 unidade cada (custo mantido), e 95 produtos
   `active=false` só com as vendas antigas (125 vendas, receita e lucro batendo com o antigo).
3. **Importar catálogo pela API, não por SQL:** `POST /api/watches` (+ `initialQty`) e
   `POST /:id/images`; `price` = à vista, `costPrice` = pago, cartão em `cardPrice`. Linhas de
   qualidade por faixa de preço só com o dono confirmando ("480 a 700 é Premium, acima ETA").
4. **Contatos do WhatsApp:** `POST /api/customers/import` deduplica por telefone; situação
   (comprou/interessado/não respondeu) é heurística pela última mensagem — o dono revisa; áudio
   não se transcreve. 522 clientes em uma passada; vendas achadas no chat NÃO vão pro financeiro
   sem o dono pedir.
5. **Padronizar cadastro feito à mão** (Tag→TAG Heuer, Tudro→Tudor, BvlgaRI→Bvlgari,
   Patek→Patek Philippe, Audemars→Audemars Piguet, MontBlanc→Montblanc): mapa explícito
   `id → (marca, modelo)` revisado antes, `GET`+`PUT` por produto, log antes/depois, e conferir a
   faixa de marcas da vitrine no fim. Modelo que ficou igual à marca é sinal de cadastro incompleto:
   avisar, não inventar.

**Why:** migração é a hora em que mais se perde dado do dono, e o erro aparece dias depois como
"o lucro está errado".

**How to apply:** toda importação tem (a) validação da fonte, (b) script em arquivo com log
reversível, (c) conferência de totais no painel e na vitrine, (d) relatório ao dono do que mudou.
Ver [[loja-dados-ao-vivo]], [[loja-admin-estoque-e-financeiro]].
