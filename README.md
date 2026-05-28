# freeVendeur — Guide d'installation et de configuration

> **Documentation technique - Q22 - BC04-EC10**  
> Projet : Module d'authentification freeVendeur  
> Auteur : NGASSAM TCHANA Angela Danielle  
> Date : 28 Mai 2026

---

## Table des matières

1. [Prérequis](#1-prérequis)
2. [Cloner le dépôt](#2-cloner-le-dépôt)
3. [Créer et activer l'environnement virtuel](#3-créer-et-activer-lenvironnement-virtuel)
4. [Installer les dépendances](#4-installer-les-dépendances)
5. [Configurer les variables d'environnement](#5-configurer-les-variables-denvironnement)
6. [Configurer la base de données MySQL](#6-configurer-la-base-de-données-mysql)
7. [Vérifier l'installation](#7-vérifier-linstallation)
8. [Lancer les tests](#8-lancer-les-tests)
9. [Structure du projet](#9-structure-du-projet)
10. [Commandes du quotidien](#10-commandes-du-quotidien)
11. [Résolution des problèmes courants](#11-résolution-des-problèmes-courants)

---

## 1. Prérequis

Avant de commencer, vérifiez que vous disposez des éléments suivants sur votre machine :

| Outil | Version minimale | Vérification |
|-------|-----------------|--------------|
| Python | 3.10+ | `python --version` |
| pip | 22+ | `pip --version` |
| MySQL | 8.0+ | `mysql --version` |
| Git | 2.30+ | `git --version` |
| VS Code (recommandé) | toute version récente | — |

> **Système d'exploitation supporté :** Windows 10/11, Ubuntu 22.04+, macOS 12+

---

## 2. Cloner le dépôt

Ouvrez un terminal et exécutez :

```bash
git clone https://github.com/AngelaNgassam/freevendeur.git
cd freevendeur
```

Si vous n'avez pas encore de dépôt distant, créez simplement le dossier :

```bash
mkdir freevendeur
cd freevendeur
git init
```

---

## 3. Créer et activer l'environnement virtuel

L'environnement virtuel isole les dépendances du projet du reste de votre système.

```bash
# Créer le venv
python -m venv venv
```

**Activer le venv :**

```bash
# Windows (PowerShell)
venv\Scripts\activate

# Windows (CMD)
venv\Scripts\activate.bat

# Linux / macOS
source venv/bin/activate
```

✅ Vous devez voir `(venv)` au début de votre ligne de terminal. C'est obligatoire avant toute commande pip ou pytest.

Pour désactiver le venv à la fin d'une session :

deactivate


---

## 4. Installer les dépendances

Avec le venv activé :

pip install -r requirements.txt


Si le fichier `requirements.txt` n'existe pas encore (première installation) :

pip install mysql-connector-python sqlalchemy python-dotenv bcrypt pytest pytest-cov flake8 black
pip freeze > requirements.txt


**Dépendances principales et leur rôle :**

| Package | Rôle |
|---------|------|
| `mysql-connector-python` | Connexion à MySQL |
| `python-dotenv` | Chargement des variables d'environnement depuis `.env` |
| `bcrypt` | Hachage sécurisé des mots de passe |
| `pytest` | Framework de tests automatisés |
| `pytest-cov` | Rapport de couverture de code |
| `flake8` | Vérification du style PEP8 |
| `black` | Formatage automatique du code |

---

## 5. Configurer les variables d'environnement

Le projet ne stocke jamais de credentials dans le code source. Toutes les informations sensibles passent par un fichier `.env`.

**Étape 1 — Copier le fichier exemple :**


# Linux / macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env


**Étape 2 — Remplir le fichier `.env` :**

Ouvrez `.env` dans VS Code et complétez les valeurs :

```env
DB_HOST=localhost
DB_USER=freevendeur_user
DB_PASSWORD=votre_mot_de_passe_ici
DB_NAME=freevendeur_db


> ⚠️ **Le fichier `.env` ne doit jamais être commité sur Git.** Il est déjà listé dans `.gitignore`. Ne le retirez jamais de cette liste.



## 6. Configurer la base de données MySQL manuellement ou en passant par Wamp

Connectez-vous à MySQL en tant qu'administrateur :


mysql -u root -p


Puis exécutez les commandes suivantes dans le shell MySQL :

sql
-- Créer la base de données
CREATE DATABASE freevendeur_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer un utilisateur dédié (ne jamais utiliser root en production)
CREATE USER 'freevendeur_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_ici';

-- Accorder les droits uniquement sur la base du projet
GRANT ALL PRIVILEGES ON freevendeur_db.* TO 'freevendeur_user'@'localhost';
FLUSH PRIVILEGES;

-- Vérifier
SHOW DATABASES;
EXIT;


**Créer la table utilisateurs :**

```sql
USE freevendeur_db;

CREATE TABLE utilisateurs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    login           VARCHAR(100) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    is_blocked      BOOLEAN NOT NULL DEFAULT FALSE,
    failed_attempts INT NOT NULL DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Vérifier l'installation

Après les étapes 3 à 6, vérifiez que tout est en place :


# 1. Venv actif ?
python --version
# Attendu : Python 3.10.x ou supérieur, avec (venv) visible dans le terminal

# 2. Dépendances installées ?
pip list | grep bcrypt
# Attendu : bcrypt  4.x.x

# 3. Connexion à la base ?
python -c "from app.database import get_connection; c = get_connection(); print('DB OK'); c.close()"
# Attendu : DB OK

# 4. Import du service sans erreur ?
python -c "from app.services.auth_service import AuthenticationService; print('Import OK')"
# Attendu : Import OK


Si toutes les commandes retournent les résultats attendus, l'environnement est correctement configuré.

---

# Résultat attendu :
# tests/test_auth_service.py::TestAuthenticationService::test_tc01_connexion_reussie PASSED
# tests/test_auth_service.py::TestAuthenticationService::test_tc02_echec_mot_de_passe PASSED
# ...
# 8 passed in X.XXs
 
# Rapport de couverture de code
pytest --cov=app --cov-report=term-missing
 
# Rapport HTML (ouvrir htmlcov/index.html dans le navigateur)
pytest --cov=app --cov-report=html
 
# Arrêter au premier test échoué
pytest -x
```
 
> **Taux de couverture cible : 80% minimum** sur le module `app/services/auth_service.py`.
 
---

## 9. Structure du projet

```
freevendeur/
├── app/
│   ├── __init__.py
│   ├── database.py              # Connexion MySQL centralisée
│   ├── repositories/
│   │   └── user_repository.py   # Accès aux données (requêtes paramétrées)
│   ├── services/
│   │   └── auth_service.py      # Logique métier d'authentification
│   ├── models/
│   │   └── user.py              # Modèle utilisateur
│   └── utils/
│       └── validators.py        # Fonctions de validation
├── tests/
│   ├── conftest.py              # Fixtures et mocks partagés
│   └── test_auth_service.py     # 8 cas de test TC-01 à TC-08
├── docs/
│   └── architecture.md          # Documentation d'architecture
├── .env                         # Variables d'environnement (non commité)
├── .env.example                 # Modèle de variables (commité)
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md                    # Ce fichier


---

## 10. Commandes du quotidien

| Action | Commande |
|--------|----------|
| Activer le venv (Windows) | `venv\Scripts\activate` |
| Activer le venv (Linux/Mac) | `source venv/bin/activate` |
| Lancer les tests | `pytest -v` |
| Voir la couverture | `pytest --cov=app --cov-report=term-missing` |
| Formater le code | `black app/ tests/` |
| Vérifier le style PEP8 | `flake8 app/ tests/` |
| Mettre à jour requirements.txt | `pip freeze > requirements.txt` |
| Créer une nouvelle branche | `git checkout -b feature/nom-fonctionnalite` |

---

## 11. Résolution des problèmes courants

**`ModuleNotFoundError: No module named 'app'`**  
→ Vérifiez que vous êtes bien à la racine du projet (`cd freevendeur`) et que le venv est activé.

**`mysql.connector.errors.ProgrammingError: Access denied`**  
→ Vérifiez les valeurs dans `.env`. L'utilisateur MySQL doit correspondre exactement à celui créé à l'étape 6.

**`bcrypt` introuvable**  
→ Réinstallez avec `pip install bcrypt` (venv activé).

**Les tests échouent avec `ImportError`**  
→ Exécutez `pip install -r requirements.txt` depuis la racine du projet, venv activé.

**`(venv)` n'apparaît pas dans le terminal VS Code**  
→ `Ctrl+Shift+P` → `Python: Select Interpreter` → choisir `./venv/bin/python` (Linux/Mac) ou `./venv/Scripts/python.exe` (Windows).