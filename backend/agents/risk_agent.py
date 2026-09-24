from typing import List, Dict, Any
from models import DisasterZone, ResourcePool, AgentRecommendation
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="risk_agent",
            agent_name="Risk Agent",
            priority_focus="Risk Indicator Comparison & Priority Matrix"
        )

    def analyze_risk(self, zones: List[DisasterZone]) -> AgentRecommendation:
        prompt = f"""
You are the Risk Agent in RESQ-AI emergency response system.
Disaster Zones:
{self.format_zones_summary(zones)}

Compare environmental risk indicators, calculate severity index, and rank zones by threat level.
Output JSON with:
{{
  "insights": [
    "Risk assessment insight 1",
    "Hazard priority ranking 2"
  ],
  "priority_focus": "Critical Threat Priority Matrix"
}}
"""
        system_instruction = "You are a crisis risk assessment AI agent. Analyze environmental hazards, secondary threats, and priority rankings."
        llm_data = llm_service.generate_json(prompt, system_instruction)

        insights = []
        if llm_data and "insights" in llm_data:
            insights = llm_data["insights"]
        else:
            crit_zones = [z.name for z in zones if z.risk == "Critical"]
            high_zones = [z.name for z in zones if z.risk == "High"]
            insights = [
                f"Risk Priority Matrix: {', '.join(crit_zones) or 'None'} designated as CRITICAL RISK sectors.",
                f"Secondary hazard warnings active for {', '.join(high_zones) or 'remaining sectors'}.",
                "Evacuation directive risk score elevated due to compounding hazards."
            ]

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=[],
            insights=insights,
            priority_focus="Compound Risk Evaluation"
        )
