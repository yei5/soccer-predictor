# Soccer Predictor — Agente Híbrido de Predicción Deportiva

Sistema inteligente que combina **Machine Learning**, **LangChain** y **Groq (Llama 3.3)** para predecir resultados de partidos de fútbol y ofrecer análisis deportivo interactivo.

El frontend está construido en **React + Vite + Tailwind CSS**. El backend expone una **API REST con FastAPI**.

## Características principales

- **Predicción híbrida**: modelo estadístico (Gradient Boosting) + refinamiento con LLM vía LangChain.
- **Salida estructurada**: probabilidades 1X2, marcador, confianza y factores clave en formato JSON.
- **RAG táctico**: base de conocimiento con búsqueda por keywords para inyectar contexto relevante.
- **Datos en tiempo real**: integración con [Football-Data.org](https://www.football-data.org/) y [SoccerDataAPI](https://api.soccerdataapi.com/).
- **Archivo histórico**: más de 37,000 partidos españoles para entrenar el modelo ML.
- **Interfaz bilingüe**: inglés y español con historial de sesiones.

## Interfaz: listas desplegables vs chat

La aplicación ofrece **dos modos de interacción** con propósitos distintos:

### Listas desplegables (panel de Predicción)

Sirven para **generar una predicción concreta** de un partido:

1. **Liga** — qué competición analizar (La Liga, Premier League, etc.).
2. **Equipo local** — quién juega en casa.
3. **Equipo visitante** — quién juega fuera.

Al pulsar **Analizar partido**, el backend ejecuta el pipeline completo:

- Consulta Football-Data.org y SoccerDataAPI.
- Ejecuta el modelo ML (Gradient Boosting).
- Enriquece el contexto con RAG táctico.
- Refina probabilidades con Groq vía LangChain.
- Devuelve probabilidades, marcador, factores clave y análisis.

Es un flujo **guiado y estructurado**: eliges equipos y obtienes una predicción completa con datos reales.

### Chat (pestaña Chat + barra inferior)

Sirve para **conversar libremente** con el analista deportivo:

- Preguntas como "¿Qué ligas hay disponibles?", "¿Cómo va el Real Madrid?" o "¿Qué es el gegenpressing?".
- No requiere seleccionar liga ni equipos.
- El LLM responde en el idioma seleccionado (inglés o español).
- **No** ejecuta automáticamente el pipeline de predicción (APIs en vivo + ML + RAG).

Es un flujo **abierto**: escribes lo que quieras y recibes una respuesta conversacional basada solo en el modelo de lenguaje.

### Comparación rápida

| | Listas desplegables | Chat |
|---|---------------------|------|
| Propósito | Predecir un partido específico | Preguntar, explorar, charlar |
| Entrada | Liga + 2 equipos | Texto libre |
| Salida | Tarjeta con probabilidades, marcador y factores | Mensaje de texto (renderizado como Markdown) |
| Usa ML + APIs externas | Sí, siempre | No |
| Endpoint backend | `POST /predict` | `POST /chat` |
| Cuándo usarlo | "¿Quién gana Barcelona vs Real Madrid?" | "¿Qué equipos hay en la Serie A?" |

### Cómo se conectan

Si analizas un partido con las listas, el resultado **también aparece en el chat** de esa sesión como tarjeta de predicción. El historial de la barra lateral guarda todas las sesiones (predicciones y conversaciones).

## Arquitectura

```text
┌─────────────────────────────────────────────────────────┐
│  Frontend — React + Vite + Tailwind (frontend/)         │
└────────────────────────┬────────────────────────────────┘
                         │ REST (localhost:8000)
┌────────────────────────▼────────────────────────────────┐
│  API — FastAPI (backend/main.py)                        │
│  /leagues  /teams  /predict  /chat  /sessions           │
└──┬──────────────┬──────────────┬────────────────────────┘
   │              │              │
┌──▼──────────┐ ┌─▼────────────┐ ┌▼──────────────────────┐
│ Prediction  │ │ API Clients  │ │ Persistencia          │
│ Agent       │ │ FootballData │ │ SQLite (chat)         │
│ ML + RAG    │ │ SoccerData   │ │ DataSetPartidos.txt   │
│ + LangChain │ │              │ │                       │
└──────┬──────┘ └──────────────┘ └───────────────────────┘
       │
┌──────▼──────┐
│ Groq API    │
│ Llama 3.3   │
└─────────────┘
```

### Flujo de predicción

1. El usuario selecciona liga y equipos en el frontend React.
2. El backend recopila datos: standings, forma reciente, H2H, lesiones, clima y archivo histórico.
3. El **Feature Engineer** extrae métricas numéricas (puntos/partido, goles, win rate).
4. El **modelo ML** (Gradient Boosting) genera probabilidades base entrenadas con 37k partidos.
5. El **Retriever RAG** busca conocimiento táctico relevante (ventaja local, lesiones, forma, etc.).
6. **LangChain + Groq** refinan las probabilidades con salida estructurada (Pydantic).
7. Se combinan ambas señales (65% ML + 35% LLM por defecto) y se devuelve el resultado.

## Estructura del proyecto

```text
soccer-predictor/
├── backend/
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── requirements.txt           # Dependencias Python
│   ├── .env.example               # Variables de entorno
│   ├── data/
│   │   ├── DataSetPartidos.txt    # Dataset histórico (~37k partidos)
│   │   └── models/                # Modelo ML cacheado (generado al arrancar)
│   └── src/
│       ├── agents/
│       │   ├── prediction_agent.py  # Orquestador ML + RAG + LLM
│       │   ├── soccer_analyst.py    # LangChain + Groq
│       │   └── match_predictor.py   # Formateo de contexto
│       ├── api/                     # Clientes Football-Data y SoccerDataAPI
│       ├── config/                  # Settings y prompts
│       ├── database/                # SQLite y repositorio histórico
│       ├── models/
│       │   ├── prediction_model.py  # Gradient Boosting
│       │   ├── feature_engineer.py  # Extracción de features
│       │   └── schemas.py           # Modelos Pydantic de salida
│       └── rag/                     # Knowledge base + retriever
└── frontend/
    ├── src/App.tsx                  # UI principal (React)
    └── package.json
```

## Requisitos previos

- **Python 3.10+**
- **Node.js 18+**
- Claves de API:
  - [Groq](https://console.groq.com/) (gratis, sin tarjeta)
  - [Football-Data.org](https://www.football-data.org/)
  - [SoccerDataAPI](https://api.soccerdataapi.com/) (opcional)

## Instalación

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
cp .env.example .env         # Editar con tus API keys
```

### Frontend

```bash
cd frontend
npm install
```

## Configuración (`.env`)

```env
FOOTBALL_DATA_API_KEY=tu_clave_football_data
GROQ_API_KEY=tu_clave_groq
SOCCER_DATA_API_KEY=tu_clave_soccer_data   # opcional
GROQ_MODEL=llama-3.3-70b-versatile
ML_BLEND_WEIGHT=0.65
```

| Variable | Descripción |
|----------|-------------|
| `GROQ_MODEL` | Modelo de Groq (`llama-3.3-70b-versatile` o `llama-3.1-8b-instant`) |
| `ML_BLEND_WEIGHT` | Peso del modelo ML en el blend final (0.0–1.0) |

## Ejecución

**Terminal 1 — Backend:**

```bash
cd backend
python main.py
# o: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Abre `http://localhost:5173` en el navegador.

> El primer arranque del backend entrena el modelo ML (~1–2 min). Las ejecuciones siguientes cargan el modelo desde `backend/data/models/`.

## API endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/leagues` | Ligas disponibles |
| `GET` | `/teams/{competition_id}` | Equipos de una liga |
| `POST` | `/predict` | Predicción híbrida ML + LLM |
| `POST` | `/chat` | Chat con el analista |
| `GET` | `/sessions` | Historial de sesiones |
| `GET` | `/sessions/{id}/messages` | Mensajes de una sesión |

### Ejemplo de respuesta `/predict`

```json
{
  "session_id": 1,
  "prediction": "## Predicción: Real Madrid vs Barcelona\n...",
  "structured": {
    "outcome": "home_win",
    "home_win_probability": 0.48,
    "draw_probability": 0.27,
    "away_win_probability": 0.25,
    "predicted_score": "2-1",
    "confidence": "medium",
    "key_factors": ["...", "..."],
    "rationale": "..."
  },
  "ml_result": {
    "probabilities": { "home_win": 0.45, "draw": 0.28, "away_win": 0.27 },
    "source": "gradient_boosting"
  }
}
```

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Frontend | React 19, Vite, Tailwind CSS, Axios, react-markdown |
| API | FastAPI, Uvicorn |
| ML | scikit-learn (Gradient Boosting), joblib |
| IA / LLM | LangChain, langchain-groq, Llama 3.3 |
| RAG | Knowledge base + keyword retriever |
| Datos | SQLite, Football-Data.org, SoccerDataAPI |

---

*Proyecto académico — IA2, Semestre 8*
