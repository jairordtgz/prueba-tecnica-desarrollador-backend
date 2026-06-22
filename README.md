# ISP/ERP – Gestión de Clientes, Líneas y Cobranza

Mini-servicio REST (Django + DRF) con proceso asíncrono periódico (Celery + Redis)
para control de morosidad de líneas de servicio.

## Stack

- Django + Django REST Framework
- SQLite (desarrollo local) / PostgreSQL (Docker)
- Celery + Celery Beat
- Redis (broker)
- pytest / pytest-django

## Arquitectura — decisiones y trade-offs

- **No se aplicó Clean Architecture completa** (repositorios abstractos, entidades
  desacopladas del ORM). Para el tamaño de este proyecto y con un solo backend de
  persistencia, esa capa extra agrega ceremonia sin beneficio real (YAGNI). El ORM
  de Django ya cumple el rol de capa de persistencia.
- **Separación de capas solo donde hay lógica de negocio no trivial**: la app
  `cobranza` separa `tasks.py` (orquestación/Celery) de `services.py`
  (`MorosidadService`, la regla de negocio pura). Esto permite testear la lógica
  de suspensión/reactivación sin levantar Redis ni Celery. El CRUD de
  `cliente`/`linea` no tiene esta separación porque no la necesita: la validación
  vive en el serializer, que es su nivel correcto de abstracción en DRF.
- **SOLID aplicado de forma puntual**:
  - SRP: `tasks.py` (IO) vs `services.py` (regla) vs `models.py` (esquema).
  - OCP: la política de suspensión está aislada en `_determinar_accion()`;
    cambiar la regla no toca el resto del flujo.
  - DIP: el task depende de `MorosidadService`, no de queries inline.
- **Soft delete**: `is_active=False` en `Cliente` y `LineaServicio`, nunca borrado
  físico. `Rubro` no tiene `is_active`; el estado `ANULADO` cumple esa función.
- **Idempotencia**: cada corrida de la tarea **recalcula desde cero**
  `saldo_vencido` (agregación SQL, no acumulación) y compara el `estado_linea`
  actual antes de decidir la acción. Corridas repetidas sin pagos nuevos producen
  el mismo estado/saldo. Sí se crea un `CollectionsRequestLog` nuevo por
  ejecución — es esperado (trazabilidad por corrida), no una duplicación.
- **Regla de negocio documentada**: líneas `CANCELADO` o `NO_INSTALADO` nunca se
  suspenden aunque tengan rubros vencidos. Se les sigue calculando
  `saldo_vencido`/`unpaid_count` para trazabilidad, pero `action_taken=NONE`.
- **N+1 evitado**: el cálculo de morosidad usa `.aggregate(Count, Sum)` en una
  sola consulta por línea, en vez de traer todos los `Rubro` a Python.
- **Resiliencia**: el log de cada línea se crea con `status=FAILED` por defecto
  y solo se sobreescribe a `SUCCESS` si el bloque `try` termina sin errores — así
  un fallo a medias del worker no deja el registro ambiguo. Además, el task
  completo tiene `autoretry_for` con backoff para fallas sistémicas (ej. caída de
  conexión a BD), mientras que errores por línea individual se capturan y no
  detienen el resto del lote.
- **Autenticación**: Token simple de DRF (`rest_framework.authtoken`). Cualquier
  usuario autenticado puede leer/crear/editar; el `DELETE` (soft delete) queda
  restringido a usuarios `is_staff` vía `core/permissions.py`.
- **`estado-cobranza` calcula `unpaid_count` en vivo** (no desde el último log),
  para que el resumen sea correcto incluso si el batch de Celery no ha corrido
  recientemente.

## Setup

```bash
git clone <url-del-repo>
cd prueba-tecnica-desarrollador-backend
python -m venv venv

# Windows
venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Variables de entorno

| Variable | Default (sin definir) | Uso |
|---|---|---|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Broker de Celery |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Backend de resultados |
| `DB_ENGINE` | `django.db.backends.sqlite3` | Motor de BD |
| `DB_NAME` | `db.sqlite3` | Nombre/archivo de BD |
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | — | Solo si `DB_ENGINE` es Postgres |

Sin definir nada, el proyecto corre con SQLite local — útil para desarrollo rápido.

## Comandos

```bash
# Migraciones
python manage.py migrate

# Crear usuario admin (puede hacer DELETE)
python manage.py createsuperuser

# Servidor de desarrollo
python manage.py runserver

# Redis (si no usas Docker)
docker run -p 6379:6379 redis:7-alpine

# Worker de Celery (Windows requiere --pool=solo)
celery -A isp_erp_backend worker -l info --pool=solo
# Linux/macOS
celery -A isp_erp_backend worker -l info

# Celery Beat (tarea periódica cada 5 min)
celery -A isp_erp_backend beat -l info

# Tests
pytest -v
```

## Docker (alternativa completa)

```bash
docker-compose up --build
```

Levanta Postgres, Redis, `web`, `celery_worker` y `celery_beat`.

## Cómo probar

1. Obtener token:
```bash
   curl -X POST http://127.0.0.1:8000/api/auth/token/ \
     -d "username=admin&password=<tu_password>"
```
2. Usar el token en cada request: header `Authorization: Token <token>`.
3. Ver `requests.http` para ejemplos completos de cada endpoint.
4. Para probar el proceso de cobranza sin esperar 5 minutos:
```bash
   python manage.py shell
```
```python
   from cobranza.tasks import procesar_morosidad
   procesar_morosidad()  # corre sincrónico, sin necesidad de worker activo
```
5. Healthcheck: `GET /api/health/` · Métricas: `GET /api/metrics/`.

## Endpoints

| Método | Endpoint | Auth |
|---|---|---|
| POST | `/api/auth/token/` | No |
| GET/POST | `/api/clientes/` | Sí (cualquier usuario autenticado) |
| GET/PATCH | `/api/clientes/{id}/` | Sí |
| DELETE | `/api/clientes/{id}/` | Sí, solo `is_staff` |
| GET/POST | `/api/lineas/` | Sí |
| GET/PATCH | `/api/lineas/{id}/` | Sí |
| DELETE | `/api/lineas/{id}/` | Sí, solo `is_staff` |
| GET | `/api/lineas/{id}/estado-cobranza/` | Sí |
| GET | `/api/health/` | No |
| GET | `/api/metrics/` | No |