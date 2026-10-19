# Serviços e bounded contexts

Cada diretório de serviço representa um limite de modelo e de propriedade de
dados; não implica que cada contexto já tenha um processo implantável. Os seis
diretórios específicos são placeholders arquiteturais para evolução futura.

| Diretório | Contexto |
|---|---|
| [`tenant-service/`](tenant-service/README.md) | Tenant & Organization |
| [`identity-directory-service/`](identity-directory-service/README.md) | Identity Directory |
| [`authentication-service/`](authentication-service/README.md) | Authentication & Assurance |
| [`authorization-service/`](authorization-service/README.md) | Authorization & Policy |
| [`protocol-service/`](protocol-service/README.md) | Identity Protocols & Clients |
| [`audit-service/`](audit-service/README.md) | Audit & Privacy |

## Regras de isolamento

- Cada contexto é autoridade sobre seus próprios modelos e dados.
- Não importe módulos internos de outro serviço nem compartilhe sua persistência.
- Use contratos explícitos para interações síncronas e eventos versionados para
  integração assíncrona. O transporte não define o modelo de domínio.
- Mantenha adaptadores de tecnologia fora do domínio e trate indisponibilidade
  de dependências com segurança, sem permissões implícitas.
- A implementação FastAPI já existente permanece em `src/identity_service`.
  A migração para deploys independentes depende de decisões e histórias futuras.

Veja o [mapa de domínios e contextos](../docs/architecture/domain-and-context-map.md).
