# Shared Kernel e componentes compartilhados

O pacote Python reutilizável está em [`src/shared/`](../src/shared/__init__.py);
esta pasta documenta seus limites. Tipos aqui devem ser técnicos, estáveis e
independentes de qualquer bounded context. Compartilhar código não deve criar
dependências entre modelos ou ciclos entre contextos.

| Diretório | Escopo permitido |
|---|---|
| [`kernel/`](kernel/README.md) | Entidade, value object, aggregate root, evento, exceção, Result e Clock. |
| [`events/`](events/README.md) | Contratos de eventos, metadados, serialização e versão. |
| [`contracts/`](contracts/README.md) | Envelopes de resposta, erros e paginação. |
| [`observability/`](observability/README.md) | IDs de correlação e contratos de logs, traces e métricas. |
| [`security/`](security/README.md) | Contratos de hashing/JWT e mascaramento de dados sensíveis. |
| [`persistence/`](../src/shared/persistence/README.md) | Configuração, engine, sessão assíncrona, unit of work, isolamento de tenant e migrações Alembic para PostgreSQL. |
| `testing/` | Fixture, factory e helpers reutilizáveis nos testes. |

Não coloque aqui entidades, repositórios, regras de negócio, modelos de
persistência ou serviços que coordenem contextos. Um contexto não deve depender
diretamente de outro contexto, mesmo por meio de código compartilhado.

## Guia de utilização

Os imports públicos são feitos a partir de `shared`. Exemplos:

```python
from shared.kernel import AggregateRoot, DomainEvent, Result, ValueObject
from shared.contracts.pagination import PaginationResponse
from shared.security.masking import mask_sensitive_data
```

`Entity` representa identidade; `ValueObject` deve declarar uma propriedade
`value` completa e imutável; `AggregateRoot` coleta eventos até que o chamador
os consuma com `pull_domain_events()`. `Result.success(value)` e
`Result.failure(error)` tornam sucesso e falha explícitos: acessar a variante
errada levanta `ResultAccessError`, sem retornar valores vazios.

Interfaces como `Clock`, `EventSerializer`, `PasswordHasher`, `JwtService`,
`StructuredLogger` e `Tracer` são contratos para implementação nas camadas de
infraestrutura. Este pacote não escolhe algoritmo criptográfico, formato de
serialização, backend de telemetria ou provedor de nuvem. Nunca registre
tokens, senhas ou claims completos; use `mask_sensitive_data` para mascarar
campos sensíveis conhecidos antes de expor estruturas.

Um exemplo executável mínimo está em
[`examples/shared_kernel_usage.py`](../examples/shared_kernel_usage.py).
Decisões e limites arquiteturais estão em
[`docs/architecture/shared-kernel.md`](../docs/architecture/shared-kernel.md).
