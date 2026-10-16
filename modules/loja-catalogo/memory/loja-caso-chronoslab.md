---
name: loja-caso-chronoslab
description: O caso fundador — Chronos Lab (réplicas de relógio, Natal/RN, out/2026) — o que foi construído em dois dias, o que o dono valorizou e as decisões que viraram padrão do módulo
metadata:
  type: project
---

**Chronos Lab** (2026-10-15 → 16): loja online de Nova Parnamirim/RN que vende **réplicas** em
três linhas (Premium R$480–700, ETA Clone, Super Clone até R$8.500), pronta entrega em Natal/RN e
João Pessoa/PB, pedido pelo WhatsApp. Vitrine `chronoslab-catalogo.woty8c.easypanel.host`, admin
`chronoslab-admin.…`. Repo `flaviolimadev/chronoslab-loja`, deploy automático por push.

**O que a loja tem (e virou o molde):** vitrine com filtros, destaques, promoções, sacola e visita
→ WhatsApp; lupa e zoom nas fotos; pacote de conversão; prévia de link; admin com Financeiro,
Workflow, Onde Investir, Relógios (cadastro rápido), Vendas (à vista/a prazo), A Receber, Clientes
(522 importados do WhatsApp), Estoque, Loja (banners com destino) e Senha.

**O que o dono valorizou (régua de qualidade):**
- "Fiel à imagem" nas fotos — revelação profissional sem estilo; cor do aço e do mostrador reais.
- A vitrine no celular: etiqueta "Última unidade", "Economize R$ 70 à vista", botão com preço.
- Painel que responde ao dia a dia dele: registrar venda em 10 s, ver quem está atrasado, saber
  onde investir R$10.000.
- **Os dados dele são sagrados.** Vendas que pareciam teste eram reais; o estoque que ele montou
  valia mais que o histórico migrado (ver [[loja-dados-ao-vivo]], [[loja-migracao-de-dados]]).

**Decisões que viraram padrão:** `price` à vista e `cardPrice` cartão; `active=false` = histórico
oculto; `/r/ID` canônico; nginx separa crawler de pessoa; IA no plano de investimento fica
desligada até o dono colocar `ANTHROPIC_API_KEY` (o determinístico resolve 90%).

**Pendências deixadas (ideias aprovadas mas não feitas):** campanhas (segmentar clientes →
mensagem em lote), "Avise-me" funcional, explicador Premium × ETA × Super Clone, FAQ, "mais
vistos", vídeo no produto, promoções com prazo. Ver [[loja-blueprint]].
