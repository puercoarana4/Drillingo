# Plan de Implementación: Drillingo

## Overview

Implementación incremental de Drillingo: plataforma web gamificada para aprendizaje de inglés AAVE/Drill. Stack: FastAPI (Python 3.12) + Next.js 14 + PostgreSQL 16. Las tareas siguen el orden backend-first (infraestructura → datos → módulos de negocio) seguido del frontend y los property-based tests con Hypothesis.

## Tasks

- [x] 1. Scaffolding del proyecto y configuración de infraestructura
  - Crear estructura de directorios `backend/` y `frontend/` en la raíz del repositorio
  - Crear `backend/requirements.txt` con dependencias fijadas: `fastapi==0.111.0`, `uvicorn[standard]==0.29.0`, `sqlalchemy[asyncio]==2.0.30`, `alembic==1.13.1`, `asyncpg==0.29.0`, `passlib[bcrypt]==1.7.4`, `python-jose[cryptography]==3.3.0`, `pydantic[email]==2.7.1`, `pytz==2024.1`, `hypothesis==6.100.1`, `pytest==8.2.0`, `pytest-asyncio==0.23.6`, `httpx==0.27.0`
  - Crear `backend/app/main.py` con la instancia FastAPI, registro de routers y CORS configurado
  - Crear `backend/app/core/config.py` con `Settings` (Pydantic BaseSettings) para `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
  - Crear `backend/app/core/database.py` con el engine async de SQLAlchemy y la función `get_db` como dependencia
  - Crear `docker-compose.yml` en la raíz con servicios: `db` (postgres:16-alpine, puerto 5432), `backend` (build ./backend, puerto 8000), `frontend` (build ./frontend, puerto 3000)
  - Crear `backend/.env.example` con las variables de entorno requeridas
  - _Requirements: 2.1_

- [x] 2. Migraciones de base de datos con Alembic
  - Inicializar Alembic en `backend/alembic/` con `alembic init alembic`
  - Configurar `alembic/env.py` para usar el engine async de SQLAlchemy y apuntar a `app.models`
  - Crear migración inicial que defina los tres enums PostgreSQL: `level_band_enum` (B1/B2/C1), `dialect_segment_enum` (east_coast/midwest), `module_type_enum` (reading/listening/writing/speaking)
  - Crear migración con el DDL completo de las 7 tablas: `users`, `lessons`, `lesson_progress`, `vocabulary_items`, `user_vocabulary`, `oral_reports`, `streaks`, incluyendo todas las constraints CHECK, UNIQUE, FK con ON DELETE CASCADE y los índices definidos en el diseño
  - Crear índice GIN sobre `oral_reports.raw_json` para consultas JSONB
  - Verificar que `alembic upgrade head` ejecuta sin errores contra la base de datos de desarrollo
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_

- [x] 3. Módulo Auth — modelos, schemas, repositorio, servicio y router
  - [x] 3.1 Crear modelo SQLAlchemy `backend/app/models/user.py` con la clase `User` mapeada a la tabla `users` (todos los campos del DDL)
  - [x] 3.2 Crear schemas Pydantic en `backend/app/schemas/auth.py`: `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`; validar que `password` tenga mínimo 8 caracteres en `RegisterRequest`
  - [x] 3.3 Crear `backend/app/core/security.py` con funciones: `hash_password(plain: str) -> str` (bcrypt, cost factor 12), `verify_password(plain, hashed) -> bool`, `create_access_token(data: dict) -> str` (JWT 24h), `decode_token(token: str) -> dict`
  - [x] 3.4 Crear `backend/app/repositories/user_repo.py` con métodos async: `get_by_email`, `get_by_id`, `create`
  - [x] 3.5 Crear `backend/app/services/auth_service.py` con métodos: `register(data) -> TokenResponse` (lanza 409 si email duplicado, 400 si password < 8 chars), `login(data) -> TokenResponse` (lanza 401 si credenciales inválidas)
  - [x] 3.6 Crear `backend/app/routers/auth.py` con los tres endpoints: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` (requiere JWT válido)
  - [x] 3.7 Registrar el router de auth en `main.py` y verificar que los tres endpoints responden correctamente con `pytest` usando `TestClient`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 4. Módulo Content — lecciones, vocabulario y segmentación dialectal
  - [x] 4.1 Crear modelos SQLAlchemy `backend/app/models/lesson.py` y `backend/app/models/vocabulary.py` mapeados a `lessons` y `vocabulary_items`
  - [x] 4.2 Crear schemas Pydantic en `backend/app/schemas/content.py`: `LessonResponse`, `VocabularyItemResponse`, `LessonDetailResponse`; incluir `dialect_segment` en todas las respuestas de vocabulario
  - [x] 4.3 Crear `backend/app/repositories/lesson_repo.py` con métodos async: `find_by_dialect_and_level(dialect, level)`, `find_all_ordered_by_day()`, `get_by_id(lesson_id)`
  - [x] 4.4 Crear `backend/app/repositories/vocabulary_repo.py` con métodos async: `find_by_dialect_and_level(dialect, level)`, `get_by_id(item_id)`
  - [x] 4.5 Crear `backend/app/services/content_service.py` con métodos: `get_lessons(dialect=None, level=None)` (si no hay dialect, devuelve ambos ordenados por `day_order`; si hay dialect, filtra), `get_lesson_detail(lesson_id)`, `get_vocabulary(dialect=None, level=None)`
  - [x] 4.6 Crear `backend/app/routers/content.py` con los cuatro endpoints GET definidos en el diseño; proteger con JWT middleware
  - [x] 4.7 Escribir tests unitarios para `content_service.py` verificando el filtrado por dialect y level
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 5.6, 5.7, 5.8_

- [-] 5. Módulo Progress — registro de progreso, XP y level-up automático
  - [x] 5.1 Crear modelos SQLAlchemy `backend/app/models/progress.py` (tabla `lesson_progress`) y actualizar `backend/app/models/user.py` para incluir `xp_total`
  - [ ] 5.2 Crear schemas Pydantic en `backend/app/schemas/progress.py`: `LessonProgressRequest`, `LessonProgressResponse`, `ProgressSummaryResponse`, `VocabularyProgressResponse`
  - [ ] 5.3 Crear `backend/app/repositories/progress_repo.py` con métodos async: `create_lesson_progress(user_id, lesson_id, module_type, score)`, `get_user_summary(user_id)`, `get_user_vocabulary_progress(user_id)`
  - [ ] 5.4 Crear `backend/app/services/progress_service.py` con métodos:
    - `record_lesson_progress(user_id, data)`: persiste el registro, otorga XP según módulo (Reading=10, Listening=15, Writing=20, Speaking=25), llama a `check_level_up`
    - `check_level_up(user_id, new_xp_total)`: evalúa umbrales (500 XP → B2, 2000 XP → C1) y actualiza `level_band` si corresponde, registrando la fecha del cambio
    - `mark_vocabulary_mastered(user_id, vocab_item_id)`: actualiza `mastered=True` cuando `correct_count >= 3`
    - `update_vocabulary_interaction(user_id, vocab_item_id, correct)`: incrementa `correct_count` y actualiza `last_reviewed_at`
  - [ ] 5.5 Crear `backend/app/routers/progress.py` con los cuatro endpoints definidos en el diseño
  - [ ] 5.6 Escribir tests unitarios para `progress_service.py` verificando: XP correcto por módulo, level-up en umbral exacto, marcado automático de vocabulario dominado
  - _Requirements: 4.3, 4.6, 5.3, 5.5, 5.6, 6.3, 6.5, 6.6, 10.1, 10.2, 10.3, 10.4, 10.6, 11.1, 11.4_

- [ ] 6. Streak Engine — cálculo con timezone del cliente y endpoint de check-in
  - [ ] 6.1 Crear modelo SQLAlchemy `backend/app/models/streak.py` mapeado a la tabla `streaks`
  - [ ] 6.2 Crear schemas Pydantic en `backend/app/schemas/streak.py`: `CheckinRequest` (campo `timezone: str`), `StreakResponse`
  - [ ] 6.3 Crear `backend/app/repositories/streak_repo.py` con métodos async: `get_by_user_id(user_id)`, `upsert(streak)`
  - [ ] 6.4 Crear `backend/app/services/streak_engine.py` con la función `process_checkin(user_id, client_timezone, db)`:
    - Validar timezone IANA con `pytz.timezone()`; lanzar HTTP 400 si es inválida
    - Calcular `today_client` usando la timezone del cliente
    - Aplicar la lógica de los cuatro casos: primera actividad, mismo día, día consecutivo, racha rota
    - Actualizar `longest_streak` si `current_streak` lo supera
    - Persistir y retornar el estado actualizado
  - [ ] 6.5 Crear `backend/app/routers/streak.py` con `POST /api/streak/checkin` y `GET /api/streak`
  - [ ] 6.6 Escribir tests unitarios para `streak_engine.py` verificando: primer check-in, día consecutivo, racha rota, mismo día (idempotente), timezone inválida devuelve 400
  - _Requirements: 8.1, 8.2, 8.3, 8.5, 8.6, 8.8, 8.9_

- [ ] 7. Report Parser — ingesta y validación de Oral Reports
  - [ ] 7.1 Crear modelo SQLAlchemy `backend/app/models/oral_report.py` mapeado a la tabla `oral_reports` con el campo `raw_json` como `JSONB`
  - [ ] 7.2 Crear schemas Pydantic en `backend/app/schemas/report.py`: `OralReportRequest` con validadores que rechacen scores fuera de [0, 100] y campos obligatorios faltantes; `OralReportResponse`
  - [ ] 7.3 Crear `backend/app/repositories/oral_report_repo.py` con métodos async: `create(user_id, data)`, `get_by_user(user_id)`, `query_by_jsonb(user_id, condition)`
  - [ ] 7.4 Crear `backend/app/services/report_parser.py` con método `parse_and_persist(user_id, raw_payload, db)`:
    - Validar campos obligatorios (`fluency_score`, `pronunciation_score`); lanzar 400 si faltan
    - Validar rango [0, 100]; lanzar 422 si fuera de rango
    - Persistir `raw_json` sin modificar el contenido original
    - Extraer métricas numéricas y llamar a `progress_service` para actualizar promedios del dashboard
  - [ ] 7.5 Crear `backend/app/routers/report.py` con `POST /api/reports/oral` y `GET /api/reports/oral`
  - [ ] 7.6 Escribir tests unitarios para `report_parser.py` verificando: campo faltante → 400, score fuera de rango → 422, payload válido persiste correctamente
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 2.6, 2.9, 2.10_

- [ ] 8. Dashboard — agregación de métricas y endpoint único
  - [ ] 8.1 Crear `backend/app/services/dashboard_service.py` con el método `get_dashboard(user_id, db)` que ejecuta en paralelo (usando `asyncio.gather`) las siguientes consultas:
    - `level_band` y `xp_total` del usuario
    - `current_streak` y `longest_streak` de la tabla `streaks`
    - Scores promedio por `module_type` de `lesson_progress` (para el radar chart)
    - Conteo de `user_vocabulary` donde `mastered = true`
    - Últimos 30 registros de `oral_reports` ordenados por `submitted_at DESC`
    - Historial de cambios de `level_band` (de `lesson_progress` agrupado por fecha)
  - [ ] 8.2 Crear schema Pydantic `backend/app/schemas/dashboard.py` con `DashboardResponse` que incluya todos los campos del response definido en el diseño
  - [ ] 8.3 Crear `backend/app/routers/dashboard.py` con `GET /api/dashboard`; proteger con JWT
  - [ ] 8.4 Escribir test de integración que verifique que `GET /api/dashboard` responde en menos de 500ms con datos de prueba en la base de datos
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [ ] 9. Checkpoint — Backend completo
  - Verificar que todos los routers están registrados en `main.py`
  - Ejecutar `pytest backend/tests/` y confirmar que todos los tests pasan
  - Verificar que `alembic upgrade head` ejecuta sin errores
  - Confirmar que `docker-compose up` levanta los tres servicios sin errores
  - Preguntar al usuario si hay ajustes antes de continuar con el frontend

- [ ] 10. Frontend — Setup, layout y sistema de diseño
  - Inicializar proyecto Next.js 14 en `frontend/` con App Router: `npx create-next-app@14 frontend --typescript --tailwind --app --no-src-dir`
  - Configurar `frontend/tailwind.config.ts` con la paleta de colores de Drillingo: `background: '#1A1A1A'`, `surface: '#242424'`, `accent: '#FF0033'`, `foreground: '#FFFFFF'`; añadir `fontFamily` con `Roboto Black` e `Impact`
  - Crear `frontend/app/layout.tsx` con el layout raíz: fondo `#1A1A1A`, modo oscuro obligatorio, importación de fuentes Google (Roboto Black)
  - Crear componentes UI primitivos en `frontend/components/ui/`: `Button.tsx` (altura mínima 48px, texto en mayúsculas, variante `primary` con `bg-accent`), `Card.tsx` (fondo `#242424`), `Badge.tsx`
  - Crear `frontend/components/layout/Navbar.tsx` con navegación principal y `StreakBadge.tsx` con ícono de fuego y contador
  - Crear `frontend/lib/api.ts` como wrapper de `fetch` con: base URL configurable, inyección automática del JWT desde `localStorage`, manejo de errores HTTP
  - Crear `frontend/lib/auth.ts` con helpers: `getToken()`, `setToken()`, `removeToken()`, `isAuthenticated()`
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

- [ ] 11. Frontend — Módulo Auth (login y registro)
  - Crear `frontend/app/(auth)/register/page.tsx` con formulario de registro (email, username, password); validar password >= 8 chars en cliente; llamar a `POST /api/auth/register`; redirigir al dashboard en éxito
  - Crear `frontend/app/(auth)/login/page.tsx` con formulario de login; llamar a `POST /api/auth/login`; persistir JWT; redirigir al dashboard
  - Implementar middleware de Next.js en `frontend/middleware.ts` para proteger rutas del grupo `(app)` redirigiendo a `/login` si no hay JWT válido
  - _Requirements: 1.1, 1.2, 1.5_

- [ ] 12. Frontend — Módulo Reading (Street Texts)
  - Crear `frontend/components/modules/ChatBubble.tsx` con props `message`, `sender` (`self` | `other`), `highlighted_terms`; renderizar burbujas diferenciadas por emisor estilo iMessage/DM
  - Crear `frontend/app/(app)/modules/reading/[id]/page.tsx` que cargue el ejercicio de Reading, renderice los mensajes con `ChatBubble`, y presente un input para cada término marcado
  - Implementar lógica de evaluación en el cliente: al enviar respuesta, llamar a `POST /api/progress/lesson`; si incorrecta, mostrar definición y ejemplo antes de continuar
  - Al completar todos los términos, mostrar resumen de score y XP ganado
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ] 13. Frontend — Módulo Listening (The Cypher)
  - Crear `frontend/components/modules/AudioPlayer.tsx` con controles de reproducción (play/pause, barra de progreso, velocidad 0.75x/1x/1.25x); recibir `audio_url` como prop y hacer streaming directo a S3
  - Crear `frontend/components/modules/FillInBlank.tsx` que renderice la transcripción parcial con inputs en los espacios en blanco
  - Crear `frontend/app/(app)/modules/listening/[id]/page.tsx` que integre `AudioPlayer` y `FillInBlank`; al enviar respuestas, llamar a `POST /api/progress/lesson`; mostrar respuesta correcta con explicación si falla
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [ ] 14. Frontend — Módulo Writing (Spitting Bars)
  - Crear `frontend/components/modules/TranslationInput.tsx` con textarea para la traducción y botón de envío
  - Crear `frontend/app/(app)/modules/writing/[id]/page.tsx` que muestre la frase formal, el input de traducción, y evalúe la respuesta contra las variantes aceptadas (normalizar a minúsculas y trim antes de comparar)
  - Implementar lógica de variantes ortográficas equivalentes en el cliente (ej: "finna" == "fin to")
  - Al completar, llamar a `POST /api/progress/lesson` y mostrar XP ganado
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ] 15. Frontend — Módulo Speaking (Live Report Sync)
  - Crear `frontend/components/modules/OralReportForm.tsx` con campos: `session_duration_seconds` (number input), `fluency_score` (slider 0–100), `pronunciation_score` (slider 0–100), `notes` (textarea opcional)
  - Crear `frontend/app/(app)/modules/speaking/page.tsx` que integre `OralReportForm`; al enviar, llamar a `POST /api/reports/oral`; mostrar confirmación con los scores registrados
  - Manejar errores 400 y 422 del backend mostrando mensajes descriptivos al usuario
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 16. Frontend — Dashboard (métricas y gráficas)
  - Instalar dependencias: `recharts@2.12.0`, `date-fns@3.6.0`
  - Crear `frontend/components/dashboard/RadarChart.tsx` usando `RadarChart` de Recharts con las cinco dimensiones (Reading, Listening, Writing, Speaking, Vocabulary); colores de acento `#FF0033`
  - Crear `frontend/components/dashboard/LevelProgressBar.tsx` que muestre la barra de progreso B1→B2→C1 con XP actual y umbral siguiente
  - Crear `frontend/components/dashboard/OralHistoryChart.tsx` usando `LineChart` de Recharts para los últimos 30 reportes orales (fluency y pronunciation como dos líneas)
  - Crear `frontend/components/dashboard/StreakDisplay.tsx` con ícono de fuego, `current_streak` prominente y `longest_streak`
  - Crear `frontend/app/(app)/dashboard/page.tsx` que llame a `GET /api/dashboard` y componga todos los componentes del dashboard
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 8.4, 10.5_

- [ ] 17. Frontend — Vocabulario dominado
  - Crear `frontend/app/(app)/vocabulary/page.tsx` que llame a `GET /api/progress/vocabulary` y muestre la lista de items con `mastered = true`
  - Implementar filtro por `dialect_segment` (east_coast / midwest) en el cliente con botones toggle
  - Mostrar para cada item: término, definición, `dialect_segment` como badge, y ejemplo de uso en contexto
  - _Requirements: 11.2, 11.3, 11.5_

- [ ] 18. Checkpoint — Frontend completo
  - Verificar que todas las páginas renderizan sin errores en `next build`
  - Confirmar que el modo oscuro y los colores de acento se aplican correctamente en todas las vistas
  - Verificar que el ratio de contraste 4.5:1 se cumple en los componentes principales
  - Confirmar que la interfaz es funcional en 375px de ancho (móvil)
  - Preguntar al usuario si hay ajustes antes de continuar con los PBT

- [ ] 19. Property-Based Tests con Hypothesis
  - [ ] 19.1 Crear `backend/tests/property/test_oral_report_round_trip.py` e implementar Property 1 (round-trip de Oral Report):
    - Usar `@given` con `st.integers(0, 100)` para scores y `st.integers(1, 86400)` para duración
    - Verificar que `OralReportSchema(**payload).model_dump()` produce un objeto semánticamente equivalente al original
    - Configurar `@settings(max_examples=100)`
    - **Property 1: Round-trip de Oral Report**
    - **Validates: Requirements 7.7**
  - [ ] 19.2 Crear `backend/tests/property/test_streak_invariant.py` e implementar Property 2 (invariante del streak):
    - Usar `@given` con `st.lists(st.dates(...), min_size=1, max_size=365).map(sorted)`
    - Implementar función auxiliar `compute_streak_from_dates(dates)` que simule el Streak Engine
    - Verificar que `current_streak == count_consecutive_days_ending_at(dates, dates[-1])`
    - **Property 2: Invariante del Streak**
    - **Validates: Requirements 8.7**
  - [ ] 19.3 Crear `backend/tests/property/test_score_validation.py` e implementar Property 3 (scores fuera de rango rechazados):
    - Usar `@given` con `st.one_of(st.integers(max_value=-1), st.integers(min_value=101))`
    - Verificar que `OralReportSchema(fluency_score=score, ...)` lanza `ValidationError`
    - **Property 3: Validación de scores fuera de rango**
    - **Validates: Requirements 7.4**
  - [ ] 19.4 Crear `backend/tests/property/test_dialect_filter.py` e implementar Property 4 (filtrado de lecciones por dialecto):
    - Definir `lesson_strategy()` con `st.builds` sobre un dataclass o dict de lección
    - Usar `@given` con `st.sampled_from(["east_coast", "midwest"])` y `st.lists(lesson_strategy(), max_size=50)`
    - Verificar que `filter_lessons_by_dialect(lessons, dialect)` devuelve solo lecciones con el dialect solicitado
    - **Property 4: Filtrado de lecciones por dialecto**
    - **Validates: Requirements 3.1**
  - [ ] 19.5 Crear `backend/tests/property/test_longest_streak_consistency.py` e implementar Property 5 (consistencia longest_streak):
    - Reutilizar `compute_streak_from_dates` de la Property 2
    - Usar `@given` con la misma estrategia de fechas
    - Verificar que `streak.longest_streak >= streak.current_streak` para toda secuencia de fechas
    - **Property 5: Consistencia longest_streak**
    - **Validates: Requirements 8.2**
  - [ ] 19.6 Crear `backend/tests/property/__init__.py` y `backend/tests/conftest.py` con la configuración de Hypothesis (`settings.register_profile("ci", max_examples=100)`)
  - [ ] 19.7 Ejecutar `pytest backend/tests/property/ -v` y confirmar que las 5 propiedades pasan
  - _Requirements: 7.4, 7.7, 8.2, 8.7, 3.1_

- [ ] 20. Checkpoint final — Integración y cierre
  - Ejecutar `pytest backend/tests/ -v` y confirmar que todos los tests (unitarios + PBT) pasan
  - Ejecutar `next build` en `frontend/` y confirmar que no hay errores de compilación
  - Verificar que `docker-compose up` levanta los tres servicios y el flujo completo (registro → lección → dashboard) funciona end-to-end
  - Confirmar que `GET /api/dashboard` responde en menos de 500ms con datos reales
  - Preguntar al usuario si hay ajustes finales antes de cerrar la implementación

## Notes

- Las tareas de PBT (19.1–19.5) son parte integral del plan y deben implementarse; no son opcionales
- Cada tarea referencia los requisitos específicos para trazabilidad completa
- El orden de las tareas garantiza que no haya código huérfano: cada módulo se integra en el paso siguiente
- Los checkpoints (9, 18, 20) son puntos de validación explícitos antes de avanzar a la siguiente fase
- El campo `xp_total` se añade a la tabla `users` en el DDL (tarea 2) aunque el requisito 2.1 no lo menciona explícitamente; está justificado por los requisitos 10.1–10.3
- Los umbrales de XP son: 500 XP para B1→B2, y 500+1500=2000 XP acumulados para B2→C1 (según requisito 10.3)
