from typing import List
from models import DisasterZone, ResourcePool, AgentRecommendation, ZoneAllocation, PublicAlert
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class CommunicationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="communication_agent",
            agent_name="Communications Agent",
            priority_focus="Public Evacuation Alerts & Safety Messaging"
        )

    def generate_public_alert(self, zones: List[DisasterZone], location: str = "Active Sector", disaster_type: str = "Flood") -> PublicAlert:
        evac_zones = [z for z in zones if z.evacuation_required or z.risk_level in ["Critical", "Very High"]]
        target_zone = evac_zones[0] if evac_zones else (zones[0] if zones else None)
        target_name = target_zone.name if target_zone else "Affected Sector"
        target_route = target_zone.alternate_route if (target_zone and target_zone.alternate_route) else "designated relief bypass"

        prompt = f"""
You are the Communications Agent for RESQ-AI emergency response system.
Location: {location}
Disaster Type: {disaster_type}
Target Evacuation Sector: {target_name}
Approved Evacuation Bypass Route: {target_route}

Draft an urgent, authoritative emergency public alert broadcast instructing residents to evacuate safely.
Output JSON with:
{{
  "title": "🚨 EMERGENCY PUBLIC ALERT — {location.upper()}",
  "target_zone": "{target_name}",
  "message": "Heavy flooding in {location} has created hazardous conditions. Residents in {target_name} are urged to evacuate via {target_route} to designated relief shelters.",
  "approved_route": "{target_route}"
}}
"""
        system_instruction = "You are a crisis communications expert AI. Draft clear, urgent public safety alert broadcasts for emergency evacuations."
        llm_data = llm_service.generate_json(prompt, system_instruction)

        if llm_data and "message" in llm_data:
            return PublicAlert(
                title=llm_data.get("title", f"🚨 EMERGENCY PUBLIC ALERT — {location.upper()}"),
                target_zone=llm_data.get("target_zone", target_name),
                message=llm_data.get("message", f"Heavy flooding in {location} has created high-risk conditions. Residents in {target_name} should evacuate using {target_route}."),
                approved_route=llm_data.get("approved_route", target_route),
                timestamp=self.get_timestamp(),
                label="AI-GENERATED PUBLIC ALERT — SIMULATED SCENARIO"
            )

        # Fallback Alert using active location
        return PublicAlert(
            title=f"🚨 EMERGENCY PUBLIC ALERT — {location.upper()}",
            target_zone=target_name,
            message=f"AI-GENERATED PUBLIC ALERT ({location.upper()}): Heavy flooding has created high-risk conditions in {target_name}. Residents in affected sectors should follow designated evacuation instructions via {target_route}.",
            approved_route=target_route,
            timestamp=self.get_timestamp(),
            label="AI-GENERATED PUBLIC ALERT — SIMULATED SCENARIO"
        )

    def analyze(self, zones: List[DisasterZone], resources: ResourcePool) -> AgentRecommendation:
        evac_zones = [z for z in zones if z.evacuation_required]
        insights = [
            f"Public Communication Status: {len(evac_zones)} sectors flagged for immediate emergency evacuation broadcasts.",
            "Wireless Emergency Alert (WEA) network active for severe flood sectors.",
            "Bypass evacuation advisories published for blocked primary corridors."
        ]

        recommendations = []
        for z in zones:
            if z.evacuation_required or z.severity_score >= 80:
                msg = f"URGENT ALERT: Mandatory Evacuation Order issued for {z.name}. Evacuate via {z.alternate_route or z.road_name}."
            elif z.severity_score >= 50:
                msg = f"CRITICAL ADVISORY: High flood severity in {z.name}. Prepare emergency kits and stand by for evacuation."
            else:
                msg = f"ADVISORY: Moderate hazard level for {z.name}. Clear primary routes for rescue vehicles."

            recommendations.append(ZoneAllocation(
                zone_id=z.id,
                zone_name=z.name,
                vehicles=1 if z.evacuation_required else 0,
                medics=0,
                shelter_units=1 if z.evacuation_required else 0,
                supplies=20,
                priority=z.risk_level,
                severity_score=z.severity_score,
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
