# Requirements Document

## Introduction

Drillingo es una aplicación web gamificada para el aprendizaje de inglés avanzado (niveles B1 a C1) con foco exclusivo en el AAVE (African American Vernacular English) y el dialecto de la cultura Drill de Estados Unidos, segmentado entre las escenas de Nueva York (East Coast Drill) y Chicago (Midwest/Chiraq Drill). La plataforma combina módulos de lectura, escucha, escritura y práctica oral con mecánicas de gamificación, un dashboard analítico y una estética streetwear dark-mode. Todo el contenido lingüístico se trata como material académico de análisis sociolingüístico sin censura.

---

## Glossary

- **Drillingo**: Nombre del sistema completo descrito en este documento.
- **User**: Persona registrada que utiliza la plataforma para aprender.
- **Lesson**: Unidad de contenido diaria compuesta por uno o más módulos de aprendizaje.
- **Module**: Componente de aprendizaje dentro de una lección (Reading, Listening, Writing, Speaking).
- **Dialect_Segment**: Clasificación dialectal del contenido: `east_coast` (Nueva York) o `midwest` (Chicago).
- **Vocabulary_Item**: Entrada de slang o jerga con definición, ejemplos y región de origen.
- **Streak**: Contador de días consecutivos en los que el User completó al menos una lección.
- **XP**: Puntos de experiencia acumulados por completar actividades.
- **Level_Band**: Banda de nivel CEFR asignada al User: B1, B2, C1.
- **Oral_Report**: Objeto JSON enviado por el User con métricas de una sesión de práctica oral externa.
- **Fluency_Score**: Métrica numérica (0–100) que representa la fluidez oral del User.
- **Pronunciation_Score**: Métrica numérica (0–100) que representa la precisión de pronunciación del User.
- **Dashboard**: Panel visual principal que muestra el progreso agregado del User.
- **Streak_Engine**: Componente del backend responsable de calcular y actualizar el Streak del User.
- **Report_Parser**: Componente del backend responsable de parsear y validar Oral_Reports.
- **Content_Service**: Componente del backend responsable de servir Lessons y Vocabulary_Items segmentados por Dialect_Segment.
- **Progress_Service**: Componente del backend responsable de registrar y consultar el progreso del User.
- **Auth_Service**: Componente del backend responsable del registro, autenticación y gestión de sesiones.
- **Object_Storage**: Servicio externo de almacenamiento de objetos (AWS S3, Cloudinary o Supabase Storage) donde se almacenan los archivos de audio de las lecciones.
- **Audio_URL**: Cadena de texto (VARCHAR) que contiene la URL pública o firmada que apunta al archivo de audio almacenado en el Object_Storage.

---

## Requirements

### Requirement 1: Registro y Autenticación de Usuarios

**User Story:** Como visitante, quiero registrarme y autenticarme en Drillingo, para que mi progreso y configuración queden persistidos de forma segura.

#### Acceptance Criteria

1. THE Auth_Service SHALL exponer un endpoint de registro que acepte email, contraseña y nombre de usuario.
2. WHEN un visitante envía credenciales de registro válidas, THE Auth_Service SHALL crear un registro de User en la base de datos y devolver un token de sesión JWT.
3. IF el email proporcionado ya existe en la base de datos, THEN THE Auth_Service SHALL devolver un error HTTP 409 con el mensaje "Email already registered".
4. IF la contraseña proporcionada tiene menos de 8 caracteres, THEN THE Auth_Service SHALL devolver un error HTTP 400 con el mensaje "Password must be at least 8 characters".
5. WHEN un User envía credenciales de inicio de sesión válidas, THE Auth_Service SHALL devolver un token JWT con tiempo de expiración de 24 horas.
6. IF un User envía credenciales de inicio de sesión inválidas, THEN THE Auth_Service SHALL devolver un error HTTP 401 con el mensaje "Invalid credentials".
7. THE Auth_Service SHALL almacenar contraseñas usando un algoritmo de hashing bcrypt con un factor de coste mínimo de 12.

---

### Requirement 2: Modelo de Datos Relacional (PostgreSQL)

**User Story:** Como arquitecto del sistema, quiero un esquema relacional en PostgreSQL, para que usuarios, progreso, lecciones, vocabulario e historial de reportes orales queden persistidos de forma estructurada y consultable.

#### Acceptance Criteria

1. THE Drillingo SHALL mantener una tabla `users` con columnas: `id` (UUID PK), `email` (unique, not null), `username` (unique, not null), `password_hash` (not null), `level_band` (enum B1/B2/C1, default B1), `created_at`, `updated_at`.
2. THE Drillingo SHALL mantener una tabla `lessons` con columnas: `id` (UUID PK), `title` (not null), `dialect_segment` (enum east_coast/midwest, not null), `level_band` (enum B1/B2/C1, not null), `day_order` (integer, not null), `audio_url` (VARCHAR, not null), `created_at`. El campo `audio_url` almacenará exclusivamente la URL del archivo de audio en el Object_Storage; no se almacenarán BLOBs de audio en la base de datos.
3. THE Drillingo SHALL mantener una tabla `lesson_progress` con columnas: `id` (UUID PK), `user_id` (FK → users), `lesson_id` (FK → lessons), `completed_at` (timestamp), `score` (integer 0–100), `module_type` (enum reading/listening/writing/speaking).
4. THE Drillingo SHALL mantener una tabla `vocabulary_items` con columnas: `id` (UUID PK), `term` (not null), `definition` (not null), `example_sentence`, `dialect_segment` (enum east_coast/midwest), `level_band` (enum B1/B2/C1), `created_at`.
5. THE Drillingo SHALL mantener una tabla `user_vocabulary` con columnas: `user_id` (FK → users), `vocabulary_item_id` (FK → vocabulary_items), `mastered` (boolean, default false), `last_reviewed_at` (timestamp). La clave primaria es compuesta `(user_id, vocabulary_item_id)`.
6. THE Drillingo SHALL mantener una tabla `oral_reports` con columnas: `id` (UUID PK), `user_id` (FK → users), `raw_json` (JSONB, not null), `fluency_score` (integer 0–100), `pronunciation_score` (integer 0–100), `session_duration_seconds` (integer), `submitted_at` (TIMESTAMPTZ, not null). El tipo JSONB (no TEXT ni VARCHAR) es obligatorio para permitir consultas SQL directas dentro del JSON.
7. THE Drillingo SHALL mantener una tabla `streaks` con columnas: `user_id` (FK → users, PK), `current_streak` (integer, default 0), `longest_streak` (integer, default 0), `last_activity_date` (date).
8. WHEN se elimina un registro de `users`, THE Drillingo SHALL eliminar en cascada todos los registros asociados en `lesson_progress`, `user_vocabulary`, `oral_reports` y `streaks`.
9. THE Drillingo SHALL permitir consultas SQL directas sobre el campo `raw_json` de la tabla `oral_reports` usando operadores JSONB nativos de PostgreSQL (por ejemplo: `raw_json->>'pronunciation_score' < '70'`).
10. WHEN se ejecuta una consulta de filtrado sobre `oral_reports` usando operadores JSONB, THE Drillingo SHALL devolver únicamente los registros cuyo campo `raw_json` satisfaga la condición especificada (por ejemplo: sesiones donde `pronunciation_score < 70`).

---

### Requirement 3: Gestión de Contenido y Segmentación Dialectal

**User Story:** Como estudiante, quiero que el contenido de las lecciones esté segmentado entre East Coast Drill y Midwest/Chiraq Drill, para que pueda aprender a diferenciar regionalismos y acentos.

#### Acceptance Criteria

1. THE Content_Service SHALL servir lecciones filtradas por `dialect_segment` cuando el User seleccione una región.
2. THE Content_Service SHALL servir lecciones filtradas por `level_band` correspondiente al nivel actual del User.
3. WHEN el User solicita el vocabulario de una lección, THE Content_Service SHALL devolver únicamente los Vocabulary_Items cuyo `dialect_segment` coincida con el de la lección.
4. THE Content_Service SHALL etiquetar cada Vocabulary_Item con su región de origen (east_coast o midwest) en todas las respuestas de API.
5. IF el User no ha seleccionado una región, THEN THE Content_Service SHALL devolver lecciones de ambos dialectos ordenadas por `day_order`.
6. THE Content_Service SHALL incluir en cada lección al menos un ejemplo de uso en contexto (frase o fragmento lírico) para cada Vocabulary_Item.

---

### Requirement 4: Módulo Reading — Street Texts

**User Story:** Como estudiante, quiero descifrar mensajes de chat llenos de abreviaturas reales del AAVE y la cultura Drill, para que pueda desarrollar comprensión lectora en contextos auténticos.

#### Acceptance Criteria

1. THE Drillingo SHALL renderizar los ejercicios de Reading en una interfaz que simule una pantalla de chat estilo iMessage/Instagram DM con burbujas de mensaje diferenciadas por emisor.
2. WHEN el User abre un ejercicio de Reading, THE Content_Service SHALL cargar un conjunto de mensajes con entre 3 y 8 abreviaturas o términos de slang marcados para descifrar.
3. WHEN el User envía una respuesta a un término marcado, THE Progress_Service SHALL registrar si la respuesta es correcta o incorrecta y actualizar el score de la lección.
4. IF el User responde incorrectamente a un término, THEN THE Drillingo SHALL mostrar la definición correcta del término y un ejemplo de uso en contexto antes de continuar.
5. THE Drillingo SHALL incluir abreviaturas reales del AAVE y la cultura Drill como: "idn" (I don't know), "wtw" (what's the word / what's up), "omms" (on my mama's soul), "smh" (shaking my head), "wrd2" (word to, I swear), entre otras.
6. WHEN el User completa todos los términos de un ejercicio de Reading, THE Progress_Service SHALL marcar el módulo como completado y otorgar XP al User.

---

### Requirement 5: Módulo Listening — The Cypher

**User Story:** Como estudiante, quiero escuchar fragmentos de audio de artistas reales del Drill y completar ejercicios de comprensión auditiva, para que pueda desarrollar mi oído para el acento y la cadencia del dialecto.

#### Acceptance Criteria

1. THE Drillingo SHALL reproducir fragmentos de audio de letras de artistas del Drill (incluyendo artistas como Kay Flock, DD Osama, Lil Jeff, King Von) dentro del módulo Listening.
2. WHEN el User inicia un ejercicio de Listening, THE Drillingo SHALL presentar el fragmento de audio junto con una transcripción parcial que contenga entre 2 y 5 espacios en blanco ("fill in the blanks").
3. WHEN el User completa los espacios en blanco y envía sus respuestas, THE Progress_Service SHALL evaluar cada respuesta, registrar el score y otorgar XP.
4. IF el User falla un espacio en blanco, THEN THE Drillingo SHALL mostrar la respuesta correcta con una explicación del doble sentido o significado contextual de la barra.
5. THE Drillingo SHALL incluir al menos una pregunta de comprensión semántica por fragmento que pregunte por el significado de una barra o el doble sentido de una expresión.
6. THE Content_Service SHALL etiquetar cada fragmento de audio con su `dialect_segment` (east_coast o midwest) para que el User identifique la región del artista.
7. THE Content_Service SHALL almacenar los archivos de audio de los fragmentos exclusivamente en el Object_Storage (AWS S3, Cloudinary o Supabase Storage) y persistir únicamente la Audio_URL resultante en la columna `audio_url` de la tabla `lessons`.
8. WHEN el Content_Service sirve un fragmento de audio, THE Content_Service SHALL devolver la Audio_URL al cliente para que este realice la solicitud de streaming directamente al Object_Storage, sin que el servidor de aplicación actúe como proxy del archivo binario.

---

### Requirement 6: Módulo Writing — Spitting Bars

**User Story:** Como estudiante, quiero traducir frases formales al dialecto Drill, para que pueda internalizar la gramática no estándar del AAVE y construir expresiones auténticas.

#### Acceptance Criteria

1. WHEN el User abre un ejercicio de Writing, THE Drillingo SHALL presentar una frase en inglés formal estándar y solicitar su traducción al dialecto Drill/AAVE.
2. THE Drillingo SHALL incluir ejercicios que cubran las siguientes estructuras gramaticales del AAVE: uso de "ain't" como negación, "finna" como marcador de futuro inmediato, "allat" como pronombre demostrativo enfático, doble negación, y omisión del verbo copulativo "to be".
3. WHEN el User envía una traducción, THE Progress_Service SHALL comparar la respuesta contra un conjunto de respuestas aceptadas y registrar el resultado.
4. IF la respuesta del User no coincide con ninguna respuesta aceptada, THEN THE Drillingo SHALL mostrar al menos una respuesta de referencia con una explicación de la estructura gramatical aplicada.
5. THE Drillingo SHALL aceptar variaciones ortográficas equivalentes como respuestas correctas (por ejemplo: "finna" y "fin to" se consideran equivalentes).
6. WHEN el User completa un ejercicio de Writing, THE Progress_Service SHALL otorgar XP y actualizar el contador de estructuras gramaticales dominadas del User.

---

### Requirement 7: Módulo Speaking — Live Report Sync

**User Story:** Como estudiante, quiero enviar un reporte JSON de mi sesión de práctica oral externa, para que el sistema registre mis métricas de fluidez y pronunciación y las refleje en mi dashboard.

#### Acceptance Criteria

1. THE Report_Parser SHALL exponer un endpoint HTTP POST que acepte un objeto JSON con los campos: `session_duration_seconds` (integer), `fluency_score` (integer 0–100), `pronunciation_score` (integer 0–100), y `notes` (string, opcional).
2. WHEN el Report_Parser recibe un Oral_Report válido, THE Report_Parser SHALL persistir el reporte completo en la tabla `oral_reports` incluyendo el `raw_json` original.
3. IF el JSON recibido no contiene los campos obligatorios `fluency_score` o `pronunciation_score`, THEN THE Report_Parser SHALL devolver un error HTTP 400 con un mensaje que indique el campo faltante.
4. IF el valor de `fluency_score` o `pronunciation_score` está fuera del rango 0–100, THEN THE Report_Parser SHALL devolver un error HTTP 422 con el mensaje "Score must be between 0 and 100".
5. WHEN el Report_Parser persiste un Oral_Report exitosamente, THE Progress_Service SHALL actualizar el promedio histórico de `fluency_score` y `pronunciation_score` del User en el Dashboard.
6. THE Report_Parser SHALL parsear el campo `raw_json` y extraer las métricas numéricas sin modificar el contenido original del JSON almacenado.
7. FOR ALL Oral_Reports válidos, parsear el JSON y luego serializarlo de vuelta SHALL producir un objeto semánticamente equivalente al original (propiedad round-trip).

---

### Requirement 8: Sistema de Racha (Streak Engine)

**User Story:** Como estudiante, quiero ver mi racha de días consecutivos estudiando, para que tenga motivación para mantener una práctica diaria constante.

#### Acceptance Criteria

1. WHEN el User completa al menos una lección en un día calendario, THE Streak_Engine SHALL incrementar el `current_streak` del User en 1.
2. WHEN el Streak_Engine incrementa el `current_streak` y este supera el `longest_streak` registrado, THE Streak_Engine SHALL actualizar el `longest_streak` con el nuevo valor.
3. IF el User no completa ninguna lección en un día calendario completo, THEN THE Streak_Engine SHALL reiniciar el `current_streak` a 0 al inicio del día siguiente.
4. THE Drillingo SHALL mostrar el `current_streak` del User con un ícono de fuego en la interfaz principal.
5. THE Streak_Engine SHALL usar la zona horaria enviada por el cliente en cada request de check-in para determinar el día calendario, no la zona horaria del servidor.
6. WHEN el User completa su primera lección del día, THE Streak_Engine SHALL actualizar el campo `last_activity_date` con la fecha actual en la zona horaria del cliente.
7. FOR ALL secuencias de actividad diaria, el `current_streak` al día N SHALL ser igual al número de días consecutivos con actividad terminando en el día N (propiedad invariante).
8. THE Drillingo SHALL almacenar todos los campos de timestamp relacionados con el Streak_Engine usando el tipo `TIMESTAMPTZ` (timestamp with time zone) en PostgreSQL.
9. IF el cliente envía su timezone en el header o payload del request de check-in, THEN THE Streak_Engine SHALL usar esa timezone para determinar el límite de medianoche del día calendario al evaluar y actualizar el `current_streak`.

---

### Requirement 9: Dashboard Visual y Métricas de Progreso

**User Story:** Como estudiante, quiero ver un dashboard con gráficas de mi evolución, para que pueda entender mi progreso hacia el nivel C1 y mantenerme motivado.

#### Acceptance Criteria

1. THE Dashboard SHALL mostrar una gráfica de barras con la evolución del nivel del User (B1 → B2 → C1) a lo largo del tiempo, usando datos de `lesson_progress`.
2. THE Dashboard SHALL mostrar una gráfica de radar con las dimensiones: Reading, Listening, Writing, Speaking, y Vocabulary, con puntuaciones de 0 a 100 por dimensión.
3. THE Dashboard SHALL mostrar el número total de Vocabulary_Items con `mastered = true` para el User.
4. THE Dashboard SHALL mostrar la evolución histórica del `fluency_score` y `pronunciation_score` del User como una gráfica de línea con los últimos 30 reportes orales.
5. WHEN el User accede al Dashboard, THE Progress_Service SHALL calcular y devolver todas las métricas en una sola respuesta de API con tiempo de respuesta menor a 500ms.
6. THE Dashboard SHALL mostrar el `current_streak` y el `longest_streak` del User de forma prominente.
7. THE Drillingo SHALL renderizar el Dashboard en modo oscuro obligatorio con colores de acento rojo neón (#FF0033), blanco (#FFFFFF) y gris asfalto (#1A1A1A).

---

### Requirement 10: Gamificación y Progresión de Nivel

**User Story:** Como estudiante, quiero ganar XP y avanzar de nivel automáticamente, para que sienta progresión tangible en mi aprendizaje.

#### Acceptance Criteria

1. THE Progress_Service SHALL otorgar XP al User al completar cada módulo: 10 XP por Reading, 15 XP por Listening, 20 XP por Writing, 25 XP por Speaking.
2. WHEN el User acumula suficiente XP para avanzar de nivel, THE Progress_Service SHALL actualizar el `level_band` del User al siguiente nivel (B1 → B2 → C1).
3. THE Progress_Service SHALL definir los umbrales de XP para avance de nivel: 500 XP para pasar de B1 a B2, y 1500 XP adicionales para pasar de B2 a C1.
4. WHEN el `level_band` del User cambia, THE Content_Service SHALL comenzar a servir lecciones del nuevo nivel en la siguiente sesión.
5. THE Drillingo SHALL mostrar una notificación visual al User cuando avance de nivel.
6. THE Progress_Service SHALL registrar la fecha de cada cambio de `level_band` para su visualización en el Dashboard.

---

### Requirement 11: Gestión de Vocabulario Dominado

**User Story:** Como estudiante, quiero marcar palabras de slang como dominadas y ver mi colección, para que pueda rastrear mi vocabulario activo del dialecto Drill.

#### Acceptance Criteria

1. WHEN el User responde correctamente a un Vocabulary_Item en tres ejercicios distintos, THE Progress_Service SHALL marcar automáticamente ese ítem como `mastered = true` en la tabla `user_vocabulary`.
2. THE Drillingo SHALL mostrar al User una sección de "Vocabulario Dominado" con todos sus Vocabulary_Items donde `mastered = true`.
3. WHEN el User accede a un Vocabulary_Item dominado, THE Drillingo SHALL mostrar el término, su definición, su `dialect_segment`, y al menos un ejemplo de uso en contexto.
4. THE Progress_Service SHALL actualizar el campo `last_reviewed_at` cada vez que el User interactúa con un Vocabulary_Item en cualquier módulo.
5. THE Drillingo SHALL permitir al User filtrar su vocabulario dominado por `dialect_segment` (east_coast o midwest).

---

### Requirement 12: Interfaz de Usuario — Estética Streetwear Dark Mode

**User Story:** Como usuario, quiero que la interfaz tenga una estética streetwear agresiva en modo oscuro, para que la experiencia visual sea coherente con la cultura Drill que estoy aprendiendo.

#### Acceptance Criteria

1. THE Drillingo SHALL aplicar modo oscuro obligatorio en todas las vistas, con fondo principal en gris asfalto (#1A1A1A) y superficies secundarias en (#242424).
2. THE Drillingo SHALL usar rojo neón (#FF0033) como color de acento primario para botones de acción principal, indicadores de progreso activo y elementos de énfasis.
3. THE Drillingo SHALL usar tipografía Roboto Black o Impact para todos los títulos y encabezados de sección.
4. THE Drillingo SHALL usar botones con altura mínima de 48px y texto en mayúsculas para todas las acciones primarias.
5. THE Drillingo SHALL ser completamente funcional en resoluciones de pantalla desde 375px de ancho (móvil) hasta 1440px (escritorio).
6. THE Drillingo SHALL cumplir con un ratio de contraste mínimo de 4.5:1 entre texto y fondo en todos los componentes de interfaz, conforme a WCAG 2.1 nivel AA.
