# Usando Python Alpine para imagem mais leve e segura
FROM python:3.11-alpine

# Criar usuário não-root para segurança
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Instalar dependências do sistema necessárias
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconfig

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivo de requirements primeiro (para cache de camadas)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários e dar permissões
RUN mkdir -p /app/sites /tmp/flask_instance && \
    chown -R appuser:appgroup /app /tmp/flask_instance

# Trocar para usuário não-root
USER appuser

# Expor porta
EXPOSE 5000

# Variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando para iniciar a aplicação
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
