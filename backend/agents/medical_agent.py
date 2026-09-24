from typing import List
from models import DisasterZone, ResourcePool, AgentRecommendation, ZoneAllocation
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class MedicalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="medical_agent",
            agent_name="Medical Agent",
            priority_focus="Triage & Trauma Medic Allocation"
        )

    def analyze(self, zones: List[DisasterZone], resources: ResourcePool) -> AgentRecommendation:
        prompt = f"""
You are the Medical Agent in RESQ-AI emergency response system.
Available Resources: {self.format_resources_summary(resources)}

Disaster Zones Telemetry & Hazard Analysis:
{self.format_zones_summary(zones)}

Analyze injury severity, critical trauma cases, hazard severity scores, and medical urgency.
Do NOT use population alone to allocate medical staff. Prioritize zones with high critical patients and high hazard severity.

Output JSON with:
{{
  "insights": ["insight 1", "insight 2"],
  "recommendations": [
    {{
      "zone_id": "zone-b",
      "zone_name": "Zone B",
      "vehicles": 1,
      "medics": 5,
      "shelter_units": 0,
      "supplies": 35,
      "priority": "Critical",
      "reason": "Medical triage rationale based on 10 critical patients and 84/100 severity score."
    }}
  ]
}}
"""
        system_instruction = "You are a chief medical officer and triage AI expert. Prioritize saving lives, emergency trauma treatment, and field medic allocation based on medical urgency and hazard severity."
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
                    reason=rec.get("reason", "Medical triage allocation")
                ))
        else:
            # Deterministic Fallback Triage Logic based on trauma & hazard severity
            total_critical = sum(z.critical for z in zones) or 1
            total_injured = sum(z.injured for z in zones) or 1

            insights = [
                f"Medical Triage Analysis: Identified {sum(z.critical for z in zones)} critical casualties and {sum(z.injured for z in zones)} injured across active sectors.",
                f"Primary Medical Focus: Sectors with elevated hazard severity and critical patient concentration assigned priority medic teams.",
                f"Resource Bounds: {resources.medics} total medics allocated strictly by medical urgency and hazard severity (population alone is ignored)."
            ]

            for z in zones:
                # Allocation based on critical patients and severity score
                if z.critical >= 8 or z.severity_score >= 80:
                    medics_demanded = 5
                    priority_lvl = "Critical"
                elif z.critical >= 4 or z.severity_score >= 60:
                    medics_demanded = 3
                    priority_lvl = "Very High"
                elif z.critical >= 1 or z.severity_score >= 40:
                    medics_demanded = 2
                    priority_lvl = "High"
                else:
                    medics_demanded = 1 if z.injured > 0 else 0
                    priority_lvl = "Moderate"

                vehicles_demanded = 2 if z.critical >= 6 else (1 if z.injured > 10 else 0)

                recommendations.append(ZoneAllocation(
                    zone_id=z.id,
                    zone_name=z.name,
                    vehicles=vehicles_demanded,
                    medics=medics_demanded,
                    shelter_units=0,
                    supplies=int((z.injured / total_injured) * 60) + 10,
                    priority=priority_lvl,
                    severity_score=z.severity_score,
                    reason=f"Medical triage: {z.critical} critical patients, {z.injured} injured, severity score {z.severity_score}/100."
                ))

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=recommendations,
            insights=insights,
            priority_focus=self.priority_focus
        )
