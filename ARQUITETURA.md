# Arquitetura do PromptFlow

O projeto usa uma arquitetura em camadas para reduzir acoplamento:

1. **API (`app/api`)**: recebe HTTP, valida parâmetros e define códigos de resposta.
2. **Schemas (`app/schemas`)**: contratos Pydantic de entrada e saída.
3. **Services (`app/services`)**: regras de negócio, renderização e integração LLM.
4. **Repositories (`app/repositories`)**: consultas e comandos de persistência.
5. **Models (`app/models`)**: entidades relacionais SQLAlchemy.
6. **DB (`app/db`)**: sessão, engine, chave estrangeira e criação das tabelas.
7. **Core (`app/core`)**: configuração e tratamento uniforme de exceções.

## Fluxo de geração

`POST /api/v1/generations` → valida o template → confere atividade e variáveis →
renderiza o prompt → registra a execução → chama o provedor → salva resposta,
status e latência → devolve HTTP 201.

Falhas do provedor também são persistidas com status `failed`, sem expor a chave da
API. O cliente recebe 502, 503 ou 504 conforme a natureza do problema.

## Modelo relacional

- `prompt_templates`: configuração reutilizável de prompts.
- `generations`: histórico das execuções; cada item pertence a um template.

A relação é 1:N e usa chave estrangeira com exclusão restrita. Um template com
histórico deve ser desativado, preservando rastreabilidade.

