# Contratos de eventos

Reservado a convenções e contratos de integração assíncrona versionados. Os
contextos produtores são responsáveis por seus eventos; consumidores não
devem depender de classes internas do produtor.

Eventos devem conter somente os dados mínimos necessários. Não publicar
senhas, material de fatores, tokens, códigos de autorização, chaves privadas,
claims completos ou outros segredos/dados excessivos. A escolha e configuração
de EventBridge/SQS, outbox, ordenação, retentativas e retenção ficam para
histórias futuras. Nenhum evento está implementado nesta fundação.
