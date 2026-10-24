# ADR003: Fundação de mensageria SQS

- Status: Aceita
- Contexto: US021 - SQS Foundation
- Data: 2026-10-23

## Contexto

Os bounded contexts precisam publicar e consumir contratos de eventos sem
conhecer o SDK ou a topologia física de filas. As fundações US016, US018 e
US020 fornecem, respectivamente, a integração AWS, os envelopes versionados e
a criptografia KMS.

## Decisão

- Isolar toda interação SQS em `shared.messaging.providers.AwsSqsProvider`,
  criado pelo `AwsClientFactory`.
- Resolver filas por um allowlist de bounded context/event type. O provider
  descobre URLs por `ListQueues` e verifica conta e região pelo ARN; URLs não
  fazem parte da configuração nem dos contratos.
- Serializar somente `EventEnvelope` validado por JSON UTF-8. Consumidores
  validam envelope e schema novamente antes do despacho.
- Executar chamadas síncronas boto3 fora do event loop com `asyncio.to_thread`.
- Fazer long polling sem apagar a mensagem; o chamador só confirma a mensagem
  depois que o handler conclui com sucesso.
- Usar KMS opcionalmente para cifrar o corpo, mantendo apenas metadados
  necessários ao roteamento fora do ciphertext. Logs nunca recebem o corpo.
- Delegar a idempotência a um ciclo durável de claim/completion/release;
  implementações devem usar persistência compartilhada e claims recuperáveis,
  nunca estado em memória de processo.
- Implementar os claims da fundação com a tabela DynamoDB compartilhada,
  condition expressions e tokens de claim para impedir que workers obsoletos
  concluam ou liberem claims adquiridos por outra execução.
- Calcular retries com backoff exponencial limitado e mover mensagens para DLQ
  copiando-as antes de apagar a mensagem de origem.
- Limitar as operações SQS a enviar, receber, apagar, obter atributos e listar
  filas. A fundação não cria, apaga, purga ou reconfigura filas.

## Consequências

Filas, DLQs e suas políticas de redrive devem existir previamente e ser
provisionadas fora desta fundação com menor privilégio. O cliente AWS precisa
das permissões de dados necessárias e de `ListQueues` para resolver URLs.
Handlers devem ser idempotentes e confirmar mensagens apenas após sucesso.
Claims de idempotência precisam expirar ou ser recuperáveis se o worker parar
antes de completar o processamento.
Integrações que usam KMS devem disponibilizar o provider e resolver de chaves
da fundação KMS.

## Alternativas consideradas

- Permitir chamadas boto3 dentro de cada bounded context: rejeitado por
  duplicar segurança, observabilidade e tratamento de erros.
- Configurar URLs de filas: rejeitado por acoplar código a conta, região e
  ambiente e por dificultar validação da identidade da fila.
- Usar estado local para idempotência: rejeitado por não resistir a
  reinicializações nem coordenar réplicas concorrentes.
