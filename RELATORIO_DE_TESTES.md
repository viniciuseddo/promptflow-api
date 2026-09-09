# Relatório de testes

Validação executada em **08/09/2026**, no Windows, com Python 3.14.3.

## Resultado automatizado

```text
.............                                                            [100%]
13 passed in 0.94s
```

Comando usado:

```bash
pytest
```

Foram verificados:

- conexão SQLite e endpoint de saúde;
- disponibilidade do Swagger e do esquema OpenAPI;
- CRUD completo de templates;
- nome único sem diferença entre maiúsculas e minúsculas;
- validação Pydantic e campos obrigatórios na atualização;
- sintaxe e correspondência das variáveis de prompt;
- bloqueio de execução de template inativo;
- geração local, histórico e filtros;
- proteção contra exclusão de template com histórico;
- recursos inexistentes com HTTP 404;
- provedor externo sem chave com HTTP 503 e persistência da falha.

## Teste de inicialização

O banco foi criado com `python -m scripts.init_db`. Em seguida, a aplicação foi
iniciada com Uvicorn e recebeu as seguintes verificações reais por HTTP:

```text
GET /api/v1/health -> 200 (status=ok, database=connected)
GET /docs          -> 200
```

Os dois avisos exibidos pelo Pytest são de depreciação interna das dependências de
teste FastAPI/Starlette e não representam falha na aplicação.

