# ADR002: Fundação de contratos de eventos

- Status: Aceita
- Contexto: US018 - Event Contracts Foundation
- Data: 2026-10-23

## Contexto

Os bounded contexts precisam trocar fatos de domínio sem depender diretamente
de barramentos ou de implementações internas de outros contextos. As fundações
de observabilidade e shared kernel já fornecem IDs de correlação/trace e tipos
de domínio reutilizáveis.

## Decisão

- Modelar envelopes, metadados e schemas com Pydantic v2.
- Usar JSON UTF-8 e versões SemVer estáveis em campo separado do nome do evento.
- Exigir tenant, serviço de origem, instante UTC, correlação e trace nos
  envelopes; consumidores continuam responsáveis por autorização e isolamento
  de tenant.
- Exigir nomes `<bounded_context>.<aggregate>.<event>` e registro explícito de
  cada par tipo/versão.
- Validar o payload por schema antes de serialização e após desserialização.
- Manter contratos de publicação/consumo assíncronos e independentes de AWS.
- Não implementar transporte, persistência, retentativas, outbox ou políticas
  de entrega nesta fundação.

## Consequências

Produtores devem definir schemas allowlistados e registrar cada versão antes de
serializar. Consumidores rejeitam tipos, versões, envelopes e payloads não
registrados/compatíveis. Mudanças incompatíveis requerem nova versão major;
eventos e schemas anteriores permanecem disponíveis enquanto houver
consumidores compatíveis.

Eventos carregam apenas dados mínimos. O pacote não mascara payloads
automaticamente e não substitui controles de segurança, autorização por tenant,
retenção ou auditoria. A escolha do barramento e as garantias de entrega ficam
para histórias futuras e ADRs específicos.

## Alternativas consideradas

- Acoplar contratos diretamente ao EventBridge/SQS: rejeitado por acoplar os
  bounded contexts ao transporte.
- Usar nome de evento como único mecanismo de versão: rejeitado porque mistura
  identidade estável e evolução do schema.
- Aceitar payloads sem schema registrado: rejeitado porque não permite validar
  compatibilidade nem limitar os dados publicados.
