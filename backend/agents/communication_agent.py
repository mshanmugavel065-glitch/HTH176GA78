from typing import List
from models import DisasterZone, ResourcePool, AgentRecommendation, ZoneAllocation, PublicAlert
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class CommunicationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="communication_agent",
            agent_name="Communications Agent",
            priority_focus="Public Evacuation Alerts & Safety Messages"
        )

    def generate_public_alert(self, zones: List[DisasterZone]) -> PublicAlert:
        evac_zones = [z for z in zones if z.evacuation_required]
        target_zone_name = evac_zones[0].name if evac_zones else zones[0].name
        target_zone_route = evac_zones[0].alternate_route if (evac_zones and evac_zones[0].alternate_route) else "designated evacuation route"

        prompt = f"""
You are the Communications Agent for RESQ-AI emergency response system.
Target Evacuation Zone: {target_zone_name}
Approved Route: {target_zone_route}

Draft an urgent, authoritative emergency public alert broadcast instructing residents to evacuate safely.
Output JSON with:
{{
  "title": "🚨 FLOOD EVACUATION ALERT — {target_zone_name}",
  "target_zone": "{target_zone_name}",
  "message": "Residents in {target_zone_name} are advised to move to the designated emergency shelter immediately using {target_zone_route}. Follow instructions from emergency response teams.",
  "approved_route": "{target_zone_route}"
}}
"""
        system_instruction = "You are a crisis communications expert AI. Draft clear, urgent public safety alert broadcasts for emergency evacuations."
        llm_data = llm_service.generate_json(prompt, system_instruction)

        if llm_data and "message" in llm_data:
            return PublicAlert(
                title=llm_data.get("title", f"🚨 FLOOD EVACUATION ALERT — {target_zone_name}"),
                target_zone=llm_data.get("target_zone", target_zone_name),
                message=llm_data.get("message", f"Residents in {target_zone_name} are advised to move to designated shelters using {target_zone_route}."),
                approved_route=llm_data.get("approved_route", target_zone_route),
                timestamp=self.get_timestamp(),
                label="AI-GENERATED PUBLIC ALERT — SIMULATED SCENARIO"
            )

        # Fallback Alert
        return PublicAlert(
            title=f"🚨 FLOOD EVACUATION ALERT — {target_zone_name}",
            target_zone=target_zone_name,
            message=f"URGENT MANDATORY EVACUATION: Residents in {target_zone_name} are advised to move to the designated emergency shelter using approved bypass route {target_zone_route}. Follow directives from field response teams.",
            approved_route=target_zone_route,
            timestamp=self.get_timestamp(),
            label="AI-GENERATED PUBLIC ALERT — SIMULATED SCENARIO"
        )

    def analyze(self, zones: List[DisasterZone], resources: ResourcePool) -> AgentRecommendation:
        evac_zones = [z for z in zones if z.evacuation_required]
        insights = [
            f"Public Communication Status: {len(evac_zones)} sectors flagged for immediate emergency evacuation advisories.",
            "Wireless Emergency Alert (WEA) broadcast initiated for high-hazard flood zones.",
            "Evacuation route guidance published for blocked road bypasses."
        ]

        recommendations = []
        total_pop = sum(z.population for z in zones) or 1
        for z in zones:
            if z.evacuation_required:
                msg = f"URGENT ALERT: Mandatory Evacuation Order issued for {z.name}. Evacuate via {z.alternate_route or z.road_name}."
            elif z.risk == "Critical":
                msg = f"CRITICAL WARNING: High hazard level in {z.name}. Shelter in place and await medical rescue teams."
            else:
                msg = f"ADVISORY: Moderate flood warning for {z.name}. Clear primary roads for emergency vehicles."

            recommendations.append(ZoneAllocation(
                zone_id=z.id,
                zone_name=z.name,
                vehicles=1 if z.evacuation_required else 0,
                medics=0,
                shelter_units=1 if z.evacuation_required else 0,
                supplies=int((z.population / total_pop) * 50),
                priority=z.risk,
                reason=msg
            ))

        return AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=recommendations,
            insights=insights,
            priority_focus=self.priority_focus
        )
