"""
tests/conftest.py
Fixtures partagées entre tous les tests.
Le UserRepository est mocké : aucune base MySQL réelle n'est nécessaire.
"""
import pytest
import bcrypt
from unittest.mock import MagicMock
from app.services.auth_service import AuthenticationService


def hash_password(plain: str) -> str:
    """Hache un mot de passe pour l'utiliser dans les fixtures."""
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@pytest.fixture
def mock_repo():
    """Retourne un UserRepository simulé (MagicMock)."""
    return MagicMock()


@pytest.fixture
def auth_service(mock_repo):
    """Retourne un AuthenticationService injecté avec le mock."""
    return AuthenticationService(user_repository=mock_repo)


@pytest.fixture
def valid_user():
    """Données d'un utilisateur actif non bloqué."""
    return {
        'id': 1,
        'login': 'alice',
        'password_hash': hash_password('MotDePasse123'),
        'is_blocked': False,
        'failed_attempts': 0
    }


@pytest.fixture
def blocked_user():
    """Données d'un utilisateur bloqué."""
    return {
        'id': 2,
        'login': 'bob',
        'password_hash': hash_password('MotDePasse123'),
        'is_blocked': True,
        'failed_attempts': 3
    }


@pytest.fixture
def user_two_failures():
    """Utilisateur avec déjà 2 tentatives échouées (blocage au prochain échec)."""
    return {
        'id': 3,
        'login': 'charlie',
        'password_hash': hash_password('MotDePasse123'),
        'is_blocked': False,
        'failed_attempts': 2
    }