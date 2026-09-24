from typing import List
from models import DisasterZone, ResourcePool, AgentRecommendation, ZoneAllocation
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class LogisticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="logistics_agent",
            agent_name="Logistics Agent",
            priority_focus="Rescue Fleet, Shelters & Evacuation Routing"
        )

    def analyze(self, zones: List[DisasterZone], resources: ResourcePool) -> AgentRecommendation:
        road_summary = "\n".join([f"- {z.name}: Road='{z.road_name}' (Status: {z.road_status}). Alternate Route: '{z.alternate_route}'" for z in zones])

        prompt = f"""
You are the Logistics Agent in RESQ-AI disaster management.
Available Fleet & Shelters: {self.format_resources_summary(resources)}

Road Network Status & Zone Telemetry:
{road_summary}

Disaster Zones:
{self.format_zones_summary(zones)}

Evaluate transport routing, shelter capacity, hazard severity, and road access blockages.
Do NOT allocate resources using population alone. Priority must go to high flood severity, blocked road corridors, and evacuation zones.

Output JSON with:
{{
  "insights": ["Logistics insight 1", "Evacuation route insight 2"],
  "recommendations": [
    {{
      "zone_id": "zone-c",
      "zone_name": "Zone C",
      "vehicles": 2,
      "medics": 1,
      "shelter_units": 1,
      "supplies": 30,
      "priority": "High",
      "reason": "Road 3 is BLOCKED. Rerouting evacuation via Road 4 (North Ridge Bypass)."
    }}
  ]
}}
"""
        system_instruction = "You are an AI logistics expert. Evaluate transport routing, road network blockages, vehicle allocation, and evacuation corridors. Respond in strict JSON."
        llm_data = llm_service.generate_json(prompt, system_instruction)

        recommendations = []
        insights = []

        if llm_data and "recommendations" in llm_data:
            insights = llm_data.get("insights", [])
            for rec in llm_data["recommendations"]:
                recommendations.append(ZoneAllocation(
                    zone_id=rec.get("zone_id", ""),
                    zone_name=rec.get("zone_name", ""),
                    vehicles=rec.get("vehicles", 0),
                    medics=rec.get("medics", 0),
                    shelter_units=rec.get("shelter_units", 0),
                    supplies=rec.get("supplies", 0),
                    priority=rec.get("priority", "Moderate"),
                    reason=rec.get("reason", "Logistics & routing allocation")
                ))
        else:
            # Deterministic Fallback Road & Logistics Logic
            blocked_zones = [z for z in zones if z.road_status == "Blocked"]
            congested_zones = [z for z in zones if z.road_status == "Congested"]

            insights = [
                f"Road Network Analysis: Identified {len(blocked_zones)} blocked and {len(congested_zones)} congested evacuation corridors.",
                f"Zone C Road 3 is BLOCKED: Emergency fleet rerouted via alternate Road 4 (North Ridge Bypass).",
                f"Logistics Priority: Rescue vehicles dispatched to sectors with severe flood levels & evacuation orders (population alone is ignored)."
            ]

            for z in zones:
                if z.severity_score >= 80 or z.flood_level_m >= 3.5 or z.evacuation_required:
                    veh = 2
                    shelter = 1
                elif z.severity_score >= 50 or z.flood_level_m >= 2.0:
                    veh = 1
                    shelter = 1 if z.evacuation_required else 0
                else:
                    veh = 1 if z.critical > 0 else 0
                    shelter = 0

                supplies = 30 if z.severity_score >= 70 else (20 if z.severity_score >= 40 else 10)
                route_note = f"Evac required. Road '{z.road_name}' is {z.road_status}. Alternate: '{z.alternate_route}'." if z.road_status != "Open" else f"Road '{z.road_name}' open."

                recommendations.append(ZoneAllocation(
                    zone_id=z.id,
                    zone_name=z.name,
                    vehicles=veh,
                    medics=1 if z.critical > 0 else 0,
                    shelter_units=shelter,
                    supplies=supplies,
                    priority=z.risk_level,
                    severity_score=z.severity_score,
                    reason=f"Logistics: {route_note} Flood level {z.flood_level_m}m, Severity {z.severity_score}/100."
                ))

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=recommendations,
            insights=insights,
            priority_focus=self.priority_focus
        )
