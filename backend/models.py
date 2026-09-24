from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DisasterZone(BaseModel):
    id: str
    name: str
    population: int = Field(..., ge=0)
    injured: int = Field(..., ge=0)
    critical: int = Field(..., ge=0)
    risk: str = Field(..., description="Low, Moderate, High, Very High, or Critical")
    rainfall_mm: float = 0.0
    flood_level_m: float = 0.0
    affected_area_km2: float = 0.0
    road_access: float = 1.0  # 0.0 (blocked) to 1.0 (fully open)
    severity_score: float = 0.0  # Prototype score 0 - 100
    risk_level: str = "Low"
    evacuation_required: bool = False
    road_name: str = "Road 1"
    road_status: str = "Open"  # Open, Congested, Blocked
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
    priority: str = "Moderate"  # Low, Moderate, High, Very High, Critical
    severity_score: float = 0.0
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
    resource_type: str  # vehicles, medics, shelters, supplies
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

class PlanDifference(BaseModel):
    zone_id: str
    zone_name: str
    before_risk: str
    after_risk: str
    before_priority: str
    after_priority: str
    before_vehicles: int
    after_vehicles: int
    before_medics: int
    after_medics: int
    reason: str

class PublicAlert(BaseModel):
    title: str = "🚨 EMERGENCY EVACUATION ALERT"
    target_zone: str = "Zone C"
    message: str
    approved_route: str = "Approved Emergency Bypass Route"
    timestamp: str
    label: str = "AI-GENERATED PUBLIC ALERT — SIMULATED SCENARIO"

class AgentNegotiation(BaseModel):
    intelligence_request: str
    medical_request: str
    logistics_request: str
    comm_request: str
    coordinator_resolution: str

class DatasetMetadata(BaseModel):
    filename: Optional[str] = None
    data_type: str = "SIMULATED DISASTER SCENARIO"  # "UPLOADED DATASET" or "SIMULATED DISASTER SCENARIO"
    columns_detected: List[str] = []
    row_count: int = 0
    warnings: List[str] = []
    summary_stats: Dict[str, Any] = {}

class DisasterIntelligenceResult(BaseModel):
    overall_severity_score: float = 0.0
    overall_risk_level: str = "Moderate"
    max_rainfall_mm: float = 0.0
    max_flood_level_m: float = 0.0
    total_affected_area_km2: float = 0.0
    priority_zone_id: Optional[str] = None
    priority_zone_name: Optional[str] = None
    contributing_factors: Dict[str, str] = {}
    explanation: str = ""
    model_disclaimer: str = "Prototype Risk Score Model — Simulated / Prototype Scoring"

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
    type: str = "info"  # info, warning, success, conflict

class ChatMessage(BaseModel):
    id: str
    sender: str  # "user" or "assistant" or "system"
    content: str
    timestamp: str
    agent_name: Optional[str] = "RESQ-AI Assistant"
    suggested_actions: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = None

class SystemState(BaseModel):
    location: str = ""
    disaster_type: str = "Flood"
    situation_query: str = ""
    data_source_mode: str = "SIMULATED DISASTER SCENARIO"
    dataset_metadata: Optional[DatasetMetadata] = None
    intelligence_result: Optional[DisasterIntelligenceResult] = None
    zones: List[DisasterZone] = []
    resources: ResourcePool = ResourcePool(vehicles=5, medics=10, shelters=3, supplies=100)
    current_plan: Optional[CoordinatorPlan] = None
    previous_plan: Optional[CoordinatorPlan] = None
    plan_differences: List[PlanDifference] = []
    agent_activity: List[ActivityLog] = []
    agent_recommendations: Dict[str, AgentRecommendation] = {}
    chat_history: List[ChatMessage] = []
    active_agents_count: int = 5
    is_analyzed: bool = False
    is_pending_replan: bool = False
    last_updated: str = ""
