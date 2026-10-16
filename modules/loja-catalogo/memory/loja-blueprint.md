---
name: loja-blueprint
description: A arquitetura de uma loja-catálogo — vitrine estática (Vite+React) + admin (Node/Express+Postgres) + WhatsApp como checkout; o que é público, o que é do dono e o modelo de dados que serve a qualquer segmento
metadata:
  type: reference
---

**Três peças, dois serviços e um banco** (validado na Chronos Lab, 2026-10-15/16):

1. **Vitrine** (`src/`, Vite+React, servida por nginx como site estático): mobile-first, lê
   `GET /api/catalog` e cai no JSON embutido (`src/data/`) se a API estiver fora. Todo botão de
   compra vira **mensagem pronta no WhatsApp** (`wa.me/<numero>?text=…`) com produto, preço e link
   canônico `/r/ID`. Não tem carrinho com pagamento: a sacola só monta a mensagem.
2. **Admin** (`admin/server` Express + `admin/web` React, um serviço só que serve o painel e a
   API): login por cookie JWT, rotas `/api/*` protegidas; públicas só `/api/catalog`, `/uploads/*`,
   `/r/:id` e `/og-image/:id.jpg`. Fotos em volume (`UPLOAD_DIR`).
3. **Postgres**: `users`, `settings` (JSONB: nome, WhatsApp, cidades, parcelas, sem juros,
   banners, vídeo), `watches` (produto — renomeie por segmento), `purchases` (entradas),
   `sales` (vendas com custo congelado, cliente, pagamento, canal), `customers`, `installments`.

**O que muda por segmento:** só os atributos do produto e os filtros. Relógio tem gênero,
mecanismo, pulseira, mostrador, diâmetro; perfume teria família olfativa, ml, concentração.
A tabela de produto carrega os genéricos (marca, modelo, ref, preço à vista, preço no cartão,
custo, qualidade/linha, destaque, novo, visível, fotos, vídeo, descrição) + os do segmento.
Os filtros da vitrine nascem dos valores existentes — valor novo vira opção nova sem código.

**Regras que valem em toda loja:**
- `price` é **à vista**; `cardPrice` é o parcelado total. A diferença vira "economize R$ X".
- A vitrine recebe `soldOut` e `lastUnit`, nunca a quantidade de estoque.
- `active=false` esconde da vitrine mas mantém histórico e relatórios (é assim que o passado fica).
- Nome da loja, número, cidades e parcelas vêm do admin (`settings`), nunca fixos no código.

Ver [[loja-nova-loja-checklist]] (ordem de criação), [[loja-admin-estoque-e-financeiro]]
(as contas), [[loja-deploy-easypanel]] (no ar).
