# Componentes compartilhados

Esta área é reservada a contratos estáveis e capacidades técnicas transversais.
Compartilhar código não deve criar dependências entre modelos ou ciclos entre
bounded contexts.

| Diretório | Escopo permitido |
|---|---|
| [`kernel/`](kernel/README.md) | Tipos técnicos mínimos, independentes de domínio. |
| [`events/`](events/README.md) | Convenções e contratos de eventos versionados. |
| [`observability/`](observability/README.md) | Instrumentação e convenções OpenTelemetry. |
| [`security/`](security/README.md) | Primitivas e convenções de segurança transversais. |

Não coloque aqui entidades, repositórios, regras de negócio, modelos de
persistência ou serviços que coordenem contextos. Um contexto não deve depender
diretamente de outro contexto, mesmo por meio de código compartilhado.
