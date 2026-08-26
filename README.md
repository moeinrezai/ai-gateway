# AI Gateway

A secure, scalable, and professional AI Gateway built with FastAPI.

## 🚀 Project Overview
This project acts as a secure intermediary between clients and AI providers (like OpenAI). It handles authentication, authorization, rate limiting, and provider abstraction, ensuring that API keys remain secure on the server side.

## 🏗️ Architecture
- **Backend**: FastAPI (Async)
- **Database**: PostgreSQL (SQLAlchemy 2.x + Alembic)
- **Cache/Rate Limit**: Redis
- **Containerization**: Docker & Docker Compose
- **Package Management**: uv

## 🛠️ Tech Stack
- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 (Async)
- Redis
- Pydantic v2
- Docker

## 📂 Project Structure
app/
├── api/ # Routers, Dependencies, Middleware
├── core/ # Config, Security, Exceptions, Logging
├── models/ # SQLAlchemy Models
├── schemas/ # Pydantic Schemas
├── repositories/ # Database Access Layer
├── services/ # Business Logic Layer
├── ai/ # AI Provider Abstraction
└── main.py # FastAPI Application Entry Point


## 📖 Documentation
Detailed documentation will be added as the project progresses.

## 📜 License
This project is licensed under the MIT License.