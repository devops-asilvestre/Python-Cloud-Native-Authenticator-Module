# Baseline de segurança

Este baseline orienta o desenvolvimento; não constitui certificação ou
declaração de conformidade.

- **Zero Trust e menor privilégio:** autenticar e autorizar cada operação; negar
  por padrão; limitar permissões de aplicação e infraestrutura ao necessário.
- **Segredos:** não versionar credenciais, chaves privadas, tokens ou arquivos
  `.env`; obter segredos de um gerenciador apropriado em cada ambiente.
- **Transporte e armazenamento:** exigir TLS em trânsito e definir criptografia
  em repouso para dados e backups antes de provisionar recursos.
- **Identidade e tokens:** selecionar fluxos OAuth2/OIDC apropriados, validar
  emissor, audiência, assinatura, expiração e uso; proteger MFA e recuperação de
  conta contra abuso.
- **Multi-tenancy:** incluir o tenant no contexto autenticado e impor isolamento
  em toda leitura, escrita, cache e evento; não confiar em tenant informado
  apenas pelo cliente.
- **Auditoria e privacidade:** minimizar dados pessoais em logs, definir
  retenção, acesso e descarte; avaliar base legal e requisitos LGPD.
- **Resiliência:** aplicar limites, timeouts, validação, proteção contra replay
  quando pertinente e tratamento seguro de erros.
- **Entrega:** executar testes e análise estática no CI; revisar dependências e
  infraestrutura como código antes de releases.

Nenhuma credencial deve ser adicionada ao `.env.example`. O exemplo contém
somente configurações não sensíveis.
