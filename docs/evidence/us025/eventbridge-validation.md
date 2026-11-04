# US025A - Validação do EventBridge

## Recursos esperados

| Recurso | Valor |
|---|---|
| Event bus | `authenticator-bus` |
| Rule | `authentication-events-to-sqs` |
| Padrões roteados | `authentication.authentication.succeeded`, `authentication.authentication.failed`, `authentication.session.created`, `authentication.session.terminated` |
| Endpoint | `http://127.0.0.1:4566` |

## Inspeção

```powershell
aws --endpoint-url http://127.0.0.1:4566 events describe-event-bus `
  --name authenticator-bus
aws --endpoint-url http://127.0.0.1:4566 events describe-rule `
  --event-bus-name authenticator-bus `
  --name authentication-events-to-sqs
aws --endpoint-url http://127.0.0.1:4566 events list-targets-by-rule `
  --event-bus-name authenticator-bus `
  --rule authentication-events-to-sqs
```

As chamadas devem retornar o bus, a rule habilitada e um target SQS. A
aplicação usa `AUTHENTICATOR_EVENTBRIDGE_ENDPOINT_URL` para apontar o
publisher compartilhado para o LocalStack; em AWS real, a variável deve ficar
ausente.

## Fluxo de certificação

1. Executar `POST /authentication/login` com credenciais válidas.
2. Repetir com credenciais inválidas.
3. Criar e terminar uma sessão.
4. Confirmar os quatro `detail-type` na fila descrita em
   [sqs-validation.md](./sqs-validation.md).

## Contrato preservado

Os eventos continuam sendo publicados pelo
[`EventBridgePublisher`](../../../src/shared/eventbus/publishers/eventbridge_publisher.py)
com `EventEnvelope`, tenant, correlação, trace e versão existentes.
