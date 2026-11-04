# Estratégia de branches

## Convenções

| Tipo | Padrão | Base | Destino |
|---|---|---|---|
| Funcionalidade | `feature/<US>-<slug>` | `developer` | `developer` |
| Correção | `fix/<issue>-<slug>` | `developer` | `developer` |
| Preparação de release | `release/<major>.<minor>.<patch>` | `developer` | `main` e depois `developer` |
| Correção urgente | `hotfix/<major>.<minor>.<patch>-<slug>` | `main` | `main` e depois `developer` |

Use nomes curtos, minúsculos e separados por hífen. Inclua identificador da
história/issue quando disponível. Não inclua nomes de pessoas, dados
confidenciais ou detalhes sensíveis.

## Proteção e ciclo de vida

- Exigir PR para `main` e `developer`, verificações CI e aprovações conforme a
  [política de PR](pull-request-policy.md).
- Desabilitar force push e exclusão das branches permanentes.
- Solicitar CODEOWNER quando arquivos cobertos forem alterados.
- Manter branches curtas; sincronizar com a base usando merge ou rebase local
  antes da revisão, sem reescrever branches compartilhadas.
- Excluir branches temporárias após integração.

As regras de proteção são configuração do GitHub e precisam ser habilitadas
pelos administradores; arquivos versionados não as ativam automaticamente.
