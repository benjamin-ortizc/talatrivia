# TalaTrivia

API REST para gestionar trivias de RRHH. Permite a administradores crear preguntas y trivias, asignar participantes y consultar rankings. Los usuarios pueden jugar en las trivias asignadas y ver sus resultados.

Proyecto de prueba técnica para el puesto SSR Software Engineer en Talana.

[PDF de requerimiento](./docs/talatrivia.pdf)

## Documentación de diseño

Antes de implementar una solución, se diseñó el modelo de datos y el contrato del API. Ambos documentos viven en [`docs/`](docs/) y guían toda la implementación:

- **[`docs/database.md`](docs/database.md)** — modelo de datos: tablas, constraints, relaciones y decisiones de modelado. Diagrama ER en [`docs/database_schema.png`](docs/database_schema.png).
- **[`docs/api-endpoints.md`](docs/api-endpoints.md)** — contrato del API: endpoints agrupados por dominio, roles requeridos y decisiones de diseño (sistema de puntajes, manejo de roles, etc.).

## Setup

Requisitos: Docker y Docker Compose.

```bash
git clone https://github.com/benjamin-ortizc/talatrivia/
cd talatrivia
cp .env.example .env
docker compose up -d --build     # levanta db + server web en background
docker compose exec web alembic upgrade head    # corre migraciones
docker compose exec web python scripts/create_admin.py    # crea admin de prueba
```

La API queda en `http://localhost:8000`. Swagger interactivo en `http://localhost:8000/docs`.

## Próximos pasos

Cosas que no se implementaron por tiempo:

- Endpoints `PATCH` / `DELETE` para preguntas y trivias (actualmente solo crear/leer).
- Paginación en listas (`GET /trivias`, `GET /questions`).
- Refresh tokens en auth.
- Modificar `POST /trivias/{id}/submit` para soportar envios parciales y guardar progreso de la trivia.