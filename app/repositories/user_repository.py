"""
app/repositories/user_repository.py
Gère uniquement l'accès aux données utilisateur en base de données.
Responsabilité Unique : ce fichier ne fait que lire/écrire en base.
"""
import logging
import mysql.connector
from app.database import get_connection

logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 3


class UserRepository:
    """
    Accès aux données des utilisateurs.
    Toutes les requêtes sont paramétrées pour prévenir les injections SQL (OWASP A03).
    """

    def find_user_by_login(self, login: str) -> dict | None:
        """
        Recherche un utilisateur par son identifiant.
        Retourne un dictionnaire avec les données ou None si inexistant.
        """
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            # Requête paramétrée : jamais de concaténation de chaînes
            cursor.execute(
                "SELECT id, login, password_hash, is_blocked, failed_attempts "
                "FROM utilisateurs WHERE login = %s",
                (login,)
            )
            return cursor.fetchone()
        except mysql.connector.Error as error:
            logger.error("Erreur DB find_user_by_login : %s", error)
            return None
        finally:
            # Toujours fermer la connexion, succès ou erreur (DRY, anti-fuite)
            if connection and connection.is_connected():
                connection.close()

    def increment_failed_attempts(self, login: str) -> None:
        """Incrémente le compteur de tentatives échouées pour un utilisateur."""
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE utilisateurs SET failed_attempts = failed_attempts + 1 "
                "WHERE login = %s",
                (login,)
            )
            connection.commit()
        except mysql.connector.Error as error:
            logger.error("Erreur DB increment_failed_attempts : %s", error)
        finally:
            if connection and connection.is_connected():
                connection.close()

    def block_user(self, login: str) -> None:
        """Bloque un utilisateur après trop de tentatives échouées."""
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE utilisateurs SET is_blocked = TRUE WHERE login = %s",
                (login,)
            )
            connection.commit()
            logger.warning("Compte bloqué après %d tentatives : %s", MAX_FAILED_ATTEMPTS, login)
        except mysql.connector.Error as error:
            logger.error("Erreur DB block_user : %s", error)
        finally:
            if connection and connection.is_connected():
                connection.close()

    def reset_failed_attempts(self, login: str) -> None:
        """Réinitialise le compteur de tentatives après une connexion réussie."""
        connection = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE utilisateurs SET failed_attempts = 0 WHERE login = %s",
                (login,)
            )
            connection.commit()
        except mysql.connector.Error as error:
            logger.error("Erreur DB reset_failed_attempts : %s", error)
        finally:
            if connection and connection.is_connected():
                connection.close()