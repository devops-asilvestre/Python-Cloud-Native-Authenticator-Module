# Infraestrutura

Esta área contém definições de ambiente e automação de infraestrutura, sem
regras de domínio. A estrutura prepara execução local e evolução AWS; não
provisiona recursos AWS por padrão.

- [`docker/`](docker/README.md): serviços de desenvolvimento local via Compose.
- [`terraform/`](terraform/README.md): estrutura IaC AWS existente e sua
  organização futura.
- [`environments/`](environments/README.md): separação documental de ambientes.
- [`scripts/`](scripts/README.md): automação operacional versionável.

Não armazenar credenciais, arquivos de estado Terraform, outputs sensíveis ou
configuração específica de conta/ambiente no repositório.
