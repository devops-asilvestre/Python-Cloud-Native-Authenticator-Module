# Contratos compartilhados

[`src/shared/contracts/`](../../src/shared/contracts/__init__.py) contém os
envelopes genéricos `BaseResponse[T]`, `ErrorResponse` e
`PaginationResponse[T]`. A paginação valida números positivos para página e
tamanho e total não negativo; `total_pages` retorna zero quando não há itens.

Estes são modelos independentes de HTTP e framework. APIs podem mapeá-los para
seus formatos de transporte sem colocar endpoints ou dependências FastAPI no
Shared Kernel. Não inclua stack traces, segredos ou dados pessoais
desnecessários em mensagens/detalhes de erro.
