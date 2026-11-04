# US025A - Validação do SQS

## Recurso esperado

- Queue: `authentication-events`
- Endpoint: `http://127.0.0.1:4566`
- Target: `authentication-events-to-sqs`

## Inspeção da fila

```powershell
$queueUrl = aws --endpoint-url http://127.0.0.1:4566 sqs get-queue-url `
  --queue-name authentication-events --query QueueUrl --output text
aws --endpoint-url http://127.0.0.1:4566 sqs get-queue-attributes `
  --queue-url $queueUrl --attribute-names All
aws --endpoint-url http://127.0.0.1:4566 sqs receive-message `
  --queue-url $queueUrl --max-number-of-messages 10 --wait-time-seconds 2
```

## Resultado esperado

Depois dos fluxos de login e sessão, `receive-message` deve exibir mensagens
contendo os eventos:

- `authentication.authentication.succeeded`
- `authentication.authentication.failed`
- `authentication.session.created`
- `authentication.session.terminated`

O comando de recebimento é somente de inspeção nesta evidência; não apagar a
mensagem até registrar o payload e o `MessageId`. Os payloads devem ser
sanitizados antes de serem anexados a um relatório compartilhado.

## Observabilidade

O publisher registra sucesso ou falha com `event_id`, `event_type`, tenant,
correlação, trace e latência, sem registrar o payload do evento. Falhas de
`PutEvents` são explícitas e propagadas como
`EventBridgePublishException`.
