"""
tests/test_auth_service.py
Tests automatisés pour AuthenticationService — Q16 de l'épreuve.
Structure Arrange / Act / Assert pour chaque test.
Lance avec : pytest -v
"""
import pytest
from app.services.auth_service import AuthenticationService


class TestAuthenticationService:
    """Tests unitaires de la logique d'authentification freeVendeur."""

    # TC-01 — Connexion réussie avec identifiants valides
    def test_tc01_connexion_reussie(self, auth_service, mock_repo, valid_user):
        # Arrange : le repository retourne un utilisateur existant et actif
        mock_repo.find_user_by_login.return_value = valid_user

        # Act : tentative de connexion avec les bons identifiants
        result = auth_service.login('alice', 'MotDePasse123')

        # Assert : connexion accordée, compteur réinitialisé
        assert result['success'] is True
        assert 'réussie' in result['message']
        mock_repo.reset_failed_attempts.assert_called_once_with('alice')

    # TC-02 — Échec avec mot de passe incorrect
    def test_tc02_echec_mot_de_passe(self, auth_service, mock_repo, valid_user):
        # Arrange
        mock_repo.find_user_by_login.return_value = valid_user

        # Act
        result = auth_service.login('alice', 'MauvaisMotDePasse')

        # Assert : connexion refusée, tentative enregistrée
        assert result['success'] is False
        mock_repo.increment_failed_attempts.assert_called_once_with('alice')

    # TC-03 — Échec avec login inexistant
    def test_tc03_echec_login_inexistant(self, auth_service, mock_repo):
        # Arrange : le repository ne trouve personne
        mock_repo.find_user_by_login.return_value = None

        # Act
        result = auth_service.login('utilisateur_inconnu', 'MotDePasse123')

        # Assert
        assert result['success'] is False
        assert 'Identifiants incorrects' in result['message']

    # TC-04 — Blocage automatique après 3 tentatives échouées
    def test_tc04_blocage_apres_trois(self, auth_service, mock_repo, user_two_failures):
        # Arrange : l'utilisateur en est à sa 3e tentative (failed_attempts = 2)
        mock_repo.find_user_by_login.return_value = user_two_failures

        # Act : mauvais mot de passe → doit déclencher le blocage
        result = auth_service.login('charlie', 'MauvaisMotDePasse')

        # Assert : compte bloqué après cette tentative
        assert result['success'] is False
        mock_repo.block_user.assert_called_once_with('charlie')

    # TC-05 — Compte bloqué refuse même les bons identifiants
    def test_tc05_compte_bloque_refuse(self, auth_service, mock_repo, blocked_user):
        # Arrange : l'utilisateur est bloqué
        mock_repo.find_user_by_login.return_value = blocked_user

        # Act : même avec le bon mot de passe
        result = auth_service.login('bob', 'MotDePasse123')

        # Assert : refus systématique
        assert result['success'] is False
        assert 'bloqué' in result['message']
        mock_repo.increment_failed_attempts.assert_not_called()

    # TC-06 — Login vide interdit
    def test_tc06_login_vide(self, auth_service, mock_repo):
        # Arrange / Act
        result = auth_service.login('', 'MotDePasse123')

        # Assert : refus sans même interroger la base
        assert result['success'] is False
        mock_repo.find_user_by_login.assert_not_called()

    # TC-07 — Mot de passe vide interdit
    def test_tc07_mot_de_passe_vide(self, auth_service, mock_repo):
        # Arrange / Act
        result = auth_service.login('alice', '')

        # Assert
        assert result['success'] is False
        mock_repo.find_user_by_login.assert_not_called()

    # TC-08 — Sensibilité à la casse du mot de passe
    def test_tc08_sensible_a_la_casse(self, auth_service, mock_repo, valid_user):
        # Arrange : mot de passe correct est 'MotDePasse123'
        mock_repo.find_user_by_login.return_value = valid_user

        # Act : version en minuscules → doit échouer
        result = auth_service.login('alice', 'motdepasse123')

        # Assert : refusé car la casse ne correspond pas
        assert result['success'] is False