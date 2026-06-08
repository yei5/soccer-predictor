import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from src.api.football_data import FootballDataClient
from src.api.soccer_data import SoccerDataClient
from src.agents.soccer_analyst import SoccerAnalyst
from src.agents.prediction_agent import PredictionAgent
from src.database.repository import ChatRepository, HistoricalMatchRepository
from src.models.prediction_model import PredictionModel
from src.utils.logger import logger
from src.utils.i18n import normalize_language, t

app = FastAPI(title="Soccer Prediction Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    api_client = FootballDataClient()
    soccer_data_api = SoccerDataClient()
    analyst = SoccerAnalyst()
    chat_repo = ChatRepository()
    historical_repo = HistoricalMatchRepository()
    ml_model = PredictionModel(historical_matches=historical_repo.matches)
    prediction_agent = PredictionAgent(analyst=analyst, ml_model=ml_model)
    logger.info("Successfully initialized all components (Groq + LangChain + ML pipeline).")
except Exception as e:
    logger.error(f"Initialization failed: {e}")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    language: str = "en"

class PredictionRequest(BaseModel):
    competition_id: str
    team1_id: int
    team2_id: int
    session_id: Optional[int] = None
    language: str = "en"

@app.get("/sessions")
async def get_sessions():
    return chat_repo.get_sessions()

@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: int):
    if not chat_repo.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return chat_repo.get_messages(session_id)

@app.post("/sessions")
async def create_session(title: str = "New Analysis"):
    session_id = chat_repo.create_session(title)
    return {"session_id": session_id}

@app.get("/leagues")
async def get_leagues():
    try:
        leagues = api_client.get_competitions()
        free_codes = ['PL', 'PD', 'BL1', 'SA', 'FL1', 'ELC', 'PPL', 'DED', 'BSA', 'WC', 'EC']
        filtered = [l for l in leagues if l['code'] in free_codes or l.get('plan') == 'TIER_ONE']
        return filtered
    except Exception as e:
        logger.error(f"Error fetching leagues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{competition_id}")
async def get_teams(competition_id: str):
    try:
        data = api_client.get_teams(competition_id)
        return data
    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id
        if session_id and not chat_repo.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        if not session_id:
            session_id = chat_repo.create_session(t("chat_session_title", request.language))

        chat_repo.add_message(session_id, "user", request.message)

        leagues = api_client.get_competitions()
        available_leagues = ", ".join([
            f"{l['name']} ({l['code']})" for l in leagues
            if l.get('plan') == 'TIER_ONE' or l['code'] in ['PL', 'PD', 'BL1', 'SA', 'FL1']
        ])

        system_context = f"Available Leagues for analysis: {available_leagues}"
        response = analyst.analyze(request.message, context=system_context, language=request.language)

        chat_repo.add_message(session_id, "assistant", response)

        return {"session_id": session_id, "response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        session_id = request.session_id
        if session_id and not chat_repo.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        if not session_id:
            session_id = chat_repo.create_session()

        teams_data = api_client.get_teams(request.competition_id)
        team1_basic = next((t for t in teams_data if t['id'] == request.team1_id), None)
        team2_basic = next((t for t in teams_data if t['id'] == request.team2_id), None)

        lang = normalize_language(request.language)

        if not team1_basic or not team2_basic:
            msg = t("teams_not_found", lang)
            chat_repo.add_message(session_id, "assistant", msg)
            return {"session_id": session_id, "prediction": msg}

        chat_repo.update_session_title(session_id, f"{team1_basic['name']} vs {team2_basic['name']}")

        user_content = t(
            "predict_user",
            lang,
            home=team1_basic["name"],
            away=team2_basic["name"],
        )
        chat_repo.add_message(session_id, "user", user_content)

        standings = []
        try:
            standings = api_client.get_standings(request.competition_id)
        except Exception:
            pass

        team1_info = team1_basic
        try:
            team1_info = api_client.get_global_team_info(request.team1_id)
        except Exception:
            pass

        team2_info = team2_basic
        try:
            team2_info = api_client.get_global_team_info(request.team2_id)
        except Exception:
            pass

        team1_recent = []
        try:
            team1_recent = api_client.get_team_matches(request.team1_id)
        except Exception:
            pass

        team2_recent = []
        try:
            team2_recent = api_client.get_team_matches(request.team2_id)
        except Exception:
            pass

        h2h = {"matches": []}
        try:
            h2h = api_client.get_head_to_head(request.team1_id, request.team2_id)
        except Exception:
            pass

        deep_h2h = historical_repo.get_h2h(team1_basic['name'], team2_basic['name'])

        soccer_data_details = {}
        soccer_data_preview = {}
        try:
            sd_t1_id = soccer_data_api.find_team_id(team1_basic['name'])
            sd_t2_id = soccer_data_api.find_team_id(team2_basic['name'])
            if sd_t1_id:
                soccer_data_details['team1_transfers'] = soccer_data_api.get_transfers(sd_t1_id)
            if sd_t2_id:
                soccer_data_details['team2_transfers'] = soccer_data_api.get_transfers(sd_t2_id)
            sd_match_id = soccer_data_api.find_match_id(team1_basic['name'], team2_basic['name'])
            if sd_match_id:
                soccer_data_details.update(soccer_data_api.get_match_details(sd_match_id))
                soccer_data_preview = soccer_data_api.get_match_preview(sd_match_id)
        except Exception:
            pass

        result = prediction_agent.predict(
            team1=team1_basic,
            team2=team2_basic,
            standings=standings,
            h2h=h2h,
            team1_recent=team1_recent,
            team2_recent=team2_recent,
            team1_info=team1_info,
            team2_info=team2_info,
            deep_h2h=deep_h2h,
            soccer_data_details=soccer_data_details,
            soccer_data_preview=soccer_data_preview,
            language=lang,
        )

        narrative = result["narrative"]
        structured = result["structured"]
        chat_repo.add_message(session_id, "assistant", narrative, prediction_data=structured)

        return {
            "session_id": session_id,
            "prediction": narrative,
            "structured": structured,
            "ml_result": result["ml_result"],
        }

    except Exception as e:
        logger.error(f"Prediction error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
