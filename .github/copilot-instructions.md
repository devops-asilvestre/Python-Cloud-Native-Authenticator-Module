# Instruções de arquitetura do workspace

Estas regras aplicam-se a mudanças futuras neste repositório:

- Use Python 3.13+ e FastAPI nos serviços Python.
- Mantenha DDD, Clean Architecture, SOLID, multi-tenancy e isolamento de tenant
  validado no servidor.
- Preserve os limites de bounded context. Um contexto não importa código
  interno de outro; integrações usam contratos explícitos e eventos versionados.
- Mantenha domínio, aplicação, adaptadores e infraestrutura em suas respectivas
  camadas. Não acople domínio a FastAPI, AWS ou tecnologia de persistência.
- Projete integrações assíncronas para EventBridge/SQS sem tratar o transporte
  como parte do domínio.
- Projete para AWS e Docker, com observabilidade OpenTelemetry e privacidade
  LGPD desde o início.
- Aplique Zero Trust, menor privilégio e minimização de dados. Nunca adicione
  credenciais, segredos, tokens ou configuração sensível ao repositório.
- Não compartilhe estado mutável de domínio entre serviços; qualquer kernel
  compartilhado deve permanecer pequeno, estável e independente dos contextos.
- Documente decisões arquiteturais em `docs/adr/` e atualize a documentação
  relacionada à mudança.
- Preserve a estrutura existente e não introduza regras de negócio ou endpoints
  em mudanças exclusivamente estruturais.
