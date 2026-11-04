# Terraform

Esta pasta contém a configuração AWS inicial existente (`versions.tf`,
`providers.tf` e `variables.tf`). Ela define requisito de versão e provider, mas
ainda não declara recursos, backend remoto ou ambientes implantáveis.

Adicione recursos em módulos com escopo explícito e componha-os por ambiente
em `infrastructure/environments/`. Planeje IAM de menor privilégio, isolamento
de estado, KMS e Secrets Manager antes de qualquer implantação. Não versione
arquivos de estado, credenciais, arquivos `.tfvars` sensíveis nem valores de
segredos. Nenhum recurso AWS é criado por esta fundação.
