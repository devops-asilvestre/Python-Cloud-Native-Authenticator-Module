# Gates de segurança

## Verificações automatizadas

- **CodeQL:** análise Python com consultas `security-extended` em branches
  protegidas, pull requests, execução semanal e disparo manual.
- **Bandit:** análise estática de `src/`, com severidade e confiança mínimas
  médias, em pull requests, branches protegidas e execução semanal.
- **pip-audit:** auditoria das dependências instaladas do projeto, incluindo
  extras de desenvolvimento, nos mesmos eventos.
- **Dependency Review:** comparação de dependências introduzidas pelo PR;
  bloqueia vulnerabilidades classificadas como alta ou crítica.

## Critérios de bloqueio e resposta

Resultados de alta/crítica devem ser triados antes do merge. Corrigir, atualizar
ou remover a dependência vulnerável; para falso positivo ou risco aceito,
registrar evidência, impacto, responsável, validade e aprovação na issue/PR.
Achados de severidade inferior também devem ser priorizados conforme
explorabilidade e impacto no serviço de identidade.

Tratar alertas do CodeQL/Bandit com revisão contextual: corrigir defeitos reais
e documentar exceções específicas, sem desabilitar a análise globalmente. Uma
falha do scanner não equivale a resultado aprovado e deve ser resolvida antes
do merge, ou seguir exceção formal de incidente.

## Controles de processo

- Manter permissões de Actions no mínimo necessário; não expor secrets a
  workflows de pull requests de forks.
- Habilitar secret scanning e push protection no GitHub quando disponíveis.
- Revisar alertas de dependência, permissões e políticas de branch regularmente.
- CI e scanners não substituem modelagem de ameaças, revisão humana, testes de
  autorização/isolamento multi-tenant ou validação operacional.

Configure os status obrigatórios e os recursos de segurança do repositório no
GitHub; a presença dos arquivos workflow, por si só, não ativa essas políticas.
