# Política de pull request

## Requisitos

- Todo PR deve ter objetivo e história/issue relacionada, escopo compreensível
  e descrição do risco ou impacto operacional.
- Manter PRs focados e pequenos; dividir mudanças independentes.
- Incluir evidências pertinentes (saída de testes, capturas sem dados sensíveis,
  exemplos ou resultados de benchmark quando aplicável).
- Atualizar documentação, configuração e ADRs diretamente relacionados.
- Não incluir segredos, dados pessoais reais, artefatos gerados ou mudanças
  alheias ao objetivo.
- Usar commits claros e resolver conversas antes do merge.

## Aprovação e merge

- Exigir pelo menos uma aprovação de revisor que não seja o autor; mudanças de
  segurança, autenticação, autorização, tenancy ou criptografia também devem
  receber revisão de alguém familiarizado com o domínio.
- Alterações cobertas por CODEOWNERS devem obter aprovação de um CODEOWNER.
- CI e gates de segurança obrigatórios devem passar; não contornar falhas sem
  correção ou exceção registrada e aprovada.
- Restringir merge a PR aprovado. Preferir squash merge para manter histórico
  de integração legível; usar merge commit para promoções de release quando
  necessário à rastreabilidade do fluxo.
- Configurar essas regras como branch protection/rulesets no GitHub.

## Exceções

Exceções urgentes devem registrar justificativa, responsável, risco, aprovação
e plano de remediação na issue/PR. A exceção não elimina a revisão posterior.
