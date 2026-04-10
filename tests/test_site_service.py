"""
Testes da camada de Service (Sites)
"""
import pytest
import os
import tempfile
from backend.services.site_service import SiteService


class TestSiteService:
    """Testes para SiteService"""
    
    def test_validate_site_name_valid(self):
        """Teste de validação de nome válido"""
        errors = SiteService.validate_site_name("valid_site-123")
        assert len(errors) == 0
    
    def test_validate_site_name_too_short(self):
        """Teste de validação com nome muito curto"""
        errors = SiteService.validate_site_name("ab")
        assert len(errors) > 0
        assert any("3 caracteres" in error for error in errors)
    
    def test_validate_site_name_invalid_chars(self):
        """Teste de validação com caracteres inválidos"""
        errors = SiteService.validate_site_name("site@invalid!")
        assert len(errors) > 0
        assert any("letras, números" in error for error in errors)
