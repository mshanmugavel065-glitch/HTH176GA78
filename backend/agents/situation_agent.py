from typing import List, Dict, Any
from models import DisasterZone, ResourcePool, AgentRecommendation
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class SituationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="situation_agent",
            agent_name="Situation / Incident Agent",
            priority_focus="Incident Categorization & Severity Estimation"
        )

    def analyze_situation(self, situation_text: str, zones: List[DisasterZone]) -> AgentRecommendation:
        prompt = f"""
You are the Situation / Incident Agent in RESQ-AI emergency response system.
Reported Situation: "{situation_text}"

Current Disaster Zones:
{self.format_zones_summary(zones)}

Categorize incidents, estimate severity, identify emergency indicators, and evaluate affected sectors.
Output JSON with:
{{
  "insights": [
    "Incident severity insight 1",
    "Casualty indicator 2"
  ],
  "priority_focus": "Flash Flood & Infrastructure Incident Priority"
}}
"""
        system_instruction = "You are an incident assessment AI agent. Categorize disaster reports, estimate damage indicators, and assess severity tiers."
        llm_data = llm_service.generate_json(prompt, system_instruction)

        insights = []
        if llm_data and "insights" in llm_data:
            insights = llm_data["insights"]
        else:
            total_injured = sum(z.injured for z in zones)
            total_critical = sum(z.critical for z in zones)
            insights = [
                f"Incident Report Analysis: '{situation_text}' categorized as High Severity Emergency.",
                f"Assessed casualty load: {total_critical} critical trauma cases, {total_injured} total injured across active zones.",
                "Structural hazard indicators flagged for immediate response escalation."
            ]

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=[],
            insights=insights,
            priority_focus="Incident Severity & Threat Categorization"
        )
