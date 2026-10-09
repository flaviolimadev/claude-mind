---
name: node-env-e-scripts
description: process.env é sempre string ("false" é truthy), dotenv só em dev, engines travado e scripts npm como a interface do projeto
metadata:
  type: feedback
---

- **`process.env` é SEMPRE string.** `"false"` é truthy, `"0"` é truthy. Compare explícito
  (`=== 'true'`) ou normalize numa borda única de config — nunca `if (process.env.FLAG)`.
- **dotenv é ferramenta de DEV.** Produção recebe env do provedor (painel/secret manager). `.env`
  nunca é comitado; `.env.example` sempre é (documenta o contrato sem os valores).
- Node ≥ 20.6 tem **`node --env-file=.env`** nativo — em projeto novo, dispensa a dependência
  dotenv por completo.
- **`engines` no `package.json`** + mesmo major em dev/CI/produção. Metade do "funciona na minha
  máquina" é versão de Node diferente.
- **Scripts npm são a interface do projeto:** `dev`, `test`, `check` — quem chega roda
  `npm run` e descobre o que o projeto sabe fazer. Comando que só existe na sua cabeça não existe.

**Why:** env string/ausente e Node de versão diferente são a causa típica do bug "só em produção"
— barato de prevenir, caro de depurar.

**How to apply:** toda leitura de env passa por comparação explícita; todo projeto declara
`engines`; todo comando repetido vira script npm. Ver [[node-esm-cjs]].
