# Kernel compartilhado

Implementações Python em [`src/shared/kernel/`](../../src/shared/kernel/__init__.py)
fornecem os tipos genéricos `Entity`, `ValueObject`, `AggregateRoot`,
`DomainEvent`, `DomainException`, `Result`, `Clock` e `SystemClock`.

`Entity` compara por tipo concreto e identificador. Cada subtipo de
`ValueObject` declara sua propriedade `value`; essa propriedade deve representar
todo o valor imutável. `AggregateRoot` acumula eventos genéricos e os entrega
como tupla por `pull_domain_events()`. O relógio do sistema sempre retorna
`datetime` com timezone UTC. `Result` exige a leitura da variante correta.

Não adicione entidades ou value objects de negócio, regras de domínio,
repositórios, clientes AWS, persistência ou dependências de bounded contexts.
Eventos concretos continuam pertencendo ao domínio que os define.
