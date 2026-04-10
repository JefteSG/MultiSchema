#!/bin/bash
# Script para executar testes do MultiSchema

echo "🧪 Executando testes do MultiSchema..."
echo ""

# Verifica se pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest não encontrado. Instalando..."
    pip install pytest pytest-cov
fi

# Executa os testes
echo "▶️  Executando suite completa de testes..."
pytest -v --tb=short

# Mostra resumo
echo ""
echo "✅ Testes concluídos!"
echo ""
echo "Para rodar testes específicos:"
echo "  pytest tests/test_repositories.py  # Testes de Repository"
echo "  pytest tests/test_services.py      # Testes de Service"
echo "  pytest tests/test_api.py           # Testes de API"
echo ""
echo "Para cobertura de código:"
echo "  pytest --cov=backend --cov-report=html"
