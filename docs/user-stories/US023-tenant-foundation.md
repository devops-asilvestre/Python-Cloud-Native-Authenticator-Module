# US023 — Tenant Foundation

- **Status:** Concluída — pronta para merge
- **Data da validação final:** 2026-11-03
- **Bounded Context:** Tenant

## Resultado

A US023 implementa e valida o primeiro Bounded Context de negócio da
plataforma, incluindo:

- Aggregate Root `Tenant`;
- Value Objects `TenantId`, `TenantName`, `TenantCode`, `TenantSlug`,
  `TenantStatus`, `TenantSettings`, `TenantDomain` e `TenantMetadata`;
- Commands, Queries, DTOs e handlers;
- persistência PostgreSQL através da foundation compartilhada;
- cache Redis através da foundation compartilhada;
- contratos de eventos versionados através da US018;
- publicação EventBridge através da US022;
- observabilidade estruturada;
- API REST completa do ciclo de vida do tenant;
- idempotência de `CreateTenant`;
- migrations, adapters, testes unitários e testes de integração.

## Critérios de aceite validados

| Critério | Resultado |
|---|---|
| Cobertura específica da US023 | **97% — aprovado** |
| Cobertura do repositório SQLAlchemy | **100% — aprovado** |
| Ruff | **Aprovado** |
| Mypy strict | **Aprovado** |
| Pytest | **Aprovado — 151 testes** |
| `git diff --check` | **Aprovado** |
| OpenAPI | **Aprovado pelos testes da API** |
| Migration Alembic | **SQL offline gerado com sucesso** |

A cobertura global de 90% não bloqueia esta história porque inclui módulos
fora do escopo da US023. O critério aplicável ao contexto Tenant foi atingido
com 97%.

## Validações adicionais realizadas

Foram corrigidos e verificados:

- conflitos de slug durante atualização;
- reutilização conflitante de `Idempotency-Key`;
- registro e validação dos contratos de eventos Tenant;
- imutabilidade dos metadados do agregado;
- execução assíncrona do Alembic com PostgreSQL/asyncpg;
- uso do Unit of Work para a transação da API;
- respostas HTTP para ID inválido, tenant inexistente, duplicidade e
  transições inválidas;
- cobertura dos caminhos do repositório SQLAlchemy.

## Pendências não bloqueantes

- A cobertura global do repositório permanece em 90% por incluir componentes
  fora da US023.
- A publicação transacional via outbox permanece como hardening operacional
  futuro.
- Testes contra instâncias reais de PostgreSQL, Redis e EventBridge devem ser
  executados no ambiente de integração/CI com os serviços disponíveis.

## Relatório

O relatório detalhado da execução está em
[`docs/reports/US023-execution-report.md`](../reports/US023-execution-report.md).
