#!/bin/bash
# Script para iniciar o MultiSchema com Docker

echo "🐳 Iniciando MultiSchema com Docker Compose..."
echo ""

# Para containers anteriores se existirem
echo "🛑 Parando containers existentes..."
docker-compose down

# Remove volumes antigos (opcional - descomente se quiser limpar dados)
# docker-compose down -v

echo ""
echo "🚀 Subindo containers (Postgres + App)..."
docker-compose up -d

echo ""
echo "⏳ Aguardando inicialização completa (~20 segundos)..."
sleep 5

# Monitora logs do app
echo ""
echo "📋 Monitorando logs da aplicação..."
echo "   (Ctrl+C para sair do log - containers continuarão rodando)"
echo ""
docker-compose logs -f app

echo ""
echo "✅ Para verificar status:"
echo "   docker-compose ps"
echo ""
echo "✅ Para parar:"
echo "   docker-compose down"
echo ""
echo "✅ API disponível em:"
echo "   http://localhost:5000/api/v1/user/"
