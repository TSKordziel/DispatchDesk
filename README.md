# DispatchDesk

DispatchDesk is a lightweight ticketing and issue-tracking API for small teams that want structure without enterprise bloat.
This repository contains the backend service only.

## Project Goals

- Provide a clean, well-structured API for tickets, status transitions, assignments, comments, and tags.
- Emphasize correctness, clarity, and maintainability over feature sprawl.
- Serve as a real-world backend systems project, not a toy demo.

## Tech Stack

- Backend: FastAPI (Python)
- Database: PostgreSQL
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Authentication: OAuth2 password flow with JWT access and refresh tokens
- Testing: Pytest + httpx
- Deployment: Dockerized service on Render with managed Postgres

## Architecture

- Request flow: FastAPI routes -> service layer -> CRUD layer -> SQLAlchemy models -> Postgres.
- Migrations are managed with Alembic and run on startup in production.
- Centralized error envelope with request IDs plus request logging middleware.

## Auth and Permissions

- Login issues access and refresh JWTs; access tokens secure API calls.
- Roles: requester, agent, admin.
- Requesters can create, view, and comment on their own tickets only.
- Agents and admins can view all tickets, assign tickets, and transition status.
- Admin role changes are restricted to admin-only paths; the API blocks promotion to admin.

## API Surface

- GET /
- GET /health
- POST /auth/register
- POST /auth/login
- GET /auth/me
- POST /tickets
- GET /tickets
- GET /tickets/{id}
- POST /tickets/{id}/assign
- POST /tickets/{id}/transition
- PATCH /tickets/{id}/priority
- POST /tickets/{id}/comments
- GET /tickets/{id}/comments
- POST /tags
- POST /tickets/{id}/tags/{tag_id}
- DELETE /tickets/{id}/tags/{tag_id}

Ticket listing filters and search:

- limit, offset
- status, priority, assigned_to
- tag
- q (title/description search)

## API Examples

Register a user:

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123456"
}
```

```http
201 Created

{
  "id": "0f2a4f2e-4a6b-4c38-9f47-1dd6a7b3c0c4",
  "email": "user@example.com",
  "role": "requester",
  "is_active": true
}
```

Create a ticket:

```http
POST /tickets
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Printer issue in lobby",
  "description": "Paper jam on floor 1"
}
```

```http
201 Created

{
  "id": "2c2d0ee3-2b7d-4c6a-9a01-5f0a93c4a1c9",
  "title": "Printer issue in lobby",
  "description": "Paper jam on floor 1",
  "status": "new",
  "priority": "med",
  "created_by_id": "0f2a4f2e-4a6b-4c38-9f47-1dd6a7b3c0c4",
  "assigned_to_id": null,
  "created_at": "2026-03-28T18:22:10Z",
  "updated_at": "2026-03-28T18:22:10Z",
  "closed_at": null
}
```

List tickets with filters and search:

```http
GET /tickets?status=triaged&priority=high&tag=ops&q=printer&limit=20&offset=0
Authorization: Bearer <access_token>
```

```http
200 OK

[
  {
    "id": "2c2d0ee3-2b7d-4c6a-9a01-5f0a93c4a1c9",
    "title": "Printer issue in lobby",
    "status": "triaged",
    "priority": "high"
  }
]
```

## Deployment

DispatchDesk is deployed as a Dockerized FastAPI service on Render.
It runs against a managed PostgreSQL database and applies Alembic migrations on startup.

Deployment story (late January 2026 to early February 2026): My initial deployment went live before I had an admin bootstrap path. Because I only had requester users, there was no way to transition ticket status. The diagnosis was immediate once I realized the permission model was working and there was simply no admin account. The fix was a manual SQL update in the managed database to promote a user to admin. The lesson was to plan a secure initial admin bootstrap before the first deployment.

Deployment lessons:

- Migrations must run on startup to keep schema in sync.
- Normalize DATABASE_URL to the SQLAlchemy driver format in production.
- Keep configuration environment-driven (DATABASE_URL, JWT_SECRET_KEY, PORT, BOOTSTRAP_ADMIN_*).

## Local Development

Run the API and database locally with Docker:

1. Build and start services.
2. Open the API at http://localhost:8000/docs.

```bash
docker compose up --build
```

Environment variables used by the API:

- DATABASE_URL
- JWT_SECRET_KEY
- PORT
- BOOTSTRAP_ADMIN_EMAIL
- BOOTSTRAP_ADMIN_PASSWORD

## Testing

- Auth tests covering register, login, and /me.
- Permission tests for requester vs agent access.
- Comment and tag tests including idempotency.
- Integration flow test covering ticket creation, assignment, transition, comments, and tags.

Run tests with a Postgres database available and TEST_DATABASE_URL set:

```bash
TEST_DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dispatchdesk_test pytest
```

## What I'd Do Next

- Add refresh token rotation and a refresh endpoint.
- Introduce an audit log for ticket actions and role changes.
- Add rate limiting and request-level metrics.
- Return pagination metadata for list endpoints.
- Expand integration tests for edge cases and failure modes.

## Non-Goals (For Now)

- Front-end UI
- Multi-tenant enterprise features
- Real-time notifications
- Integrations with external ticketing platforms
