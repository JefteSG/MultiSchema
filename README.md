# MultiSchema

Sistema de gerenciamento multi-tenant que permite criar e gerenciar múltiplos sites com bancos de dados isolados, cada um com seu próprio esquema e configuração.

## 🚀 Funcionalidades

- **Multi-tenancy**: Cada site possui seu próprio banco de dados SQLite isolado
- **Gerenciamento de Usuários**: CRUD completo para usuários com sistema de roles
- **Configuração Nginx**: Geração automática de configuração Nginx para múltiplos sites
- **Docker Support**: Containerização completa com Docker Compose
- **API RESTful**: Endpoints bem estruturados para todas as operações
- **Host Management**: Adição automática de hosts locais para desenvolvimento

## 📁 Estrutura do Projeto

```
MultiSchema/
├── backend/
│   ├── app.py              # Aplicação principal Flask
│   ├── config.py           # Configurações da aplicação
│   ├── Dockerfile          # Container da aplicação
│   ├── controllers/        # Controladores (auth, links, configs)
│   ├── models/             # Modelos de dados (User, Role)
│   ├── routes/             # Rotas da API (users, sites, redirect)
│   ├── sites/              # Configurações e dados dos sites
│   ├── templates/          # Templates (nginx)
│   └── utils/              # Utilitários (site management)
├── docker-compose.yml      # Orquestração dos containers
├── requirements.txt        # Dependências Python
├── vercel.json            # Configuração para deploy na Vercel
└── README.md              # Este arquivo
```

## 🛠️ Instalação

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (opcional)
- MySQL/MariaDB (para produção)

### Instalação Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/JefteSG/MultiSchema.git
   cd MultiSchema
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o ambiente**
   ```bash
   cd backend
   flask init
   ```
   Será solicitado usuário e senha do banco principal.

4. **Execute a aplicação**
   ```bash
   flask run
   ```

### Instalação com Docker

1. **Clone e execute**
   ```bash
   git clone https://github.com/JefteSG/MultiSchema.git
   cd MultiSchema
   docker-compose up -d
   ```

2. **Configure o banco (dentro do container)**
   ```bash
   docker exec -it flask_app flask init
   ```

## 🔧 Configuração

### Configuração do Banco de Dados

O sistema suporta dois modos de configuração:

1. **SQLite (padrão)**: Para desenvolvimento
2. **MySQL/MariaDB**: Para produção

A configuração é feita através do comando `flask init` que cria o arquivo `sites/config.json`.

### Variáveis de Ambiente

```bash
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://user:password@host/database
```

## 📡 API Endpoints

### Usuários
- `GET /api/v1/user/` - Lista todos os usuários
- `GET /api/v1/user/<id>` - Obtém usuário específico
- `POST /api/v1/user/` - Cria novo usuário
- `PUT /api/v1/user/<id>` - Atualiza usuário
- `DELETE /api/v1/user/<id>` - Remove usuário

### Sites
- `POST /create-site/<site_name>` - Cria novo site com banco isolado

### Exemplo de Uso da API

```bash
# Criar usuário
curl -X POST http://localhost:5000/api/v1/user/ \
  -H "Content-Type: application/json" \
  -d '{"username": "joao", "email": "joao@email.com", "password": "senha123"}'

# Criar novo site
curl -X POST http://localhost:5000/create-site/meusite
```

## 🏗️ Comandos CLI

```bash
# Inicializar configuração do banco
flask init

# Gerar configuração Nginx
flask setup-nginx

# Adicionar host local
sudo flask add-host meusite.local

# Migrar banco de dados
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🔒 Segurança

- Senhas são armazenadas com hash usando Werkzeug
- Isolamento completo entre sites via bancos separados
- Validação de entrada em todos os endpoints
- Tratamento adequado de erros

## 🌐 Multi-tenancy

Cada site criado possui:
- Banco de dados SQLite próprio
- Configuração independente em JSON
- Estrutura de pastas isolada
- Configuração Nginx automática

## 🚀 Deploy

### Vercel
```bash
vercel --prod
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚠️ Status do Projeto

Este projeto está em desenvolvimento ativo. Algumas funcionalidades podem estar incompletas ou em processo de refatoração.

### TODO
- [ ] Implementar autenticação JWT
- [ ] Adicionar testes unitários
- [ ] Melhorar documentação da API
- [ ] Implementar logging estruturado
- [ ] Adicionar métricas e monitoramento

## 📞 Suporte

Para dúvidas ou suporte, abra uma issue no GitHub ou entre em contato através do email do desenvolvedor.

---

Desenvolvido por JefteSG