# Fundação EventBridge

Este pacote centraliza o uso corporativo do EventBridge. Bounded contexts não
devem importar boto3 para publicar eventos; devem usar `EventBridgePublisher`.

O publisher:

1. valida `EventEnvelope`, tenant, versão e rastreabilidade;
2. resolve o barramento por categoria;
3. aplica filtros e fanout;
4. registra auditoria sem payload;
5. chama `PutEvents` através de `EventBridgeProvider`;
6. expõe metadados de replay/archive e observabilidade.

O `EventBridgeProvider` aceita um cliente injetado para testes e, em produção,
usa o `AwsClientFactory` compartilhado. A proteção opcional dos detalhes pode
ser fornecida por um callable baseado na fundação KMS, sem registrar o payload.
