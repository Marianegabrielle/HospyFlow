# HospyFlow Backend - ClinicFlow Analytics

Système d'analyse des flux hospitaliers avec Django et PostgreSQL.

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose
- Python 3.11+ (pour développement local)

### Lancer avec Docker

```bash
# Démarrer les services
docker-compose up -d

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Charger les données initiales
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

### Accès
- **API**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin/
- **Documentation Swagger**: http://localhost:8000/api/docs/
- **Documentation ReDoc**: http://localhost:8000/api/redoc/

## 📁 Structure du Projet

```
Hospyflow_backend/
├── config/                 # Configuration Django
├── apps/
│   ├── accounts/          # Gestion utilisateurs et authentification
│   ├── workflows/         # Workflows hospitaliers
│   ├── events/            # Micro-événements
│   ├── analytics/         # Analyses et tableaux de bord
│   └── alerts/            # Système d'alertes
└── fixtures/              # Données initiales
```

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens).

```bash
# Obtenir un token
POST /api/auth/login/
{
    "email": "user@example.com",
    "password": "password"
}

# Utiliser le token
Authorization: Bearer <access_token>
```

## 📚 Endpoints API

### Authentification
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/auth/register/` | POST | Inscription |
| `/api/auth/login/` | POST | Connexion |
| `/api/auth/refresh/` | POST | Rafraîchir token |
| `/api/auth/me/` | GET/PUT | Profil utilisateur |

### Workflows
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/workflows/types/` | GET | Types de workflows |
| `/api/workflows/demarrer/` | POST | Démarrer un workflow |
| `/api/workflows/instances/` | GET | Instances en cours |
| `/api/workflows/instances/<id>/avancer/` | POST | Avancer à l'étape suivante |

### Événements
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/events/` | GET | Liste des événements |
| `/api/events/signaler/` | POST | Signaler un événement |
| `/api/events/<id>/resoudre/` | POST | Résoudre un événement |
| `/api/events/critiques/` | GET | Événements critiques |

### Analytics
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/analytics/tableau-de-bord/` | GET | Tableau de bord |
| `/api/analytics/goulots/` | GET | Goulots d'étranglement |
| `/api/analytics/metriques/` | GET | Métriques par département |

### Alertes
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/alerts/` | GET | Liste des alertes |
| `/api/alerts/mes-alertes/` | GET | Mes alertes non lues |
| `/api/alerts/<id>/acquitter/` | POST | Acquitter une alerte |

## 👥 Rôles Utilisateurs

| Rôle | Description |
|------|-------------|
| `NURSE` | Infirmier(ère) |
| `DOCTOR` | Médecin |
| `LAB_TECH` | Technicien de laboratoire |
| `ADMIN` | Administrateur |

## 🏗️ Architecture

Le projet utilise une **architecture en couches** :

- **Models** - Couche de données
- **Repositories** - Accès aux données (Pattern Repository)
- **Services** - Logique métier (Patterns Service, Facade, Strategy)
- **Serializers** - Transformation des données
- **Views** - Contrôleurs API

### Design Patterns Utilisés

- **Repository Pattern** - Abstraction de l'accès aux données
- **Service Pattern** - Encapsulation de la logique métier
- **Facade Pattern** - Interface simplifiée pour opérations complexes
- **Strategy Pattern** - Traitement différencié selon sévérité/priorité
- **Singleton Pattern** - Instance unique du moteur d'analyse
- **Observer Pattern** - Notifications aux abonnés

## 🧪 Tests

```bash
docker-compose exec web python manage.py test
```

## 📄 Licence

Propriétaire - Projet académique
