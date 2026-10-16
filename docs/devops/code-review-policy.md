# Política de revisão de código

## Objetivo

Revisar cada mudança para melhorar correção, segurança, clareza, testabilidade
e aderência aos limites arquiteturais definidos em `4dev/` e `docs/`.

## Checklist do revisor

- A implementação atende aos critérios de aceitação e trata erros sem ocultá-los.
- Contratos, validação de entrada, autorização, isolamento multi-tenant e
  privacidade permanecem corretos.
- Os testes cobrem o comportamento novo e regressões relevantes; mocks não
  substituem validação de integração quando esta é necessária.
- Dependências, permissões, configuração, migrações e impacto operacional são
  justificados e mínimos.
- Código e documentação são claros, consistentes e sem segredos, dados
  sensíveis ou logs indevidos.
- A mudança respeita as camadas arquiteturais e registra decisões duradouras
  como ADR.

## Como revisar

Comentar problemas concretos e acionáveis, explicar impacto e sugerir direção
quando útil. Distinguir bloqueadores de sugestões. Aprovação significa que não
há bloqueador conhecido e que os gates aplicáveis passaram; não transfere ao
revisor a autoria nem a responsabilidade de teste.
