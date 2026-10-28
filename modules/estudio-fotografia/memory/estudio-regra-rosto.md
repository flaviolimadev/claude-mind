---
name: estudio-regra-rosto
description: Trava de segurança do estúdio — quando o cliente exige "rosto intocado", NENHUMA IA generativa toca em foto com pessoa; só correção, grade, blur fora do sujeito, recorte por segmentação local, colagem e tipografia
metadata:
  type: feedback
---

**Regra (dita pelo cliente em 27/out/2026, 2× na mesma mensagem, projeto Mocidade Betfage):**
"as edições não podem nunca, em hipótese alguma, alterar o rosto… manter a foto original
apenas adicionando os efeitos." Antes disso, no caso Ismael (12/out), o mesmo cliente reprovou
artes do Higgsfield que acinzentaram o cabelo e mudaram traços: "não pode mudar o rosto, deve
ser fiel ao rosto original, não modifique pra não ficar como se fosse outra pessoa."

**O que é PERMITIDO (não altera feições):** correção de WB/exposição; grades globais (teal &
orange, P&B, sépia); grão, halation, vinheta; blur/zoom-blur/spin-blur **em máscara fora do
sujeito**; recorte da pessoa por **segmentação local** (rembg/u2net — pixels copiados, nunca
redesenhados); molduras, cards, faixas, colagens; tipografia e elementos gráficos; upscale
clássico (Lanczos). Clarear/escurecer uma ÁREA (ex.: dentro de um frame) é ok — é brilho, não
feição.

**O que é PROIBIDO:** qualquer `generate_image`/img2img/"fidelidade"/enhancement generativo em
foto com pessoa; "transplante" de rosto; inpainting em pele/cabelo; upscale generativo que
reinterprete rosto. Fundo/céu gerado só se o sujeito for colado por cima intacto (técnica do
caso Ismael: foto real + só a nuvem transplantada).

**Why:** a IA generativa deriva identidade (envelhece, acinzenta cabelo, muda proporção) mesmo
com prompt rígido; para o cliente isso é inaceitável e invalida a entrega inteira.

**How to apply:** no briefing, se o cliente disser "rosto intocado"/"fiel"/"sem mudar as
pessoas", o `estudio-retocador` fica FORA do pipeline de pessoas (pode gerar só fundos/texturas
sem gente). QA final obrigatório: post × foto original lado a lado em zoom nos rostos. Ver
[[estudio-workflow]], [[estudio-higgsfield]], [[estudio-caso-ismael]].
