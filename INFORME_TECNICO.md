# Informe Técnico — Soccer Predictor

**Proyecto:** Agente híbrido de predicción deportiva  
**Integrantes:**
- Yeison Rodriguez
- Daniela Londoño
- Isabella Huila
- Danna Lopez
**Curso:** IA2 — Semestre 8  
**Versión del documento:** 1.0  
**Fecha:** Junio 2026

---

## 1. Resumen ejecutivo

Soccer Predictor es un sistema inteligente que predice resultados de partidos de fútbol y ofrece análisis deportivo conversacional. Combina tres paradigmas de inteligencia artificial:

1. **Machine Learning** — modelo estadístico entrenado con más de 37.000 partidos históricos.
2. **Large Language Model (LLM)** — razonamiento contextual y generación de explicaciones vía Groq (Llama 3.3) y LangChain.
3. **RAG (Retrieval-Augmented Generation)** — inyección de conocimiento táctico en el prompt del LLM.

La aplicación expone una API REST (FastAPI) consumida por un frontend en React. El usuario puede ejecutar predicciones guiadas (liga + equipos) o mantener un chat libre con el analista, en inglés o español.

---

## 2. Objetivos del sistema

| Objetivo | Descripción |
|----------|-------------|
| Predicción 1X2 | Estimar probabilidades de victoria local, empate y victoria visitante |
| Marcador | Proponer un resultado numérico coherente con las probabilidades |
| Explicabilidad | Entregar factores clave y análisis en lenguaje natural |
| Datos reales | Integrar APIs deportivas y archivo histórico |
| Interacción dual | Separar predicción estructurada de conversación abierta |
| Bilingüismo | Respuestas y UI en español e inglés |

---

## 3. Justificación de la arquitectura

La predicción deportiva requiere señales numéricas (tabla, forma, goles) y contexto cualitativo (lesiones, clima, táctica). Ningún enfoque aislado cubre ambos:

- Un **LLM solo** tiende a opinar sin calibración estadística.
- Un **modelo ML solo** no explica bien ni integra matices cualitativos.
- **APIs crudas** no sintetizan ni conversan con el usuario.

La arquitectura híbrida asigna responsabilidades claras: el ML ancla las probabilidades; el LLM ajusta y explica; el RAG aporta conocimiento táctico; las APIs alimentan datos en tiempo real.

---

## 4. Arquitectura general

```text
┌──────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                       │
│         React 19 + Vite + Tailwind CSS (frontend/)            │
│    Pestaña Predicción  |  Pestaña Chat  |  Historial         │
└────────────────────────────┬─────────────────────────────────┘
                             │ HTTP REST (puerto 8000)
┌────────────────────────────▼─────────────────────────────────┐
│                    CAPA DE API (FastAPI)                      │
│   GET /leagues  GET /teams  POST /predict  POST /chat         │
│   GET /sessions  GET /sessions/{id}/messages                  │
└─────┬──────────────────┬──────────────────┬──────────────────┘
      │                  │                  │
┌─────▼─────────┐ ┌──────▼──────┐ ┌─────────▼─────────┐
│ Agentes IA    │ │ Clientes    │ │ Persistencia      │
│ Prediction    │ │ API externa │ │ SQLite (chat)     │
│ Agent         │ │ Football    │ │ DataSetPartidos   │
│ SoccerAnalyst │ │ SoccerData  │ │ .txt (histórico)  │
│ MatchPredictor│ │             │ │ models/*.joblib   │
└───────┬───────┘ └─────────────┘ └───────────────────┘
        │
┌───────▼───────┐
│  Groq API     │
│  Llama 3.3    │
└───────────────┘
```

### 4.1 Principios de diseño

- **Separación de capas:** frontend, API, agentes, datos y persistencia desacoplados.
- **Tolerancia a fallos parciales:** las llamadas a APIs externas usan `try/except`; la predicción continúa con datos parciales.
- **Cache de modelo ML:** el entrenamiento se ejecuta una vez; ejecuciones posteriores cargan `joblib`.
- **Salida estructurada:** Pydantic valida la respuesta del LLM para integración con la UI.

---

## 5. Stack tecnológico

### 5.1 Backend

| Componente | Tecnología | Versión / notas |
|------------|------------|-----------------|
| Runtime | Python | 3.10+ |
| API web | FastAPI + Uvicorn | — |
| Validación | Pydantic, pydantic-settings | — |
| ML | scikit-learn (GradientBoostingClassifier) | ≥ 1.4 |
| Persistencia ML | joblib | — |
| LLM | LangChain + langchain-groq | ≥ 0.3 |
| HTTP cliente | requests | — |
| Base de datos | SQLite (sqlite3) | chat_history.db |

### 5.2 Frontend

| Componente | Tecnología |
|------------|------------|
| Framework | React 19 |
| Build | Vite 8 |
| Estilos | Tailwind CSS 4 |
| HTTP | Axios |
| Iconos | lucide-react |
| Markdown | react-markdown |
| Lenguaje | TypeScript 6 |

### 5.3 Servicios externos

| Servicio | Uso |
|----------|-----|
| [Groq](https://console.groq.com/) | Inferencia LLM (Llama 3.3 70B) |
| [Football-Data.org](https://www.football-data.org/) | Ligas, equipos, standings, forma, H2H |
| [SoccerDataAPI](https://api.soccerdataapi.com/) | Lesiones, clima, previews (opcional) |

---

## 6. Fuentes de datos

### 6.1 Dataset histórico (`DataSetPartidos.txt`)

- **Ubicación:** `backend/data/DataSetPartidos.txt`
- **Volumen:** ~37.149 registros
- **Formato:** texto delimitado por `::`
- **Campos principales:** temporada, división, equipos local/visitante, goles, fecha
- **Uso:**
  1. Entrenamiento del modelo Gradient Boosting al arrancar el backend.
  2. Consulta H2H histórico (`HistoricalMatchRepository.get_h2h`) en cada predicción.

### 6.2 Football-Data.org (tiempo real)

- Competiciones y equipos filtrados por tier gratuito.
- Standings, últimos 5 partidos, H2H entre equipos.
- Rate limit: ~10 peticiones/minuto (intervalo de 6 s en el cliente).

### 6.3 SoccerDataAPI (complementario)

- Transferencias, detalles de partido, preview con clima y predicción propia.
- Búsqueda de equipos/partidos mediante `livescores` (puede devolver datos parciales).
- Soporta datos mock locales en `backend/data/SoccerDataAPIex/` para desarrollo.

### 6.4 SQLite (`chat_history.db`)

- Tablas: `sessions`, `messages`
- Almacena historial de conversaciones y predicciones (`prediction_data` en JSON).

---

## 7. Pipeline de predicción

### 7.1 Flujo secuencial

```text
Usuario selecciona liga + equipos
        │
        ▼
main.py → recopila datos (Football-Data, SoccerData, H2H histórico)
        │
        ▼
MatchPredictor.format_match_context() → reporte textual
        │
        ├──► PredictionModel.predict() → probabilidades ML
        │
        ├──► Retriever.retrieve() → fragmentos RAG
        │
        └──► SoccerAnalyst.predict_structured() → ajuste LLM (Pydantic)
        │
        ▼
PredictionAgent._blend() → 65% ML + 35% LLM (configurable)
        │
        ▼
Respuesta: narrative + structured + ml_result → SQLite + frontend
```

### 7.2 Orquestador (`PredictionAgent`)

Archivo: `backend/src/agents/prediction_agent.py`

Coordina el modelo ML, el retriever RAG, el formateador de contexto y el analista LLM. Genera la narrativa final y los metadatos localizados (`confidence_label`, `outcome_label`, idioma).

### 7.3 Formateador de contexto (`MatchPredictor`)

Archivo: `backend/src/agents/match_predictor.py`

Transforma datos crudos de APIs en un informe textual para el LLM:

- Standings y métricas de forma (puntos/partido, goles, win rate).
- H2H global y archivo histórico local.
- Lesiones, clima, transferencias (si disponibles).

### 7.4 Analista LLM (`SoccerAnalyst`)

Archivo: `backend/src/agents/soccer_analyst.py`

- Cliente: `ChatGroq` (LangChain).
- Modelo por defecto: `llama-3.3-70b-versatile`.
- Métodos:
  - `analyze()` — chat conversacional.
  - `predict_structured()` — salida tipada (`MatchPredictionResult`).
- Reglas de idioma en `backend/src/utils/i18n.py`.

---

## 8. Modelo de Machine Learning

### 8.1 Algoritmo

- **Clasificador:** `GradientBoostingClassifier` (scikit-learn)
- **Hiperparámetros:** `n_estimators=120`, `max_depth=4`, `learning_rate=0.08`
- **Clases:** `home_win` (0), `draw` (1), `away_win` (2)
- **Escalado:** `StandardScaler` previo a inferencia

### 8.2 Entrenamiento

Archivo: `backend/src/models/prediction_model.py`

1. `HistoricalMatchRepository` carga el `.txt`.
2. `build_historical_training_rows()` genera features acumulativas por equipo antes de cada partido.
3. Split hold-out: 85% train / 15% test (`stratify=y`).
4. Métrica registrada en log: **accuracy en hold-out** (~0.51 en entrenamientos de referencia).
5. Artefactos guardados en `backend/data/models/`.

### 8.3 Features de entrenamiento (13 dimensiones)

| # | Feature |
|---|---------|
| 0 | Ventaja local (1.0) |
| 1–2 | Ratio victorias local / visitante |
| 3–4 | Ratio empates local / visitante |
| 5–8 | Goles a favor y en contra / partido |
| 9–10 | Victorias como local / como visitante |
| 11–12 | Diferencia de goles normalizada |

### 8.4 Features en vivo (26 dimensiones)

Archivo: `backend/src/models/feature_engineer.py` — función `extract_live_features()`

Incluye posición, puntos, diferencia de goles, forma reciente, H2H de API y H2H del archivo histórico.

### 8.5 Mapeo en vivo → entrenamiento

El modelo fue entrenado con 13 features; en producción se extraen 26. La función `_map_live_to_training_features()` proyecta el vector en vivo a 13 dimensiones mediante correspondencias heurísticas (win rate, goles de forma, goal difference normalizado, etc.).

**Limitación:** este mapeo es aproximado. La accuracy de hold-out refleja el dataset histórico español, no necesariamente el rendimiento en ligas internacionales en vivo.

### 8.6 Blend híbrido

```
P_final = ML_BLEND_WEIGHT × P_ml + (1 - ML_BLEND_WEIGHT) × P_llm
```

- Variable de entorno: `ML_BLEND_WEIGHT` (default: `0.65`).
- Las probabilidades se renormalizan para sumar ~1.0.

---

## 9. Sistema RAG

### 9.1 Base de conocimiento

Archivo: `backend/src/rag/knowledge_base.py`

10 documentos estáticos sobre: ventaja local, forma, lesiones, H2H, probabilidad de empate, regresión a la media, congestión de calendario, clima, lucha por el descenso y calibración de predicciones.

### 9.2 Retriever

Archivo: `backend/src/rag/retriever.py`

- Método: búsqueda por keywords (Groq no expone API de embeddings en este proyecto).
- Recupera los `k=4` fragmentos más relevantes según la consulta del partido.
- Fallback: devuelve documentos por defecto si no hay coincidencias.

---

## 10. API REST

### 10.1 Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/leagues` | Competiciones disponibles (filtradas) |
| `GET` | `/teams/{competition_id}` | Equipos de una liga (código, ej. `PD`) |
| `POST` | `/predict` | Pipeline completo de predicción |
| `POST` | `/chat` | Conversación con el analista |
| `GET` | `/sessions` | Listado de sesiones |
| `GET` | `/sessions/{id}/messages` | Mensajes de una sesión |
| `POST` | `/sessions` | Crear sesión |

### 10.2 Cuerpo de `POST /predict`

```json
{
  "competition_id": "PD",
  "team1_id": 86,
  "team2_id": 81,
  "session_id": null,
  "language": "es"
}
```

### 10.3 Respuesta de `POST /predict`

```json
{
  "session_id": 1,
  "prediction": "## Predicción: ...",
  "structured": {
    "outcome": "home_win",
    "home_win_probability": 0.48,
    "draw_probability": 0.27,
    "away_win_probability": 0.25,
    "predicted_score": "2-1",
    "confidence": "medium",
    "confidence_label": "Media",
    "outcome_label": "Victoria de ...",
    "key_factors": ["...", "..."],
    "rationale": "...",
    "language": "es",
    "home_team": "...",
    "away_team": "..."
  },
  "ml_result": {
    "probabilities": { "home_win": 0.45, "draw": 0.28, "away_win": 0.27 },
    "predicted_outcome": "home_win",
    "confidence": "medium",
    "source": "gradient_boosting"
  }
}
```

### 10.4 CORS

Configurado con `allow_origins=["*"]` para desarrollo local.

---

## 11. Frontend

### 11.1 Estructura de componentes

| Archivo | Responsabilidad |
|---------|-----------------|
| `App.tsx` | Estado global, navegación, llamadas API |
| `components/PredictPanel.tsx` | UI exclusiva de predicción (selectores + resultado) |
| `components/ChatPanel.tsx` | Conversación y entrada de texto |
| `components/LeagueSelect.tsx` | Selector de liga con emblema y metadatos API |
| `components/TeamPicker.tsx` | Selección local/visitante con escudos |
| `components/PredictionCard.tsx` | Tarjeta visual de probabilidades y análisis |
| `components/MarkdownContent.tsx` | Renderizado de respuestas Markdown en chat |
| `api.ts` | Normalización de respuestas `/leagues` y `/teams` |
| `i18n.ts` | Cadenas ES/EN |

### 11.2 Modos de interacción

| Aspecto | Pestaña Predicción | Pestaña Chat |
|---------|-------------------|--------------|
| Selectores liga/equipos | Sí | No |
| Pipeline ML + APIs | Sí | No |
| Solo LLM | No | Sí |
| Salida principal | `PredictionCard` | Markdown / texto |
| Color temático | Verde (emerald) | Azul (sky) |

### 11.3 Normalización de datos API

`normalizeLeagues()` y `normalizeTeams()` garantizan que los desplegables reflejen exactamente la respuesta del backend, con orden alfabético y campos `emblem`, `crest`, `areaName`, `tla`.

---

## 12. Configuración y despliegue

### 12.1 Variables de entorno (`backend/.env`)

| Variable | Descripción | Obligatoria |
|----------|-------------|-------------|
| `GROQ_API_KEY` | Clave API de Groq | Sí |
| `FOOTBALL_DATA_API_KEY` | Clave Football-Data.org | Sí |
| `SOCCER_DATA_API_KEY` | Clave SoccerDataAPI | No |
| `GROQ_MODEL` | Modelo LLM | No (default: llama-3.3-70b-versatile) |
| `ML_BLEND_WEIGHT` | Peso del ML en blend | No (default: 0.65) |

### 12.2 Arranque

```bash
# Backend (puerto 8000)
cd backend && python main.py

# Frontend (puerto 5173)
cd frontend && npm run dev
```

### 12.3 Primer arranque

Si no existen artefactos en `backend/data/models/`, el backend entrena el modelo (~1–2 minutos). Los logs muestran:

```text
Trained ML model on 37147 matches. Hold-out accuracy: 0.514
```

---

## 13. Evaluación y métricas

| Métrica | Valor / descripción |
|---------|---------------------|
| Accuracy hold-out (ML) | ~51% (registrado en log al entrenar) |
| Baseline aleatoria 1X2 | ~33% |
| Partidos de entrenamiento | ~37.147 |
| Split test | 15% estratificado |
| Confianza UI | `low` / `medium` / `high` según probabilidad máxima del ML |

**Nota:** no existe endpoint ni pantalla que exponga la accuracy en tiempo de ejecución. Solo se registra durante el entrenamiento inicial o al borrar el cache de modelos.

---

## 14. Internacionalización

- Backend: `backend/src/utils/i18n.py` — reglas de idioma en prompts, etiquetas localizadas, mensajes de sistema.
- Frontend: `frontend/src/i18n.ts` — cadenas de UI.
- Parámetro `language` (`en` | `es`) en `/predict` y `/chat`.

---

## 15. Estructura de directorios

```text
soccer-predictor/
├── INFORME_TECNICO.md          # Este documento
├── README.md                    # Guía de uso
├── .gitignore
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── data/
│   │   ├── DataSetPartidos.txt
│   │   ├── models/              # Generado (gitignored)
│   │   └── SoccerDataAPIex/   # Mocks de desarrollo
│   └── src/
│       ├── agents/              # prediction_agent, soccer_analyst, match_predictor
│       ├── api/                 # football_data, soccer_data
│       ├── config/              # settings, prompts
│       ├── database/            # connection, repository
│       ├── models/              # prediction_model, feature_engineer, schemas
│       ├── rag/                 # knowledge_base, retriever
│       └── utils/               # i18n, logger, validators
└── frontend/
    └── src/
        ├── App.tsx
        ├── api.ts
        ├── i18n.ts
        ├── types.ts
        └── components/
```

---

## 16. Componentes auxiliares (no integrados en flujo principal)

| Módulo | Estado |
|--------|--------|
| `sql_agent.py` | Implementado con Groq; no expuesto en API |
| `validators.py` | Definido; no cableado en rutas |

---

## 17. Limitaciones conocidas

1. **Mapeo de features:** proyección heurística 26→13 entre entorno en vivo y entrenamiento histórico.
2. **Dataset de entrenamiento:** ligas españolas; predicción en vivo puede ser otras competiciones.
3. **Rate limits:** Football-Data.org limita la velocidad de predicción (varias llamadas secuenciales).
4. **SoccerDataAPI:** búsqueda de partidos frágil; a menudo datos parciales.
5. **H2H histórico:** matching por nombres de equipo con heurísticas; no todos los equipos coinciden.
6. **RAG:** búsqueda por keywords, no embeddings vectoriales.
7. **Métricas:** sin backtesting automático ni panel de evaluación en UI.
8. **LLM:** dependencia de cuota y disponibilidad de Groq.

---

## 18. Trabajo futuro recomendado

- Reentrenar el ML con el vector completo de 26 features en vivo.
- Añadir endpoint `GET /model/metrics` y mostrar accuracy en la UI.
- Implementar backtesting por temporada y métricas log-loss / Brier score.
- Activar embeddings reales en RAG (cuando haya API disponible).
- Paralelizar llamadas a APIs externas (`asyncio` / `httpx`).
- Normalizar nombres de equipos con tabla de mapeo cross-API.
- Desplegar con Docker y variables de entorno por entorno (dev/prod).

---

## 19. Conclusiones

Soccer Predictor implementa un **agente híbrido** que combina aprendizaje automático, modelos de lenguaje y recuperación de conocimiento para abordar un problema de predicción deportiva de forma explicable e interactiva. La separación entre predicción guiada y chat libre, junto con la arquitectura en capas (React → FastAPI → agentes → datos), facilita el mantenimiento, la demostración académica y la evolución futura del sistema.

El sistema demuestra competencias centrales del curso IA2: integración de datos, modelado estadístico, orquestación de LLM con LangChain, diseño de API REST y desarrollo de interfaz de usuario con visualización estructurada de resultados.

---

*Documento generado como informe técnico del proyecto Soccer Predictor — IA2, Semestre 8.*
