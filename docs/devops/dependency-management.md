# Gerenciamento de dependências

## Fonte de verdade

`pyproject.toml` declara dependências de runtime, extras de desenvolvimento,
intervalos de versão, versão mínima do Python e configuração de ferramentas.
`requirements/base.txt` e `requirements/dev.txt` são interfaces de instalação
auxiliares e devem permanecer coerentes com o manifesto principal.

## Inclusão e atualização

- Adicionar somente dependências necessárias; preferir biblioteca padrão ou
  dependência já adotada se atender aos requisitos.
- Definir intervalos compatíveis com SemVer e atualizar os arquivos relacionados
  no mesmo PR.
- Revisar mantenedor, licença, atividade, transitive dependencies, superfície de
  ataque, política de suporte e impacto no pacote.
- Executar testes, Ruff, mypy e auditoria de vulnerabilidades após a alteração.
- Atualizar dependências de Actions e scanners de forma controlada e revisada.

## Vulnerabilidades e reprodutibilidade

O workflow de segurança roda pip-audit e Dependency Review. Tratar alertas
prioritários antes de merge; exceções precisam de risco aceito, owner, prazo e
plano de correção registrados. Não há lockfile de produção versionado: se a
necessidade de builds reprodutíveis exigir um, escolher e documentar uma
estratégia de lock compatível com a distribuição de biblioteca Python antes de
adicioná-lo.

Nunca atualizar dependências em produção sem validação, nem introduzir fontes
privadas ou tokens de registry no repositório.
