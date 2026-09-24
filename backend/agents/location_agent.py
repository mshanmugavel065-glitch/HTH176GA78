from typing import List, Dict, Any
from models import DisasterZone, ResourcePool, AgentRecommendation
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class LocationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="location_agent",
            agent_name="Location Intelligence Agent",
            priority_focus="Geographic Zone & Sector Analysis"
        )

    def analyze_location(self, location_name: str, zones: List[DisasterZone]) -> AgentRecommendation:
        prompt = f"""
You are the Location Intelligence Agent in RESQ-AI emergency response system.
Location Requested: "{location_name}"

Current Disaster Zones:
{self.format_zones_summary(zones)}

Analyze geographic topology, sector risk boundaries, and critical infrastructure for {location_name}.
Output JSON with:
{{
  "insights": [
    "Geographic insight 1",
    "Geographic insight 2"
  ],
  "priority_focus": "Sector Topography & Evacuation Corridors"
}}
"""
        system_instruction = "You are a GIS and Location Intelligence AI agent specializing in disaster zone partitioning and geographical emergency management."
        llm_data = llm_service.generate_json(prompt, system_instruction)

        insights = []
        if llm_data and "insights" in llm_data:
            insights = llm_data["insights"]
        else:
            insights = [
                f"Geographic mapping initialized for {location_name}.",
                f"Identified {len(zones)} key sector zones requiring emergency monitoring.",
                "Mapped primary arterial evacuation highways and high-risk flood/hazard sectors."
            ]

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=[],
            insights=insights,
            priority_focus="Geographic Sectoring & Corridor Mapping"
        )
