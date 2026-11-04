# Estratégia de GitHub Actions

## Workflows

| Workflow | Eventos | Responsabilidade |
|---|---|---|
| `CI` | Push e PR para `developer`/`main` | Ruff, mypy, pytest e relatório de cobertura |
| `Security` | Push/PR para branches protegidas, agenda semanal e execução manual | pip-audit, Bandit e Dependency Review em PR |
| `CodeQL` | Push/PR para branches protegidas, agenda semanal e execução manual | Análise estática Python com consultas estendidas |
| `Release` | Tag estável `vX.Y.Z` | Validação de tag, build de wheel/sdist e GitHub Release |

## Controles

- Usar runners hospedados efêmeros e limitar cada workflow por timeout.
- Declarar permissões globais mínimas e ampliar somente no job que precisa.
- Usar `concurrency` para cancelar execuções redundantes, exceto releases.
- Não executar código de PR não confiável com secrets, tokens de escrita ou
  `pull_request_target`.
- Manter Actions oficiais e dependências de workflow revisadas e atualizadas;
  adotar pin por SHA imutável quando o processo do repositório permitir.
- Usar cache apenas para acelerar dependências, nunca para compartilhar segredos
  ou artefatos de confiança entre contextos não confiáveis.
- Proteger branches e exigir status checks nas configurações do repositório.
- Revisar logs e artefatos para não expor tokens, dados pessoais ou configurações.

## Operação

Workflows não fazem deploy nem armazenam credenciais. Para incluir publicação
externa ou deploy, usar OIDC/federação quando suportado, GitHub Environments,
aprovação para produção e permissões restritas ao job. Falhas de security scan
devem ser tratadas como gates, não silenciosamente ignoradas.
