# Usando Python como base
FROM python:3.11

# Definir diretório de trabalho
WORKDIR /backend

# Copiar os arquivos para dentro do container
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Comando padrão para rodar a aplicação
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
