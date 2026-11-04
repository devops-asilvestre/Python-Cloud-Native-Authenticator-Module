# Arquitetura do Shared Kernel

## Propósito e limites

O pacote [`src/shared/`](../../src/shared/__init__.py) é o único ponto de
compartilhamento de código técnico da plataforma. Seus contratos apoiam os
bounded contexts sem compartilharem seus modelos ou regras de negócio.
Aplicações e domínios podem depender dos contratos; o Shared Kernel não depende
de aplicações, infraestrutura, serviços AWS, bancos de dados ou frameworks.

```text
src/shared/
├── kernel/          # identidade, valores, agregados, eventos, Result e Clock
├── events/          # contrato, metadados, serializador e versão
├── contracts/       # envelopes e paginação
├── observability/   # correlação, logs, traces e métricas
├── security/        # interfaces de hashing/JWT e mascaramento
└── testing/         # fixtures, factories e helpers para testes
```

As pastas de código ficam em `src/shared/`; `shared/` na raiz contém a
documentação dos componentes.

## Decisões de desenho

- O kernel fornece abstrações pequenas e sem comportamento de domínio.
- Eventos de domínio e eventos de integração não compartilham esquemas
  concretos; cada contexto é dono dos seus tipos públicos.
- `Clock` permite substituir o tempo do sistema por um relógio controlado em
  testes; `SystemClock` usa UTC.
- `Result` representa sucesso ou erro explicitamente e sinaliza acesso à
  variante inexistente com `ResultAccessError`.
- Interfaces de segurança e observabilidade não selecionam provedores,
  algoritmos, instrumentação ou configuração.
- Contratos de resposta não impõem transporte HTTP nem tipos do FastAPI.
- IDs, metadados e eventos genéricos não devem conter segredos ou payloads
  além do necessário.

## Dependências permitidas

O código compartilhado usa somente a biblioteca padrão do Python. Adaptadores
de infraestrutura implementam seus Protocols e podem depender de SDKs
específicos; nunca o contrário. Nenhuma integração AWS, persistência,
autenticação, autorização, endpoint ou regra de negócio é implementada aqui.

## Verificação

Na raiz do repositório, valide o pacote com:

```powershell
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe src tests
.\.venv\Scripts\pytest.exe -q
```

Os testes específicos do kernel estão em
[`tests/unit/shared_kernel/`](../../tests/unit/shared_kernel/__init__.py), e o
exemplo de consumo em [`examples/shared_kernel_usage.py`](../../examples/shared_kernel_usage.py).
