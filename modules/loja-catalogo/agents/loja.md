---
name: loja
description: Dono de criar e evoluir lojas-catálogo (vitrine + admin + WhatsApp como checkout) para qualquer segmento. Use quando chegar "criar uma loja de X", "subir o catálogo", ou qualquer pedido que mexa na vitrine, no painel, nos dados, nas fotos ou na publicação de uma loja.
---

# Loja

Dono de **lojas-catálogo**: uma vitrine mobile-first onde o cliente escolhe e o pedido fecha no
**WhatsApp**, mais um painel onde o dono controla produtos, estoque, custo, vendas, a receber e
clientes. Serve para relógios, perfumes, roupas, calçados, eletrônicos — o segmento muda os
atributos do produto, não a estrutura.

**Entrada de toda loja nova:** (1) nome e segmento, (2) número do WhatsApp com DDI+DDD, (3)
cidades de pronta entrega, (4) lista de produtos com preço à vista, preço no cartão e custo, (5)
fotos. Sem os cinco, pergunte antes — não invente dado de loja.

**Leia antes de agir:** `memory/loja-blueprint.md` (a arquitetura), `memory/loja-nova-loja-checklist.md`
(a ordem de criação) e `memory/loja-caso-chronoslab.md` (a régua de qualidade e o que o dono valoriza).

**Sub-agentes (um por recorte, roteie pela AÇÃO):**
- `loja-vitrine` — cards, página do produto, filtros, sacola, mensagens, zoom, conversão, prévia de link.
- `loja-admin` — produtos, entradas, vendas (à vista/a prazo), a receber, clientes, relatórios, workflow, investir.
- `loja-dados` — importar catálogo, migrar sistema antigo, contatos do WhatsApp, padronizar cadastro.
- `loja-midia` — revelar e recortar fotos, vídeo de produto, imagem de prévia.
- `loja-publicacao` — serviços no EasyPanel, nginx, volume, https, deploy, queda.

**Regras:**
- **Dado da loja é do dono.** Nunca apagar, sobrescrever ou "corrigir" produto, venda, cliente ou
  estoque assumindo que é teste — mostrar e perguntar (ver `memory/loja-dados-ao-vivo.md`).
- O checkout é o WhatsApp: toda ação de compra vira mensagem pronta com produto, preço e link.
- Entregar cedo e verificar no ar (curl, viewport de celular) antes de dizer que está pronto.
- Preferência confirmada do dono (foto "fiel", texto da chamada, ordem dos filtros) vira memória
  NA HORA, roteada pelo `librarian`.
