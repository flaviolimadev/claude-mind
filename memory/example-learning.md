---
name: example-learning
description: "EXEMPLO — modelo de armadilha/gotcha aprendida em campo; troque pela sua"
metadata:
  type: project
---

> Este é um exemplo para você copiar. Apague e escreva os aprendizados reais do seu projeto.

**Armadilha:** o fuso horário do banco vinha em UTC, mas todo cálculo de "hoje/ontem" precisa do fuso
local — misturar os dois deu relatórios com um dia de diferença.

**Como evitar:** normalize para o fuso do usuário na borda de leitura, uma vez só, e trate tudo depois
como local.

**Why:** esse tipo de bug não aparece no teste feliz e custa horas de depuração — registrar economiza a
próxima pessoa (que pode ser você daqui a três meses). Ver [[example-decision]].
