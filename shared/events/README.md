# Contratos de eventos

[`src/shared/events/`](../../src/shared/events/__init__.py) define o contrato
agnóstico de transporte `EventContract`, `EventMetadata`, `EventVersion` e a
interface `EventSerializer`. Contextos produtores continuam responsáveis por
seus eventos; consumidores não devem depender de classes internas do produtor.

Metadados incluem UUID, instante UTC e IDs de correlação/requisição/trace
opcionais. `EventVersion` exige versão major positiva e minor não negativa.
Eventos devem conter somente os dados mínimos necessários. Não publique
senhas, material de fatores, tokens, códigos de autorização, chaves privadas,
claims completos ou outros segredos/dados excessivos. Formato de serialização,
EventBridge/SQS, outbox, ordenação, retentativas e retenção pertencem às
histórias de integração; esta fundação não implementa transporte.
