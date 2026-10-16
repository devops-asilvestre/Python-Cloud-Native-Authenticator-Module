# Estratégia de ambientes

## Ambientes lógicos

- **Local:** desenvolvimento isolado, configurações não sensíveis e serviços
  locais/fakes. Usar `.env.example` como referência sem adicionar credenciais.
- **CI:** runners efêmeros do GitHub Actions. Instalar dependências declaradas,
  não reutilizar credenciais pessoais e descartar o ambiente após o job.
- **Desenvolvimento/integração:** destino futuro para validar integração de
  componentes; não existe deploy automatizado configurado neste repositório.
- **Homologação e produção:** ambientes futuros, separados, com aprovação,
  acesso mínimo, observabilidade e procedimento de rollback. Não estão
  provisionados por esta estratégia.

## Configuração e segredos

Manter configuração específica do ambiente fora do código e aplicar defaults
locais apenas quando forem seguros. Não armazenar segredos em Git, logs,
artefatos, outputs ou issue/PR. Usar gerenciador de segredos do ambiente e
preferir federação de identidade a credenciais estáticas nos workflows.

Quando forem adicionados deploys, usar GitHub Environments separados, restringir
branches/tags permitidos, exigir aprovação para produção e limitar secrets ao
ambiente que precisa deles. Nunca promover dados pessoais reais entre ambientes
sem autorização, minimização e controles de privacidade.
