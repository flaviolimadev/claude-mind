---
name: laravel-convencoes
description: Convenções que o Laravel premia — validação em FormRequest, controller enxuto, migration reversível e nunca editada, nomes padrão de tabela/model/FK
metadata:
  type: feedback
---

- **Validação em `FormRequest`**, não no controller. Controller enxuto: resolve a request → chama
  service/action → responde. Regra de negócio em classe própria, testável sem HTTP.
- **Migration é imutável depois de ir pra `main`:** errou, cria OUTRA migration corrigindo. E todo
  `up()` tem `down()` de verdade — "reversível" de mentira aparece na primeira emergência.
- **Eloquent explícito:** `$fillable` e `casts` declarados. `$guarded = []` é mass assignment
  esperando um campo `is_admin` no formulário.
- **Nomes padrão cobram juros se violados:** tabela plural snake_case, Model singular, FK
  `<singular>_id`. Cada desvio exige configuração manual em TODO relacionamento pra sempre.

**Why:** Laravel é opinativo — seguir a convenção compra produtividade; desviar compra
documentação implícita que ninguém leu.

**How to apply:** revisão de código Laravel confere esta lista antes de olhar lógica.
Ver [[laravel-armadilhas]], [[laravel-deploy]].
