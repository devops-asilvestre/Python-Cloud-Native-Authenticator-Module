# Visão arquitetural

## Objetivo

Construir uma plataforma corporativa de identidade e acesso em Python, orientada
à segurança, multi-tenancy, auditoria e operação cloud-native na AWS.

## Componentes-alvo

- **Presentation**: API HTTP com FastAPI; contratos versionados e validados por
  Pydantic.
- **Application**: casos de uso, comandos, consultas e DTOs; coordena as portas
  do domínio.
- **Domain**: entidades, objetos de valor, eventos, políticas e interfaces de
  repositório sem dependência de frameworks.
- **Infrastructure**: adaptadores SQLAlchemy/PostgreSQL, Redis, AWS
  (EventBridge/SQS), criptografia e telemetria OpenTelemetry.
- **Shared**: primitivas estritamente transversais; evitar dependências do
  domínio para componentes compartilhados mutáveis.

## Estrutura

```text
src/
  identity_service/
    domain/
    application/
    infrastructure/
    presentation/
    shared/
  shared/
tests/{unit,integration,e2e}/
infrastructure/{docker,terraform,scripts}/
4dev/{architecture,user_stories,adr,security,diagrams}/
```

## Fluxo de dependências

As dependências apontam para dentro: apresentação e infraestrutura implementam
portas definidas pelas camadas internas. Casos de uso não importam FastAPI,
SQLAlchemy, boto3 ou clientes Redis. Integrações externas são substituíveis e
testáveis por meio de contratos.

## Limite do scaffold

O código inicial fornece a aplicação HTTP e a rota `/health/live`. Ainda não há
armazenamento, autenticação, autorização, MFA, emissão de tokens ou integração
AWS configurados. A infraestrutura Terraform apenas declara provedor e região;
nenhum recurso AWS é provisionado.
