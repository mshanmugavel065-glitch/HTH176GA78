from typing import List
from models import DisasterZone, ResourcePool, AgentRecommendation, ZoneAllocation
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class MedicalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="medical_agent",
            agent_name="Medical Agent",
            priority_focus="Triage & Medic Allocation"
        )

    def analyze(self, zones: List[DisasterZone], resources: ResourcePool) -> AgentRecommendation:
        prompt = f"""
You are the Medical Agent in RESQ-AI emergency response system.
Available Resources: {self.format_resources_summary(resources)}

Disaster Zones:
{self.format_zones_summary(zones)}

Analyze injury severity, critical patient ratio, and medical urgency.
Output JSON with:
{{
  "insights": ["insight 1", "insight 2"],
  "recommendations": [
    {{
      "zone_id": "zone-b",
      "zone_name": "Zone B",
      "vehicles": 1,
      "medics": 6,
      "shelter_units": 0,
      "supplies": 35,
      "priority": "Critical",
      "reason": "Medical triage rationale"
    }}
  ]
}}
"""
        system_instruction = "You are a chief medical officer and triage AI expert. Prioritize saving lives, emergency treatment, and field medic allocation. Respond in strict JSON."
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
                    reason=rec.get("reason", "Medical triage allocation")
                ))
        else:
            # Deterministic Fallback Triage Logic
            total_critical = sum(z.critical for z in zones) or 1
            total_injured = sum(z.injured for z in zones)
            
            insights = [
                f"Triage Analysis: Identified {total_critical} critical casualties and {total_injured} total injured across active zones.",
                "Zone B / Critical sectors require urgent intensive medical deployment due to high trauma density.",
                f"Medical personnel constraint: {resources.medics} total medics must be prioritized strictly by trauma severity."
            ]



            # Calculate medic allocation by critical weight
            for z in zones:
                # Heavy weighting on critical patients
                if z.critical >= 8:
                    medics_demanded = 5
                elif z.critical >= 4:
                    medics_demanded = 3
                elif z.critical >= 1:
                    medics_demanded = 2
                else:
                    medics_demanded = 1 if z.injured > 0 else 0

                vehicles_demanded = 2 if z.critical >= 6 else (1 if z.injured > 10 else 0)
                
                recommendations.append(ZoneAllocation(
                    zone_id=z.id,
                    zone_name=z.name,
                    vehicles=vehicles_demanded,
                    medics=medics_demanded,
                    shelter_units=0, # Medical agent focuses on medics & med supplies
                    supplies=int((z.injured / (total_injured or 1)) * 60) + 10,
                    priority=z.risk,
                    reason=f"Triage priority: {z.critical} critical patients, {z.injured} injured. Requires {medics_demanded} medics."
                ))

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=recommendations,
            insights=insights,
            priority_focus=self.priority_focus
        )
