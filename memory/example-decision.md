---
name: example-decision
description: "EXEMPLO — modelo de registro de decisão de arquitetura (ADR); troque pelo seu"
metadata:
  type: project
---

> Este é um exemplo para você copiar. Apague e escreva as decisões reais do seu projeto.

**Decisão:** usar SQLite no começo e migrar para Postgres só quando houver escrita concorrente real.

**Contexto:** o projeto começa com um único processo e pouca escrita. Postgres agora seria complexidade
sem retorno.

**Consequências:** o código de acesso a dados fica atrás de uma interface fina, pra troca ser barata
depois. Ver [[example-convention]].

**Why:** decisões de arquitetura somem da memória da equipe se não forem escritas — e aí alguém
"redescobre" o problema seis meses depois.
