# Ambientes de infraestrutura

Área reservada à composição da infraestrutura por ambiente AWS. Cada ambiente
futuro deve ter identidade, configuração, permissões e estado Terraform
segregados; valores sensíveis devem ser obtidos de provedores de segredos e
nunca versionados.

Esta pasta ainda não define ambientes implantáveis nem recursos cloud. O
ambiente local em Docker está documentado em `infrastructure/docker/`.
