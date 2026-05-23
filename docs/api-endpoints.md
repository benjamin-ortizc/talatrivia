# Endpoints de TalaTrivia

Documento de overview de los endpoints del API, agrupados por dominio funcional.
Para detalles técnicos de cada endpoint (request/response), la API expone Swagger UI 
en `/docs`.

### Características del API
- Todos los endpoints devuelven JSON
- Códigos HTTP siguiendo principios RESTful
- Autenticación vía bearer JWT token en header `Authorization: Bearer <token>`
- Validación de inputs utilizando Pydantic Schemas

### Sistema de puntajes

Las preguntas otorgan puntos según su dificultad. Los labels que persisten en la DB son:
- `easy` - 1 punto
- `medium` - 2 puntos
- `hard` - 3 puntos

### Roles del sistema
- **Admin**: gestiona preguntas y trivias
- **Player**: participa en trivias asignadas

> Se decide dejar el campo 'role' como un string, ya que el caso de uso no amerita crear una tabla "Roles" que se interseccione con "UserRoles", ya que solamente necesitamos dos roles, los cuales son validados mediante un enum a nivel de aplicación.

### Rate limiting

Aplicado en los endpoints de auth con `slowapi`, por IP:
- `POST /auth/register` - 3 requests por minuto, para prevenir spam de cuentas.
- `POST /auth/login` - 5 requests por minuto, para prevenir brute force.

---

# Endpoints públicos

Endpoints que no requieren autenticación.

## Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/auth/register` | Registra un nuevo usuario con rol `player`. Email único requerido. |
| `POST` | `/auth/login` | Autentica usuario y devuelve JWT access token. |

## Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Health check del servicio. Devuelve estado operacional. |

---

# Endpoints con autenticación

Endpoints que requieren un JWT válido. Disponibles para cualquier usuario autenticado (sin importar role).

## Usuario actual

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/users/me` | Obtiene los datos del usuario autenticado. |

## Jugar trivias

Endpoints para participar en trivias asignadas.

| Método | Endpoint | Descripción                                                                                 |
|--------|----------|---------------------------------------------------------------------------------------------|
| `GET` | `/trivias/me` | Lista las trivias asignadas al usuario actual.                                              |
| `GET` | `/trivias/{id}/play` | Obtiene preguntas y opciones para jugar. No expone qué opción es correcta ni la dificultad. |
| `POST` | `/trivias/{id}/submit` | Envía las respuestas y calcula el score. Debe incluir exactamente una respuesta por cada pregunta de la trivia. Idempotente: una segunda llamada después de completar devuelve el mismo resultado sin reprocesar ni alterar el estado.                      |

## Ranking

| Método | Endpoint | Descripción                                           |
|--------|----------|-------------------------------------------------------|
| `GET` | `/trivias/{id}/ranking` | Ranking de una trivia específica. Ordenado por score DESC, con desempate por menor tiempo de finalización (`completed_at - started_at` ASC). |

---

# Endpoints de administración

Endpoints que requieren rol `admin`.

## Gestión de usuarios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/users` | Lista todos los usuarios del sistema. |

## Gestión de preguntas

Las preguntas viven independientes de las trivias. Una misma pregunta puede aparecer 
en múltiples trivias.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/questions` | Crea una pregunta con sus opciones. Mínimo 2 opciones, solo una correcta. |
| `GET` | `/questions` | Lista todas las preguntas del sistema. |

## Gestión de trivias

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/trivias` | Crea una trivia con preguntas y participantes asignados. Mínimo 1 pregunta y 1 participante. |
| `GET` | `/trivias` | Lista todas las trivias del sistema. |
| `GET` | `/trivias/{id}` | Obtiene los detalles de una trivia específica. |