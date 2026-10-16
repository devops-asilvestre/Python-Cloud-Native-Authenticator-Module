# Documentação do projeto

Este diretório concentra a documentação oficial do projeto. A implementação
está em `src/identity_service`; os contratos e decisões desta fase inicial
delimitam o scaffold, não funcionalidades de autenticação já prontas.

## Conteúdo

- [Visão arquitetural](architecture/overview.md)
- [Histórias iniciais](user_stories/initial-scope.md)
- [Decisão arquitetural 0001](adr/0001-clean-architecture.md)
- [Baseline de segurança](security/baseline.md)
- [Diagrama de contexto](diagrams/system-context.md)

## Estado inicial

O serviço inclui apenas a aplicação FastAPI, configuração tipada por variáveis
de ambiente e uma rota de liveness. Persistência, cache, MFA, OAuth2/OIDC,
autorização e publicação de eventos ainda precisam de desenho, implementação e
testes próprios antes de qualquer uso em produção.

## Começar

Com Python 3.13 instalado:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
uvicorn identity_service.main:app --reload --app-dir src
```

A API inicia em `http://127.0.0.1:8000`. A documentação OpenAPI fica disponível
em `/docs` no ambiente local; `/health/live` fornece a verificação de liveness.

## Verificações locais

```powershell
ruff check .
mypy src tests
pytest
```
