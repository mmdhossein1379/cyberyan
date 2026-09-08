# LinkedIn Profile Search

A full-stack profile search application developed for the Cyberyan full-stack technical assignment.

The system imports LinkedIn profile data, stores profiles in PostgreSQL, creates an Elasticsearch search index, and provides a web interface for searching profiles using keywords, skills, and job titles.

---

# Overview

This project provides:

- Keyword based profile search
- Prefix search
- Fuzzy search
- Skill filtering
- Job title filtering
- Pagination
- Elasticsearch powered searching
- PostgreSQL based data persistence
- Docker Compose deployment
- FastAPI backend
- Next.js frontend

Example searches:

```
py
```

returns profiles containing:

```
python
```

---

```
data
```

can match:

```
data analyst
data scientist
```

---

```
pyhton
```

can still find:

```
python
```

using fuzzy matching.

---

# System Architecture

The application uses PostgreSQL as the main database and Elasticsearch as a dedicated search engine.

```
                    User Browser
                         |
                         |
                         v
                    Next.js
                    Frontend
                         |
                         |
                         v
                    FastAPI
                    Backend
                         |
              ----------------------
              |                    |
              v                    v

        PostgreSQL           Elasticsearch
        Database             Search Index

        profiles             linkedin_profiles
        table                index

        Source of truth      Search engine
```

---

# Data Flow

The dataset is NOT imported directly into Elasticsearch.

The data pipeline is:

```
LinkedIn Dataset
        |
        |
        v
Import / Seed Script
        |
        |
        v
PostgreSQL
(profiles table)
        |
        |
        v
Elasticsearch Index Script
        |
        |
        v
Elasticsearch
(linkedin_profiles index)
        |
        |
        v
Search API
        |
        |
        v
Frontend
```

---

# Storage Responsibilities

| Component | Responsibility |
|---|---|
| PostgreSQL | Permanent profile storage |
| Elasticsearch | Fast searching, filtering and ranking |
| FastAPI | API layer |
| Next.js | User interface |

PostgreSQL is the source of truth.

Elasticsearch contains a searchable copy of the data.

---

# Technology Stack

## Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2 Async
- Alembic
- PostgreSQL
- Elasticsearch 8.15
- Async Elasticsearch Client


## Frontend

- Next.js
- TypeScript


## Infrastructure

- Docker
- Docker Compose

---

# Project Structure

```
linkedin-profile-search/

├── backend/
│
│   ├── alembic/
│   │
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── scripts/
│   │   └── services/
│   │
│   ├── tests/
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── entrypoint.sh
│
├── frontend/
│
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── types/
│   ├── Dockerfile
│   └── package.json
│
├── data/
│   └── 300 user linkedin.txt
│
├── docker-compose.yml
└── README.md
```

---

# Requirements

Before running the project install:

- Docker
- Docker Compose


Check installation:

```bash
docker --version
```

```bash
docker compose version
```

---

# Running the Application

Go to project root:

```bash
cd linkedin-profile-search
```

Start all services:

```bash
docker compose up --build -d
```

The first startup automatically performs:

1. PostgreSQL startup
2. Database migration
3. Dataset import
4. Elasticsearch index creation
5. Profile indexing
6. Backend startup
7. Frontend startup

---

# Running Containers

Check services:

```bash
docker compose ps
```

Expected services:

```
linkedin_db
linkedin_elasticsearch
linkedin_backend
linkedin_frontend
```

---

# Application URLs

## Frontend

```
http://localhost:3000
```


## Backend API

```
http://localhost:8080
```


## Swagger API Documentation

```
http://localhost:8080/docs
```

---

# Ports

## PostgreSQL

Container:

```
5432
```

Host:

```
55432
```


## Backend

Container:

```
8000
```

Host:

```
8080
```


## Frontend

Container:

```
3000
```

Host:

```
3000
```


## Elasticsearch

Container:

```
9200
```

Host:

```
9200
```

---

# Dataset Processing

The input dataset:

```
data/300 user linkedin.txt
```

contains LinkedIn profile records.

During import:

- Data is validated
- Invalid records are ignored
- Duplicate profiles are removed
- Required fields are extracted
- Profiles are stored in PostgreSQL


The supplied dataset produces:

```
279 unique usable profiles
```

---

# Elasticsearch Indexing

After profiles are stored in PostgreSQL, they are indexed into Elasticsearch.

Manual indexing command:

```bash
docker compose exec backend \
python -m app.scripts.index_elasticsearch
```

The indexing process:

1. Reads profiles from PostgreSQL
2. Converts database records into Elasticsearch documents
3. Creates the index:

```
linkedin_profiles
```

4. Inserts documents using bulk indexing

---

# Search Implementation

Elasticsearch is responsible for searching.

The index supports:

- Full text search
- Prefix matching
- Fuzzy matching
- Skill filtering
- Job title filtering


## Keyword Search

Example:

```
GET /api/v1/profiles/search?q=python
```

Searches through:

- name
- job title
- company
- industry
- location
- summary
- skills


Example:

```
q=py
```

matches:

```
python
```

---

## Fuzzy Search

Example:

```
q=pyhton
```

matches:

```
python
```

---

# Filters

## Skill Filter

Example:

```
GET /api/v1/profiles/search?skill=python
```

Partial matching is supported:

```
skill=py
```

can match:

```
python
```

---

## Job Title Filter

Example:

```
GET /api/v1/profiles/search?job_title=data
```

can match:

```
data analyst
data scientist
```

---

# API Documentation


## Search Profiles

Endpoint:

```
GET /api/v1/profiles/search
```


Parameters:

| Parameter | Description |
|---|---|
| q | Keyword search |
| skill | Skill filter |
| job_title | Job title filter |
| page | Page number |
| page_size | Number of results |


Example:

```
GET /api/v1/profiles/search?q=py&skill=python&job_title=data&page=1&page_size=12
```

---

## Filter Options

Endpoint:

```
GET /api/v1/profiles/filters
```

Returns available:

- skills
- job titles


Example response:

```json
{
  "skills": [
    "python",
    "sql"
  ],
  "job_titles": [
    "data analyst"
  ]
}
```

---

# Database Reset

To completely reset the project:

```bash
docker compose down -v
```

Then:

```bash
docker compose up --build
```

This removes:

- PostgreSQL data
- Elasticsearch data
- Docker volumes

and rebuilds everything.

---

# Useful Docker Commands


## Backend logs

```bash
docker compose logs backend
```


## Elasticsearch logs

```bash
docker compose logs elasticsearch
```


## Enter backend container

```bash
docker compose exec backend bash
```


## Check Elasticsearch

```bash
curl http://localhost:9200
```


Check indexed documents:

```bash
curl http://localhost:9200/linkedin_profiles/_count
```

---

# Troubleshooting


## Backend cannot connect to database

Inside Docker Compose use:

```
db
```

as PostgreSQL hostname.

Correct:

```
postgresql+asyncpg://linkedin:linkedin@db:5432/linkedin_search
```

Incorrect:

```
postgresql+asyncpg://linkedin:linkedin@localhost:5432/linkedin_search
```

because `localhost` inside a container points to that container itself.


---

## Elasticsearch is not healthy

Check:

```bash
docker compose ps
```

Expected:

```
linkedin_elasticsearch healthy
```


Test:

```bash
curl http://localhost:9200
```

---

## Code changes are not visible

Rebuild containers:

```bash
docker compose up --build
```

---

# Development Without Docker

## Backend

Create virtual environment:

```bash
cd backend

python -m venv venv
```

Activate:

Linux:

```bash
source venv/bin/activate
```


Install dependencies:

```bash
pip install -r requirements.txt
```


Run:

```bash
uvicorn app.main:app --reload
```


---

## Frontend

Install packages:

```bash
cd frontend

npm install
```


Run:

```bash
npm run dev
```

---

# Future Improvements

Possible improvements:

- Search result highlighting
- Advanced relevance scoring
- Additional filters:
  - location
  - company
  - industry
- Search analytics
- Recommendation system
- Larger Elasticsearch deployment
