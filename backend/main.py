import json
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from config import settings
from models import DisasterZone, ResourcePool, SystemState
from services.scenario_manager import scenario_manager

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="RESQ-AI: Generative Multi-Agent Disaster Response Coordinator API"
)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    location: str
    situation: str

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {
        "status": "active",
        "system": settings.PROJECT_NAME,
        "tagline": "Generative Multi-Agent Disaster Response Coordinator",
        "version": settings.VERSION,
        "llm_configured": bool(settings.GEMINI_API_KEY)
    }

@app.get("/api/state", response_model=SystemState)
def get_system_state():
    return scenario_manager.get_state()

@app.post("/api/analyze", response_model=SystemState)
def analyze_situation(req: AnalyzeRequest):
    try:
        return scenario_manager.analyze_location_and_situation(req.location, req.situation)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@app.post("/api/chat", response_model=SystemState)
def chat_with_agent(req: ChatRequest):
    return scenario_manager.process_chat_message(req.message)

@app.post("/api/plan", response_model=SystemState)
def trigger_plan():
    return scenario_manager.run_full_pipeline(is_replan=False)

@app.post("/api/replan", response_model=SystemState)
def trigger_replan():
    return scenario_manager.run_full_pipeline(is_replan=True)

@app.post("/api/zones", response_model=SystemState)
def add_or_update_zone(zone: DisasterZone):
    existing = [z for z in scenario_manager.zones if z.id == zone.id]
    if existing:
        scenario_manager.zones = [zone if z.id == zone.id else z for z in scenario_manager.zones]
    else:
        scenario_manager.zones.append(zone)
    return scenario_manager.get_state()

@app.post("/api/zones/preset-d", response_model=SystemState)
def add_preset_zone_d():
    return scenario_manager.add_preset_zone_d()

@app.delete("/api/zones/{zone_id}", response_model=SystemState)
def delete_zone(zone_id: str):
    scenario_manager.zones = [z for z in scenario_manager.zones if z.id != zone_id]
    return scenario_manager.get_state()

@app.post("/api/resources", response_model=SystemState)
def update_resources(res: ResourcePool):
    scenario_manager.resources = res
    scenario_manager._add_activity("system", "Resource Bounds Updated", f"Set to {res.vehicles} vehicles, {res.medics} medics.", "warning")
    if scenario_manager.current_plan:
        return scenario_manager.run_full_pipeline(is_replan=True)
    return scenario_manager.get_state()

@app.post("/api/reset", response_model=SystemState)
def reset_system():
    return scenario_manager.reset_system()

@app.get("/api/activity")
def get_activity_logs():
    return scenario_manager.activity_logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
