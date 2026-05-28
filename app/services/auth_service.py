"""
app/services/auth_service.py
Logique métier d'authentification — séparée de l'accès aux données (SRP).
Ce fichier ne connaît pas MySQL : il dialogue uniquement avec UserRepository.
"""
import bcrypt
import logging
from app.repositories.user_repository import UserRepository, MAX_FAILED_ATTEMPTS

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Gère la logique d'authentification des utilisateurs de freeVendeur.
    Règles métier :
      - login et mot de passe obligatoires
      - sensibles à la casse
      - blocage automatique après 3 tentatives échouées
      - un compte bloqué ne peut plus se connecter
    """

    def __init__(self, user_repository: UserRepository = None):
        """
        Injection de dépendance : permet de passer un mock en tests (testabilité).
        Si aucun repository n'est fourni, utilise le vrai.
        """
        self.user_repository = user_repository or UserRepository()

    def login(self, login: str, password: str) -> dict:
        """
        Tente d'authentifier un utilisateur.

        Args:
            login: identifiant saisi par l'utilisateur
            password: mot de passe en clair saisi par l'utilisateur

        Returns:
            dict avec 'success' (bool) et 'message' (str)
        """
        # Règle 1 : champs obligatoires
        if not login or not password:
            return {'success': False, 'message': 'Login et mot de passe obligatoires.'}

        user = self.user_repository.find_user_by_login(login)

        # Règle 2 : utilisateur inexistant
        if user is None:
            logger.info("Tentative de connexion avec un login inexistant : %s", login)
            return {'success': False, 'message': 'Identifiants incorrects.'}

        # Règle 3 : compte bloqué
        if user['is_blocked']:
            logger.warning("Tentative de connexion sur compte bloqué : %s", login)
            return {'success': False, 'message': 'Compte bloqué. Contactez un administrateur.'}

        # Règle 4 : vérification du mot de passe avec bcrypt (sensible à la casse)
        password_correct = bcrypt.checkpw(
            password.encode('utf-8'),
            user['password_hash'].encode('utf-8')
        )

        if not password_correct:
            self._handle_failed_attempt(login, user)
            return {'success': False, 'message': 'Identifiants incorrects.'}

        # Connexion réussie : réinitialiser le compteur
        self.user_repository.reset_failed_attempts(login)
        logger.info("Connexion réussie : %s", login)
        return {'success': True, 'message': 'Connexion réussie.'}

    def _handle_failed_attempt(self, login: str, user: dict) -> None:
        """
        Gère une tentative échouée : incrémente le compteur et bloque si nécessaire.
        Méthode privée (SRP : logique de blocage isolée).
        """
        self.user_repository.increment_failed_attempts(login)
        new_count = user['failed_attempts'] + 1

        if new_count >= MAX_FAILED_ATTEMPTS:
            self.user_repository.block_user(login)
            logger.warning("Compte bloqué : %s (%d tentatives)", login, new_count)