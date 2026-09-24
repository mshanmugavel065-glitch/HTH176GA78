from datetime import datetime
from typing import List, Dict, Any
from models import DisasterZone, ResourcePool, AgentRecommendation

class BaseAgent:
    def __init__(self, agent_id: str, agent_name: str, priority_focus: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.priority_focus = priority_focus

    def get_timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def format_zones_summary(self, zones: List[DisasterZone]) -> str:
        summary_lines = []
        for z in zones:
            summary_lines.append(
                f"- {z.name} ({z.id}): Pop={z.population}, Injured={z.injured}, Critical={z.critical}, Risk={z.risk}, EvacRequired={z.evacuation_required}. Description: {z.description}"
            )
        return "\n".join(summary_lines)

    def format_resources_summary(self, resources: ResourcePool) -> str:
        return f"Rescue Vehicles: {resources.vehicles}, Medics: {resources.medics}, Shelters: {resources.shelters}, Supplies: {resources.supplies}"
