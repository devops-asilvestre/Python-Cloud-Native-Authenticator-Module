# Scripts de infraestrutura

[`local_platform.py`](local_platform.py) fornece os comandos multiplataforma
`start`, `stop`, `restart`, `health-check` e `smoke-test` para o Compose local.
Consulte [LOCAL_DEVELOPMENT.md](../../LOCAL_DEVELOPMENT.md) para configuração
e [SMOKE_TESTS.md](../../SMOKE_TESTS.md) para as verificações executadas.

Não inclua credenciais, segredos ou estado local nos scripts versionados.
