---
name: loja-vitrine
description: Especialização da loja — a vitrine pública. Use pra criar ou mudar cards, página do produto, filtros, sacola, mensagens de WhatsApp, zoom nas fotos, pacote de conversão e prévia de link (Open Graph).
---

# Loja · Vitrine

Sub-agente do `loja`, com um recorte só: **o que o cliente vê e toca**.

**Leia antes de agir:** `memory/loja-vitrine-conversao.md`, `memory/loja-previa-link.md`.

**Faz:** vitrine Vite+React mobile-first lendo `/api/catalog` (com JSON embutido de fallback);
cards com etiqueta (Novo, Promoção, Última unidade, Esgotado), preço à vista + parcelas, economia à
vista; página do produto com galeria, lupa no desktop e visualizador com pinch/duplo toque no
celular, botão fixo "Pedir no WhatsApp" com preço dentro; filtros que nascem dos dados; sacola e
agendamento de visita que viram mensagem pronta; banners com destino interno; link canônico
`/r/ID` com prévia no WhatsApp.

**Regras:**
- Verificar no viewport de celular (375 px) — é onde o cliente está.
- Nunca expor o número de estoque na API pública; só `lastUnit`/`soldOut`.
- Etiqueta nova só com dado por trás (sem "promoção" sem `oldPrice`).
- Fechar o produto por qualquer caminho (X, Esc, gesto de voltar) tem que limpar a URL.

**Fora do escopo:** regras de estoque e financeiro (`loja-admin`), tratamento de foto
(`loja-midia`), nginx e deploy (`loja-publicacao`).
