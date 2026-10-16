# Catálogo de eventos

Este catálogo é uma proposta inicial de eventos de integração. Publicar um
evento é diferente de emitir um evento interno de domínio: o primeiro é um
contrato para outros contextos e precisa ser minimizado, versionado, compatível
e resiliente. Nenhum dos eventos abaixo está implementado.

## Envelope proposto

Cada evento publicado deve conter apenas metadados comuns e o payload mínimo
necessário:

| Campo | Uso |
|---|---|
| `event_id` | Identificador global para deduplicação/idempotência. |
| `event_type` | Nome estável e versionado, por exemplo `identity.status-changed.v1`. |
| `occurred_at` | Instante UTC em que ocorreu a mudança, não o instante de entrega. |
| `tenant_id` | Escopo do evento, obrigatório quando aplicável; protegido contra acesso cross-tenant. |
| `aggregate_id` | Identificador opaco do agregado afetado. |
| `correlation_id` | Correlação entre requisição e efeitos assíncronos, sem dados pessoais embutidos. |
| `causation_id` | Identificador opcional do comando/evento que causou a mudança. |
| `data` | Campos allowlisted específicos do evento; sem payload genérico de entidade. |

Versões incompatíveis exigem novo tipo de evento. Consumidores devem tolerar
entrega pelo menos uma vez, validar envelope e versão, ser idempotentes e
rejeitar ou encaminhar eventos inválidos para tratamento operacional visível.
Ordenação global não é garantida; quando necessária, definir chave de
particionamento e semântica por agregado.

## Eventos propostos

| Tipo (versão inicial) | Produtor / fato ocorrido | Consumidores previstos | Dados específicos mínimos |
|---|---|---|---|
| `tenant.created.v1` | Tenant & Organization: tenant criado. | Audit & Privacy; provisioning/configuração. | `tenant_id`, plano/configuração inicial não sensível. |
| `tenant.status-changed.v1` | Tenant & Organization: tenant suspenso, reativado ou encerrado. | Directory, Authentication, Authorization, Protocols, Audit. | `tenant_id`, `previous_status`, `new_status`, `reason_code` controlado. |
| `identity.registered.v1` | Identity Directory: identidade registrada. | Authentication, Audit; notificações se política permitir. | `identity_id`, `tenant_id`, origem do cadastro. Sem email ou perfil completo por padrão. |
| `identity.attributes-changed.v1` | Identity Directory: atributos autorizados foram alterados. | Authorization, Audit. | `identity_id`, `tenant_id`, nomes dos atributos alterados sem valores, versão do agregado. |
| `identity.status-changed.v1` | Identity Directory: estado da identidade mudou. | Authentication, Authorization, Protocols, Audit. | `identity_id`, `tenant_id`, estado anterior/novo, `reason_code`. |
| `authentication.succeeded.v1` | Authentication & Assurance: autenticação concluída. | Audit & Privacy; detecção de risco. | `identity_id`, `tenant_id`, método/fator categorizado, `assurance_level`, `correlation_id`. |
| `authentication.failed.v1` | Authentication & Assurance: tentativa não autenticada. | Audit & Privacy; detecção de abuso. | `tenant_id` se conhecido, identificador opaco da tentativa, `reason_code` genérico, timestamp. Sem senha, OTP ou token. |
| `authenticator.enrolled.v1` | Authentication & Assurance: fator inscrito após verificação. | Audit & Privacy; notificações de segurança. | `identity_id`, `tenant_id`, tipo categorizado e identificador do fator opaco. Nunca seed/segredo. |
| `authenticator.revoked.v1` | Authentication & Assurance: fator revogado. | Audit & Privacy; detecção de risco. | `identity_id`, `tenant_id`, identificador opaco do fator e `reason_code`. |
| `authorization.policy-published.v1` | Authorization & Policy: versão de política publicada. | Audit & Privacy; invalidadores de cache, se aplicável. | `tenant_id`, `policy_id`, `policy_version`, hash de conteúdo sem política completa. |
| `authorization.access-denied.v1` | Authorization & Policy: decisão de acesso negada e selecionada para auditoria. | Audit & Privacy; detecção de risco. | `tenant_id`, sujeito/recurso opacos, ação categorizada, `reason_code`, versão de política. |
| `oauth-client.registered.v1` | Identity Protocols & Clients: cliente registrado. | Audit & Privacy; provisioning. | `tenant_id`, `client_id` opaco, tipo de cliente, configuração de grant permitida. Sem segredo de cliente. |
| `oauth-client.revoked.v1` | Identity Protocols & Clients: cliente revogado. | Audit & Privacy; invalidadores de cache/sessão, se aplicável. | `tenant_id`, `client_id` opaco, `reason_code`. |
| `token.issued.v1` | Identity Protocols & Clients: token emitido com sucesso, quando requerido para auditoria. | Audit & Privacy; análise de segurança. | `tenant_id`, sujeito e cliente opacos, tipo de token, scopes categorizados, expiração. Nunca token, claims completos ou segredo. |

`authentication.failed`, `authorization.access-denied` e `token.issued` podem
ter alto volume ou carregar metadados correlacionáveis. Sua publicação,
amostragem (se permitida), controles antiabuso, retenção e necessidade legal
devem ser definidos antes de habilitá-los. Amostragem não pode comprometer
controles de segurança nem ser apresentada como trilha completa de auditoria.

## Controles de segurança e privacidade

- Não incluir senhas, respostas/segredos MFA, códigos de recuperação, tokens,
  authorization codes, client secrets, chaves privadas, cookies, cabeçalhos de
  autorização ou payloads completos de claims.
- Preferir IDs opacos e códigos de razão allowlisted. Email, IP, user-agent,
  conteúdo de perfil ou atributos ABAC podem ser dados pessoais: não adicionar
  sem finalidade, base legal, controle de acesso e retenção aprovados.
- Validar que tenant e ator vieram de contexto confiável; consumidores devem
  impor autorização por tenant e não confiar apenas no nome de fila ou no
  campo `tenant_id`.
- Restringir publicação/consumo com IAM de menor privilégio, criptografia em
  trânsito e em repouso, DLQ protegida e monitoramento de falhas/replays.
- Usar outbox transacional ou mecanismo equivalente para evitar perda entre
  gravação de estado e publicação. Definir deduplicação, retries, replay,
  ordenação por agregado, retenção e descarte em ADR.
- Propagar `correlation_id`/`causation_id` sem usá-los para guardar dados
  sensíveis. Logs e traces não substituem o registro de auditoria.

## Relação com o mapa de contextos

Os produtores e consumidores são detalhados em
[`domain-and-context-map.md`](domain-and-context-map.md#context-map). O
EventBridge/SQS são opções de transporte planejadas, não parte do contrato de
domínio. O armazenamento de auditoria, garantias de entrega e política de
retenção ainda são decisões em aberto.
