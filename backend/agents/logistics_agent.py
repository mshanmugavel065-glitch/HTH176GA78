from typing import List
from models import DisasterZone, ResourcePool, AgentRecommendation, ZoneAllocation
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class LogisticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="logistics_agent",
            agent_name="Logistics Agent",
            priority_focus="Vehicle Allocation, Shelters & Evacuation Routing"
        )

    def analyze(self, zones: List[DisasterZone], resources: ResourcePool) -> AgentRecommendation:
        road_summary = "\n".join([f"- {z.name}: Road='{z.road_name}' (Status: {z.road_status}). Alternate Route: '{z.alternate_route}'" for z in zones])

        prompt = f"""
You are the Logistics Agent in RESQ-AI disaster management.
Available Fleet & Shelters: {self.format_resources_summary(resources)}

Road Network Status:
{road_summary}

Disaster Zones:
{self.format_zones_summary(zones)}

Evaluate transport routing, shelter limits, and road access. Note blocked roads (e.g. Zone C Road 3 blocked).
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
                    priority=rec.get("priority", "Medium"),
                    reason=rec.get("reason", "Logistics & routing allocation")
                ))
        else:
            # Deterministic Fallback Road & Logistics Logic
            blocked_zones = [z for z in zones if z.road_status == "Blocked"]
            congested_zones = [z for z in zones if z.road_status == "Congested"]
            
            insights = [
                f"Road Network Analysis: Identified {len(blocked_zones)} blocked evacuation corridors.",
                f"Zone C Road 3 is BLOCKED: Routing emergency fleet via alternate {zones[2].alternate_route if len(zones)>2 else 'Bypass'}.",
                f"Fleet vehicle constraint: {resources.vehicles} vehicles available for dispatch across {len(zones)} active sectors."
            ]

            total_pop = sum(z.population for z in zones) or 1
            for z in zones:
                veh = 2 if z.evacuation_required else (1 if z.critical > 5 else 0)
                shelter = 1 if z.evacuation_required else 0
                supplies = int((z.population / total_pop) * resources.supplies)

                route_note = f"Evac required. Road '{z.road_name}' is {z.road_status}. Alternate: '{z.alternate_route}'." if z.road_status != "Open" else f"Road '{z.road_name}' open."

                recommendations.append(ZoneAllocation(
                    zone_id=z.id,
                    zone_name=z.name,
                    vehicles=veh,
                    medics=1 if z.critical > 0 else 0,
                    shelter_units=shelter,
                    supplies=supplies,
                    priority=z.risk,
                    reason=f"Logistics allocation: {route_note}"
                ))

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=recommendations,
            insights=insights,
            priority_focus=self.priority_focus
        )
