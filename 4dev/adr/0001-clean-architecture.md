# ADR 0001: Limites arquiteturais do serviço

- **Status:** Aceita para o scaffold inicial
- **Data:** 2026-10-16

## Contexto

O módulo deverá combinar regras de identidade e autorização com frameworks web,
banco relacional, cache e serviços AWS sem acoplar as regras de negócio a esses
detalhes.

## Decisão

Adotar camadas de domínio, aplicação, infraestrutura e apresentação. Interfaces
de repositório e integração pertencem às camadas internas; adaptadores externos
implementam essas interfaces. Usar FastAPI/Pydantic na borda HTTP e SQLAlchemy
2/PostgreSQL nos adaptadores de persistência.

## Consequências

- Regras de negócio podem ser testadas sem banco, rede ou AWS.
- Adapters e configurações terão testes de integração próprios.
- A separação deve ser mantida sem criar abstrações antes de existir um caso de
  uso real.
- O scaffold não define ainda protocolos de autenticação, esquema de dados nem
  desenho de eventos; decisões específicas serão registradas em novos ADRs.
