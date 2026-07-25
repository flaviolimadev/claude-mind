# MEMORY

Índice de toda a memória persistente. Uma linha por fato — sem conteúdo aqui, só o ponteiro.
É isto que o assistente carrega no começo de cada sessão pra saber o que já foi aprendido.

- [Como funciona](how-it-works.md) — a estrutura em uma página: catálogo → agentes → memória → verificador → grafo
- [Formato da memória](memory-format.md) — um arquivo = um fato, com frontmatter (name/description/type) e links `[[nome]]`
- [O verificador](the-check.md) — `scripts/check.mjs` cruza catálogo ↔ arquivos ↔ memória e aponta os desvios
- [Roteamento de tarefas](roteamento-de-tarefas.md) — toda ação passa pelo dispatcher e só roda com dono declarado
- [Especialização sob demanda](especializacao-sob-demanda.md) — recorte novo cria especialista novo, antes de executar
- [Os hooks](os-hooks.md) — o loop é automático: carrega, impõe o protocolo e barra o encerramento com desvio
- [O loop de auto-aprendizado](the-loop.md) — toda mudança passa por memória + agentes + verificação, por padrão
- [Exemplo: decisão (ADR)](example-decision.md) — modelo de registro de decisão de arquitetura
- [Exemplo: convenção](example-convention.md) — modelo de convenção de código do projeto
- [Exemplo: aprendizado](example-learning.md) — modelo de armadilha/gotcha aprendida em campo
