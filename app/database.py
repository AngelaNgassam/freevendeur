"""
app/database.py
Gestion centralisée de la connexion à la base de données MySQL.
Les credentials sont chargés depuis les variables d'environnement (jamais en dur).
"""
import os
import logging
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_connection():
    """
    Crée et retourne une connexion MySQL à partir des variables d'environnement.
    Lève une exception si la connexion échoue.
    """
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )