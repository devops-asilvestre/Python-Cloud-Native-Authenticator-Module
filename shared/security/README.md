# Segurança compartilhada

[`src/shared/security/`](../../src/shared/security/__init__.py) oferece os
contratos `PasswordHasher` e `JwtService`, além de `mask_sensitive_data` para
estruturas aninhadas. Não há algoritmo de hashing, implementação JWT ou
criptografia nesta fundação: essas escolhas e suas dependências pertencem aos
adaptadores de infraestrutura aprovados.

O mascaramento considera nomes normalizados de campos conhecidos, como
`password`, `token`, `access-token`, `api_key` e `private_key`, e devolve uma
cópia da estrutura. Revise/adapte a lista para os campos da aplicação. Não
adicione segredos, configuração sensível, políticas de domínio ou código que
contorne o proprietário de um bounded context. Identidade de tenant deve vir
de contexto validado no servidor.
