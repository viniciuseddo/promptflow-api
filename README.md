# PromptFlow API

Backend da CP1 AICSS + Python para administrar templates de prompts e gerar
descrições de produtos de e-commerce por meio de modelos de linguagem.

## Identificação

- **Tema escolhido:** 6 — Consumo de API LLMs.
- **Problema específico:** padronizar a criação de descrições de produtos usando
  templates reutilizáveis, variáveis validadas e histórico auditável.
- **Repositório GitHub:** `[PREENCHER URL DO REPOSITÓRIO - OBRIGATÓRIO]`
- **Trello:** `[PREENCHER URL DO QUADRO - OBRIGATÓRIO]`

### Integrantes

1. `[PREENCHER NOME COMPLETO - OBRIGATÓRIO]`
2. `[PREENCHER NOME COMPLETO - OBRIGATÓRIO]`
3. `[PREENCHER NOME COMPLETO OU REMOVER SE FOR DUPLA]`

Não foram inventados nomes. Os mesmos nomes devem constar em `integrantes.txt`.

## Funcionalidades e regras de negócio

- CRUD de templates de prompt.
- Nome de template único, ignorando maiúsculas/minúsculas.
- Placeholders no formato `{{variavel}}`, com rejeição de campos ausentes ou extras.
- Templates inativos não podem gerar conteúdo.
- Histórico persistente com prompt renderizado, resposta, provedor, status e latência.
- Templates com histórico não podem ser apagados; devem ser desativados.
- Dois provedores: `local` para apresentação sem chave e `openai_compatible` para
  consumo real de `/chat/completions`.
- Respostas de erro padronizadas e códigos HTTP adequados.

## Tecnologias

Python 3.10+, FastAPI, Pydantic, SQLAlchemy ORM, SQLite, HTTPX, Uvicorn e Pytest.
O Swagger/OpenAPI é gerado automaticamente em `/docs`.

## Arquitetura

```text
app/
├── api/routes/       # endpoints HTTP
├── core/             # configurações e exceções
├── db/               # engine, sessões e criação das tabelas
├── models/           # entidades SQLAlchemy
├── repositories/     # acesso ao banco
├── schemas/          # entradas e saídas Pydantic
└── services/         # regras de negócio e integração LLM
docs/                 # arquitetura e planejamento ágil
scripts/              # inicialização explícita do banco
tests/                # testes automatizados
```

Detalhes adicionais estão em `docs/ARQUITETURA.md`. A metodologia Kanban e o
backlog pronto para cadastrar no Trello estão em `docs/PLANEJAMENTO_AGIL.md`.

## Como executar

### 1. Preparar o ambiente

No terminal, dentro da pasta do projeto:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Inicializar e iniciar

```bash
python -m scripts.init_db
uvicorn app.main:app --reload
```

A aplicação estará em `http://127.0.0.1:8000` e a documentação interativa em
`http://127.0.0.1:8000/docs`. A inicialização da API também cria as tabelas caso
elas ainda não existam.

## Configuração do provedor LLM

O `.env.example` usa `LLM_PROVIDER=local`, que é determinístico e não exige chave.
Para uma API real compatível com o formato OpenAI, altere o `.env`:

```dotenv
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sua-chave
LLM_TIMEOUT_SECONDS=30
```

O `.env` e o banco local são ignorados pelo Git. Nunca envie uma chave no ZIP ou
no GitHub. O adaptador pode apontar para outros serviços que implementem
`POST /chat/completions`.

## Endpoints

| Método | Rota | Resultado |
|---|---|---|
| GET | `/api/v1/health` | Saúde da API e do banco |
| POST | `/api/v1/templates` | Cria template (201) |
| GET | `/api/v1/templates` | Lista templates (200) |
| GET | `/api/v1/templates/{id}` | Consulta template (200/404) |
| PATCH | `/api/v1/templates/{id}` | Atualiza template (200) |
| DELETE | `/api/v1/templates/{id}` | Exclui sem histórico (204/409) |
| POST | `/api/v1/generations` | Executa template e registra histórico (201) |
| GET | `/api/v1/generations` | Lista histórico com filtros (200) |
| GET | `/api/v1/generations/{id}` | Consulta geração (200/404) |
| DELETE | `/api/v1/generations/{id}` | Exclui geração (204/404) |

Filtros de histórico: `template_id`, `status`, `offset` e `limit`.

## Exemplo completo

Crie um template em `/docs` ou por terminal:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{"name":"Descrição sustentável","description":"Texto para e-commerce","system_prompt":"Você é um redator objetivo.","user_prompt_template":"Crie uma descrição de {{produto}} para {{publico}}.","model":"demo-model","temperature":0.4,"active":true}'
```

Depois use o `id` retornado:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/generations \
  -H "Content-Type: application/json" \
  -d '{"template_id":1,"variables":{"produto":"garrafa térmica","publico":"trilheiros"}}'
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes usam um SQLite temporário e cobrem saúde, Swagger, CRUD, duplicidade,
sintaxe inválida, validação Pydantic, geração, filtros, template inativo, proteção
do histórico e respostas 404.

## Códigos de resposta e erros

- `200`, `201`, `204`: operações bem-sucedidas.
- `404`: recurso inexistente.
- `409`: duplicidade ou exclusão que quebraria o histórico.
- `422`: validação ou regra de negócio.
- `502`, `503`, `504`: falha, configuração ausente ou timeout do provedor LLM.
- `500`: erro inesperado sem exposição de detalhes internos.

Formato padronizado:

```json
{
  "error": {
    "code": "business_rule_violation",
    "message": "As variáveis não correspondem ao template.",
    "details": {"missing": ["publico"], "unexpected": []}
  }
}
```

## Publicação no GitHub

1. Preencha nomes e links pendentes.
2. Crie um repositório público ou conceda acesso ao professor.
3. Confirme que `.env`, `.venv` e `*.db` não foram incluídos.
4. Envie esta pasta e valide novamente as instruções acima a partir de um clone.
