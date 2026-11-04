# Métricas DORA

## Uso pretendido

As quatro métricas DORA ajudam a entender o sistema de entrega e orientar
experimentos de melhoria; não são metas individuais nem indicadores para
comparar equipes fora de contexto. Interpretar tendências por período e junto
com estabilidade, segurança e qualidade.

## Definições e coleta

- **Deployment frequency:** frequência de releases implantadas em um ambiente
  por período. O repositório atualmente publica GitHub Releases, mas não registra
  deploys; medir deploy somente após instrumentar o ambiente e os eventos de
  implantação.
- **Lead time for changes:** tempo entre o primeiro commit de uma mudança e sua
  disponibilização em produção. Usar histórico Git e eventos de deploy com
  definição consistente de início e fim.
- **Change failure rate:** proporção de deploys que causam incidente ou exigem
  rollback/hotfix dividido pelo total de deploys no período. Definir critérios
  de falha e vincular incidentes/releases.
- **Failed deployment recovery time:** tempo entre falha de deploy e restauração
  do serviço. Registrar início do impacto e recuperação com timestamps
  operacionais.

## Próximos passos

Neste estágio, não há dados suficientes para calcular as métricas de entrega
com confiança. Estabelecer baseline quando houver deploy instrumentado, manter
definições estáveis, desagregar por serviço quando relevante e revisar tendências
periodicamente. O tempo de execução de CI e a taxa de falha de build podem ser
acompanhados como indicadores internos, mas não devem ser apresentados como
substitutos das quatro métricas DORA.
