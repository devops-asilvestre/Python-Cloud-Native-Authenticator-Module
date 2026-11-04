# CERT-US025-001 - EventBridge validation

## Recursos esperados

| Recurso | Valor |
|---|---|
| Configured bus | `authenticator-bus` |
| Authentication bus used by publisher | `authentication-bus` |
| Rule | `authentication-events-to-sqs` |
| Padrões roteados | `authentication.authentication.succeeded`, `authentication.authentication.failed`, `authentication.session.created`, `authentication.session.terminated` |
| Endpoint | `http://127.0.0.1:4566` |
| Local account | `000000000000` |

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

As chamadas devem retornar o bus, a rule habilitada e um target SQS. Durante
esta certificação, o publisher resolveu `authentication-bus`; esse barramento
e a mesma regra/target foram provisionados no LocalStack para alinhar a
topologia efetiva ao contrato do publisher.
aplicação usa `AUTHENTICATOR_EVENTBRIDGE_ENDPOINT_URL` para apontar o
publisher compartilhado para o LocalStack; em AWS real, a variável deve ficar
ausente.

## Resultado

**PASS** - o barramento `authentication-bus` foi criado, a regra
`authentication-events-to-sqs` ficou `ENABLED` e possui um target SQS.

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
