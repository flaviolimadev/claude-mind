---
name: memory-format
description: Como escrever uma memória — um arquivo por fato, com frontmatter e links entre fatos
metadata:
  type: reference
---

Cada memória é **um arquivo = um fato**, em `memory/`, com este frontmatter:

```markdown
---
name: <slug-curto-em-kebab-case>
description: <resumo em uma linha — é o que decide se este fato é relevante na hora de recuperar>
metadata:
  type: user | feedback | project | reference
---

<o fato. Para feedback/project, siga com **Why:** e **How to apply:**. Ligue fatos com [[nome]].>
```

Tipos:
- **user** — quem é o usuário (papel, preferências).
- **feedback** — como o assistente deve trabalhar (correções e abordagens confirmadas); inclua o porquê.
- **project** — trabalho em andamento, metas, restrições não dedutíveis do código.
- **reference** — ponteiros para recursos (URLs, docs, dashboards).

Regras:
- Antes de criar, procure um arquivo que já cubra o fato — atualize em vez de duplicar.
- Ligue fatos relacionados com `[[nome]]` (o `nome` do frontmatter do outro arquivo).
- Depois de criar/editar, adicione/ajuste a linha em `MEMORY.md` (uma linha por fato).
- Não guarde o que o repositório já registra (estrutura do código, histórico do git).
