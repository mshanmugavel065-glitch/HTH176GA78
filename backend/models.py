from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DisasterZone(BaseModel):
    id: str
    name: str
    population: int = Field(..., ge=0)
    injured: int = Field(..., ge=0)
    critical: int = Field(..., ge=0)
    risk: str = Field(..., description="Low, Medium, High, or Critical")
    evacuation_required: bool = False
    road_name: str = "Road 1"
    road_status: str = "Open" # Open, Congested, Blocked
    alternate_route: Optional[str] = None
    description: Optional[str] = ""

class ResourcePool(BaseModel):
    vehicles: int = 5
    medics: int = 10
    shelters: int = 3
    supplies: int = 100

class ZoneAllocation(BaseModel):
    zone_id: str
    zone_name: str
    vehicles: int = 0
    medics: int = 0
    shelter_units: int = 0
    supplies: int = 0
    priority: str = "Medium" # Low, Medium, High, Critical
    reason: Optional[str] = ""

class AgentRecommendation(BaseModel):
    agent_id: str
    agent_name: str
    timestamp: str
    recommendations: List[ZoneAllocation] = []
    insights: List[str] = []
    priority_focus: str = ""
    status: str = "completed"

class ConflictItem(BaseModel):
    id: str
    resource_type: str # vehicles, medics, shelters, supplies
    description: str
    zones_involved: List[str]
    demanded: int
    available: int
    resolution: str

class PlanChange(BaseModel):
    zone_id: str
    zone_name: str
    resource_type: str
    before: int
    after: int
    reason: str

class PublicAlert(BaseModel):
    title: str = "🚨 EMERGENCY EVACUATION ALERT"
    target_zone: str = "Zone C"
    message: str
    approved_route: str = "Approved Emergency Bypass Route"
    timestamp: str
    label: str = "AI-GENERATED PUBLIC ALERT — SIMULATED SCENARIO"

class AgentNegotiation(BaseModel):
    medical_request: str
    logistics_request: str
    comm_request: str
    coordinator_resolution: str

class CoordinatorPlan(BaseModel):
    timestamp: str
    final_allocations: List[ZoneAllocation]
    resource_usage: Dict[str, Dict[str, int]]
    conflicts: List[ConflictItem]
    changes: List[PlanChange]
    explanation: str
    agent_tradeoffs: Dict[str, str]
    public_alert: Optional[PublicAlert] = None
    agent_negotiation: Optional[AgentNegotiation] = None

class ActivityLog(BaseModel):
    id: str
    timestamp: str
    agent: str
    action: str
    details: str
    type: str = "info" # info, warning, success, conflict

class ChatMessage(BaseModel):
    id: str
    sender: str # "user" or "assistant" or "system"
    content: str
    timestamp: str
    agent_name: Optional[str] = "RESQ-AI Assistant"
    suggested_actions: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = None

class SystemState(BaseModel):
    location: str = ""
    situation_query: str = ""
    data_source_mode: str = "SIMULATED DISASTER SCENARIO"
    zones: List[DisasterZone] = []
    resources: ResourcePool = ResourcePool(vehicles=5, medics=10, shelters=3, supplies=100)
    current_plan: Optional[CoordinatorPlan] = None
    agent_activity: List[ActivityLog] = []
    agent_recommendations: Dict[str, AgentRecommendation] = {}
    chat_history: List[ChatMessage] = []
    active_agents_count: int = 4
    is_analyzed: bool = False
    is_pending_replan: bool = False
    last_updated: str = ""
