
# Access Control Log API

A simple Django-based REST API that logs door access control events and tracks system activities in real-time.

## Features

- Complete CRUD Operations (Create, Read, Update, Delete)
- Automatic Logging via Django Signals
- System Event Tracking to Log Files
- Advanced Filtering and Search Capabilities
- Statistics and Analytics Endpoints
- Comprehensive Unit Test Coverage
- Docker Support with Docker Compose
- Git Version Control with Branching Strategy

## Technology Stack

- **Python** 3.11
- **Django** 4.2.0
- **Django REST Framework** 3.14.0
- **SQLite3** (Development)
- **PostgreSQL** (Production - Optional)
- **Docker & Docker Compose**
- **Gunicorn** (Production Server)


## API Endpoints

### Core CRUD
```
POST /api/logs/ - Create log (201)
GET /api/logs/ - List logs (200)
GET /api/logs/<id>/ - Get log (200)
PUT /api/logs/<id>/ - Update log (200)
DELETE /api/logs/<id>/ - Delete log (204)
```
### Special Endpoints
```
GET /api/logs/stats/ - Get statistics
GET /api/logs/denied_access/ - Get denied logs
GET /api/logs/by_card/?card_id=C1001 - Filter by card
GET /api/logs/by_door/?door_name=Main%20Entrance - Filter by door
```
### Filtering
```
GET /api/logs/?card_id=C1001 - By card ID
GET /api/logs/?access_granted=true - By status
GET /api/logs/?search=C1001 - Search
```
###  Search

```bash
GET /api/logs/?card_id=C1001   # Filter by card ID
GET /api/logs/?door_name=Main%20Entrance   # Filter by door name
GET /api/logs/?access_granted=true   # Filter by access status
GET /api/logs/?access_granted=false

GET /api/logs/?search=C1001    # Search functionality
GET /api/logs/?page=2    # Pagination
```


## Project Structure

```
access_control_project/
├── access_control/
│   ├── migrations/
│   ├── models.py           # AccessLog Model
│   ├── serializers.py      # DRF Serializers
│   ├── views.py            # ViewSets and Views
│   ├── urls.py             # App URL Routes
│   ├── signals.py          # Django Signal Handlers
│   ├── apps.py             # App Configuration
│   ├── tests.py            # Unit Tests
│   └── admin.py            # Admin Panel Configuration
├── access_control_api/
│   ├── settings.py         # Django Settings
│   ├── urls.py             # Project URL Configuration
│   ├── asgi.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
├── .gitignore
├── README.md
└── system_events.log       # System Event Log File
```

The application will be available at `http://localhost:8000`



## Installation & Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual Environment
- Docker & Docker Compose

### Local Setup (Without Docker)

```bash
cd access_control_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create superuser (Optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Docker Setup

```bash
# Build and start containers
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (Optional)
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web

# Stop containers
docker-compose down
```

## Request/Response Examples

### Create New Log (POST)

**Request:**
```bash
curl -X POST http://localhost:8000/api/logs/ \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "C1001",
    "door_name": "Main Entrance",
    "access_granted": true
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "card_id": "C1001",
  "door_name": "Main Entrance",
  "access_granted": true,
  "timestamp": "2025-01-06T10:35:15.123456Z",
  "created_at": "2025-01-06T10:35:15.123456Z"
}
```

### List All Logs (GET)

**Request:**
```bash
curl http://localhost:8000/api/logs/
```

**Response (200 OK):**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/logs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "card_id": "C1001",
      "door_name": "Main Entrance",
      "access_granted": true,
      "timestamp": "2025-01-06T10:35:15.123456Z",
      "created_at": "2025-01-06T10:35:15.123456Z"
    },
    ...
  ]
}
```

### Get Statistics (GET)

**Request:**
```bash
curl http://localhost:8000/api/logs/stats/
```

**Response (200 OK):**
```json
{
  "total_logs": 10,
  "granted_access": 8,
  "denied_access": 2,
  "unique_cards": 3,
  "unique_doors": 2
}
```

## System Event Logging

All CREATE and DELETE operations are automatically logged to `system_events.log`:

```bash
# View log file
cat system_events.log
```

## Running Tests

```bash
# Run all tests
python manage.py test
# Run specific test class
python manage.py test access_control.tests.AccessLogAPITest
# Run with verbose output
python manage.py test --verbosity=2
# Run with coverage report
coverage run --source='.' manage.py test
coverage report
```

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

Features:
- View all access logs in a user-friendly interface
- Add, edit, and delete logs
- Search by card ID or door name
- Filter by access status and door
- Bulk actions (mark as GRANTED/DENIED)


### Environment Variables

Create a `.env` file in the project root:

```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Settings Update

Update `access_control_api/settings.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
```

## Production Deployment

### Using PostgreSQL


### Using Docker Compose

```bash
# Build and run with PostgreSQL
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Using Gunicorn

```bash
pip install gunicorn

gunicorn --bind 0.0.0.0:8000 --workers 4 access_control_api.wsgi:application
```

## Git Workflow

### Initial Setup

```bash
# Initialize repository
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create development branch
git checkout -b development

# Make commits
git add .
git commit -m "Initial setup"

# Merge to main when complete
git checkout main
git merge development
```

### Commit Guidelines



### Common Issues

#### Port Already in Use
```bash
python manage.py runserver 8001
```

#### Database Migration Issues
```bash
python manage.py migrate access_control zero
python manage.py migrate
```

#### Module Import Errors
```bash
pip install -r requirements.txt
```

#### Cache Issues
```bash
python manage.py clear_cache
```

## API Testing with Postman

### Setup

1. Download Postman from https://www.postman.com/downloads/
2. Import the API collection or manually create requests

### Basic Request

**POST /api/logs/**
```json
{
  "card_id": "C1001",
  "door_name": "Main Entrance",
  "access_granted": true
}
```

**Headers:**
```
Content-Type: application/json
```

### Pagination

Default page size: 10 items per page

```bash
GET /api/logs/?page=1
GET /api/logs/?page=2
```

### Version 1.0.0
- Initial release
- Complete CRUD operations
- Django Signals for event logging
- REST API with filtering and search
- Unit test coverage
- Docker support

---

**Last Updated:** January 2026
**Status:** Active Development  
**Maintainer:** Mahamudul Hasan