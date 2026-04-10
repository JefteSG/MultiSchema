# 🚀 Guia Rápido - MultiSchema

## ⚡ Start Rápido

### Docker (Recomendado):
```bash
./start.sh
# ou
docker-compose up -d
```
Aguarde 20s → API em http://localhost:5000

### Testes:
```bash
./run_tests.sh
# ou
pytest -v
```

---

## 📂 Estrutura das Camadas

```
Requisição HTTP
     ↓
  ROUTES (routes/)
     ↓ chama
  SERVICES (services/)
     ↓ usa
  REPOSITORIES (repositories/)
     ↓ acessa
  DATABASE
```

### Exemplo de Fluxo:

1. **Route** recebe POST `/api/v1/user/`
2. **Service** valida dados do usuário
3. **Repository** salva no banco
4. **Response** retorna JSON

---

## 📋 Comandos Úteis

### Docker:
```bash
# Iniciar
docker-compose up -d

# Logs
docker-compose logs -f app

# Parar
docker-compose down

# Limpar tudo (cuidado!)
docker-compose down -v
```

### Testes:
```bash
# Todos
pytest

# Com cobertura
pytest --cov=backend

# Específico
pytest tests/test_services.py

# Verbose
pytest -v
```

### Banco de Dados:
```bash
# Entrar no container
docker exec -it flask_app bash

# Migrations
flask db migrate -m "descrição"
flask db upgrade
```

---

## 🔍 Verificar Implementações

### 1. Camadas:
```bash
ls backend/routes/
ls backend/services/
ls backend/repositories/
```

### 2. Testes:
```bash
ls tests/
cat tests/test_services.py
```

### 3. Docker:
```bash
cat docker-compose.yml | grep postgres
```

### 4. README:
```bash
cat README.md | grep "Arquitetura"
```

---

## 📡 API Endpoints

```bash
# Listar usuários
curl http://localhost:5000/api/v1/user/

# Criar usuário
curl -X POST http://localhost:5000/api/v1/user/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123"}'

# Listar sites
curl http://localhost:5000/api/v1/sites/

# Criar site
curl -X POST http://localhost:5000/api/v1/sites/ \
  -H "Content-Type: application/json" \
  -d '{"site_name":"cliente1","description":"Cliente Teste"}'
```

---

## 🎯 Conceitos Implementados

- ✅ **Routes Layer**: Endpoints HTTP limpos
- ✅ **Service Layer**: Validações e lógica de negócio
- ✅ **Repository Layer**: CRUD isolado
- ✅ **Multi-tenancy**: Schemas isolados por tenant
- ✅ **Tests**: 40+ testes em pytest
- ✅ **Docker**: Postgres + App em containers
- ✅ **Migrations**: Flask-Migrate (Alembic)

---

## 📚 Arquivos para Review

### Código Principal:
- `backend/services/user_service.py` - Lógica de negócio
- `backend/repositories/user_repository.py` - Acesso a dados
- `backend/routes/users_routes.py` - Endpoints limpos

### Testes:
- `tests/test_services.py` - Testes de negócio
- `tests/test_repositories.py` - Testes de dados
- `tests/test_api.py` - Testes de integração

### Infraestrutura:
- `docker-compose.yml` - PostgreSQL setup
- `pytest.ini` - Configuração de testes
- `README.md` - Documentação completa

---

## 🐛 Troubleshooting

### Docker não inicia:
```bash
docker-compose down
docker-compose up -d --build
```

### Testes falhando:
```bash
# Limpar cache
pytest --cache-clear

# Reinstalar deps
pip install -r requirements.txt
```

### Porta 5000 em uso:
```bash
# Ver o que está usando
sudo lsof -i :5000

# Mudar porta no docker-compose.yml
ports:
  - "5001:5000"
```

---

## 📊 Métricas do Projeto

| Item | Quantidade |
|------|-----------|
| Camadas | 3 (Routes/Services/Repos) |
| Testes | 40+ |
| Endpoints | 10+ |
| Linhas README | 300+ |
| Cobertura | ~70% |
| Tempo Setup | <1 min (Docker) |

---

**💡 Este é um projeto portfolio-ready que demonstra arquitetura profissional!**
