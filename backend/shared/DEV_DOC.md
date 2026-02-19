# Shared Middlewares & Logging - Guia do Desenvolvedor

## 📦 Visão Geral

Este pacote compartilhado padroniza **logging estruturado** e **middlewares** para todos os microsserviços do backend.  
**Objetivo**: Logs consistentes no formato JSON para o ELK, com correlação entre serviços.

## 🏗️ Estrutura

```
shared/
├── setup.py               # Instalação do pacote
└── shared/
    ├── __init__.py        # Exporta funções principais
    ├── logging/
    │   ├── config.py      # Configuração do structlog
    │   └── processors.py  # Processadores customizados
    └── middlewares/
        ├── request_context.py  # request_id, timing
        ├── auth.py             # Autenticação JWT
        └── logging.py          # Log de requisições
```

## 🚀 Como usar em seu serviço

### 1. Adicione a dependência

No `requirements.txt` do seu serviço:

```txt
fastapi
uvicorn
-e ../shared  # Caminho relativo para o pacote compartilhado
```

Instale:

```bash
pip install -r requirements.txt
```

### 2. Configure no `main.py`

```python
from fastapi import FastAPI
from shared import (
    configure_logging,
    request_context_middleware,
    auth_middleware,
    logging_middleware,
)

# 1. Configure o logging com o nome do SEU serviço
configure_logging("nome-do-seu-servico")  # ex: "game", "tournament", "emails"

# 2. Crie a app FastAPI
app = FastAPI()

# 3. Adicione os middlewares (ORDEM É IMPORTANTE!)
app.middleware("http")(request_context_middleware())  # 1º: contexto básico
app.middleware("http")(auth_middleware())             # 2º: autenticação
app.middleware("http")(logging_middleware())          # 3º: log final

# 4. Suas rotas
@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 📝 Como fazer logs no seu código

Em qualquer arquivo:

```python
import structlog

logger = structlog.get_logger(__name__)

async def minha_funcao(user_id: str):
    # O contexto da requisição (request_id, user_id) já está automaticamente incluído!
    logger.info("Processando usuário", user_id=user_id)

    try:
        resultado = await alguma_operacao()
        logger.debug("Operação concluída", resultado=resultado)
        return resultado
    except Exception as e:
        logger.exception("Falha na operação")  # Inclui stack trace!
        raise
```

Níveis de log:

```python
logger.debug("Só em desenvolvimento")      # Geralmente filtrado em produção
logger.info("Fluxo normal")                 # Operação bem-sucedida
logger.warning("Algo preocupante")          # Token expirando, rate limit próximo
logger.error("Erro recuperável")            # Falha em operação, mas serviço continua
logger.exception("Erro com stack trace")    # Sempre dentro de except blocks
logger.critical("Sistema parando")          # Use com moderação!
```

### 🔍 O que cada middleware faz

1. **request_context_middleware**
   - Gera/captura `request_id`
   - Binda no contexto: `request_id`, `method`, `path`, `client_host`
   - Adiciona header `X-Request-ID` na resposta

2. **auth_middleware**
   - Valida token JWT no header `Authorization`
   - Binda no contexto: `user_id`, `user_roles`, `user_email`
   - Adiciona ao `request.state`

3. **logging_middleware**
   - Mede duração da requisição
   - Binda: `status_code`, `duration_ms`, `success`, `error_type`
   - Log final `"Request completed"` com TODO contexto

### 📊 Formato do log no ELK

```json
{
  "service": "nome-do-seu-servico",
  "request_id": "abc-123",
  "method": "GET",
  "path": "/users/123",
  "user_id": "456",
  "user_roles": ["admin"],
  "status_code": 200,
  "duration_ms": 45.2,
  "success": true,
  "route": "/users/123",
  "event": "Request completed",
  "level": "info",
  "timestamp": "2024-01-01T12:00:00Z",
  "env": "production"
}
```

### 🎯 Boas práticas

**✅ Faça**

- Sempre use `logger = structlog.get_logger(__name__)`
- Adicione contexto relevante nos logs: `user_id`, `order_id`, `transaction_id`
- Use `logger.exception` em `except` blocks
- Mantenha a ordem dos middlewares

**❌ Não faça**

- Não use `print()` para logs
- Não logue dados sensíveis (senhas, tokens, cartão de crédito)
- Não faça `logger.info("mensagem")` sem contexto
- Não binde o mesmo contexto em múltiplos lugares

### 🔧 Troubleshooting

- **Meus logs não estão em JSON?**  
  Verifique se chamou `configure_logging()` antes de criar a app e se o pacote `shared` está instalado corretamente.

- **O campo service está errado?**  
  Verifique o parâmetro em `configure_logging("nome-correto")`.

- **Perdi o request_id em algum log?**  
  A ordem dos middlewares está correta? `request_context` deve ser o PRIMEIRO.

- **Logs duplicados?**  
  Verifique se não está chamando `configure_logging()` mais de uma vez.

### 🧪 Testando localmente

```bash
# Rode seu serviço
uvicorn main:app --reload

# Faça uma requisição
curl -H "Authorization: Bearer SEU_TOKEN" http://localhost:8000/sua-rota

# Veja os logs no console (já em JSON!)
{"service": "seu-servico", "request_id": "...", "event": "Request started", ...}
{"service": "seu-servico", "request_id": "...", "event": "Request completed", ...}
```

### 📈 Visualizando no ELK

No Kibana, você pode:

- Filtrar por `service: "usermanagement"` para ver logs de um serviço
- Buscar por `request_id: "abc-123"` para ver TODA a jornada da requisição
- Criar dashboards de latência por serviço (`duration_ms`)
- Alertas de erro por serviço (`level: "error"`)
