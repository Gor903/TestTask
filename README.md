# TestTask

This is a sample project showcasing how to set up a FastAPI application with Docker. It includes a FastAPI backend and demonstrates how to containerize it for easy deployment and scalability.

## Features

- FastAPI backend setup
- Docker containerization
- Easy to use with `docker compose`
- Configurable environment variables


## Setup

### 1. Clone the Repository

```bash
    git clone https://github.com/Gor903/TestTask.git
    cd TestTask
    cp .env.example .env
```

### 2. Run the project
```bash
    docker compose up --build
```

### 3. Also run migrations
```bash
    alembic upgrade head
```

### You can access swagger folowing
**swagger** - http://0.0.0.0:8000/docs


## Tests

### 1. Run the project

### 2. Run tests
```bash
    pytest
```
