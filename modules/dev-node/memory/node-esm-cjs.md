---
name: node-esm-cjs
description: ESM vs CJS — "type":"module" muda as regras (require some, __dirname some, import de JSON muda); os erros clássicos e a saída de cada um
metadata:
  type: feedback
---

`"type": "module"` no `package.json` muda as regras do runtime inteiro:

- **`require` deixa de existir** (`ReferenceError: require is not defined`). Use `import`. No
  sentido inverso, CJS não consegue `require()` de um pacote ESM (`ERR_REQUIRE_ESM`) — só
  `import()` dinâmico.
- **`__dirname`/`__filename` não existem em ESM.** Derive:
  `path.dirname(fileURLToPath(import.meta.url))`. É o idioma padrão — não invente caminho
  relativo ao `cwd`, que muda conforme de onde o processo foi chamado.
- **Import de JSON** em ESM exige atributo (`with { type: 'json' }`, sintaxe que já mudou uma vez)
  — o portátil é `JSON.parse(fs.readFileSync(...))`.
- **Pegadinha dupla do `node -e`:** one-liners rodam como CJS por padrão — `require` funciona ali
  MESMO num projeto `type: module` (e `import` estático não). Não conclua nada sobre o projeto
  testando em `node -e`.
- Extensões decidem quando não há `type`: `.mjs` força ESM, `.cjs` força CJS.

**Why:** erro de sistema de módulo é o tropeço nº 1 em Node moderno e o sintoma engana — parece
que a função "sumiu", mas é o modo de carregamento errado.

**How to apply:** erro com `require`/`import`/`__dirname` → esta memória ANTES de mexer no código.
Ver [[node-env-e-scripts]], [[node-zero-deps]].
