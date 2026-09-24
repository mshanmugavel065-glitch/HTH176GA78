from typing import List, Dict, Any, Tuple
from datetime import datetime
from models import DisasterZone, ResourcePool, AgentRecommendation, DisasterIntelligenceResult
from agents.base_agent import BaseAgent
from services.llm_service import llm_service

class DisasterIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="disaster_intelligence_agent",
            agent_name="Disaster Intelligence Agent",
            priority_focus="Hazard Severity & Risk Factor Analysis"
        )

    def calculate_zone_risk(self, zone: DisasterZone) -> Tuple[float, str, Dict[str, str]]:
        # 1. Rainfall contribution (0-25 pts): normalized against 300mm max
        rainfall_val = max(0.0, float(zone.rainfall_mm or 0.0))
        rainfall_pts = min(25.0, (rainfall_val / 300.0) * 25.0)

        # 2. Flood level contribution (0-25 pts): normalized against 5.0m max
        flood_val = max(0.0, float(zone.flood_level_m or 0.0))
        flood_pts = min(25.0, (flood_val / 5.0) * 25.0)

        # 3. Affected area contribution (0-15 pts): normalized against 40 km2 max
        area_val = max(0.0, float(zone.affected_area_km2 or 0.0))
        area_pts = min(15.0, (area_val / 40.0) * 15.0)

        # 4. Medical urgency contribution (0-25 pts): based on critical patients & injured
        crit_val = max(0, int(zone.critical or 0))
        inj_val = max(0, int(zone.injured or 0))
        med_score = (crit_val * 5) + inj_val
        medical_pts = min(25.0, (med_score / 60.0) * 25.0)

        # 5. Accessibility contribution (0-10 pts): inverse of road_access (0.0 blocked = 10 pts risk)
        road_acc = max(0.0, min(1.0, float(zone.road_access if zone.road_access is not None else 1.0)))
        access_pts = (1.0 - road_acc) * 10.0

        # Total prototype severity score (0-100)
        total_score = round(rainfall_pts + flood_pts + area_pts + medical_pts + access_pts, 1)

        # Classify risk level
        if total_score >= 80.0:
            risk_lvl = "Critical"
        elif total_score >= 60.0:
            risk_lvl = "Very High"
        elif total_score >= 40.0:
            risk_lvl = "High"
        elif total_score >= 20.0:
            risk_lvl = "Moderate"
        else:
            risk_lvl = "Low"

        # Factor breakdown strings
        factors = {
            "Rainfall": "Very High" if rainfall_pts >= 20 else ("High" if rainfall_pts >= 12 else ("Moderate" if rainfall_pts >= 6 else "Low")),
            "Flood Level": "Very High" if flood_pts >= 20 else ("High" if flood_pts >= 12 else ("Moderate" if flood_pts >= 6 else "Low")),
            "Affected Area": "High" if area_pts >= 10 else ("Moderate" if area_pts >= 5 else "Low"),
            "Medical Urgency": "Critical" if medical_pts >= 20 else ("High" if medical_pts >= 12 else ("Moderate" if medical_pts >= 6 else "Low")),
            "Road Accessibility": "Impaired" if access_pts >= 7 else ("Restricted" if access_pts >= 3 else "Open")
        }

        return total_score, risk_lvl, factors

    def analyze_disaster(self, zones: List[DisasterZone], location: str, disaster_type: str) -> Tuple[DisasterIntelligenceResult, AgentRecommendation]:
        if not zones:
            res = DisasterIntelligenceResult(
                overall_severity_score=0.0,
                overall_risk_level="Low",
                explanation="No active disaster sectors to analyze."
            )
            rec = AgentRecommendation(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                timestamp=self.get_timestamp(),
                insights=["No zones active."],
                priority_focus=self.priority_focus
            )
            return res, rec

        # Compute per-zone scores and update zone objects
        highest_score = 0.0
        priority_zone = zones[0]
        max_rainfall = 0.0
        max_flood = 0.0
        total_area = 0.0

        for zone in zones:
            score, risk_lvl, factors = self.calculate_zone_risk(zone)
            zone.severity_score = score
            zone.risk_level = risk_lvl
            zone.risk = risk_lvl  # align legacy field

            if score > highest_score:
                highest_score = score
                priority_zone = zone

            if zone.rainfall_mm > max_rainfall:
                max_rainfall = zone.rainfall_mm
            if zone.flood_level_m > max_flood:
                max_flood = zone.flood_level_m
            total_area += zone.affected_area_km2

        # Overall severity is highest score or weighted average
        avg_score = sum(z.severity_score for z in zones) / len(zones)
        overall_score = round((highest_score * 0.7) + (avg_score * 0.3), 1)

        if overall_score >= 80.0:
            overall_risk = "Critical"
        elif overall_score >= 60.0:
            overall_risk = "Very High"
        elif overall_score >= 40.0:
            overall_risk = "High"
        elif overall_score >= 20.0:
            overall_risk = "Moderate"
        else:
            overall_risk = "Low"

        # Key contributing factors for the top priority zone
        _, _, top_factors = self.calculate_zone_risk(priority_zone)

        # Generate LLM explanation
        prompt = f"""
Disaster Location: {location}
Disaster Type: {disaster_type}
Total Sectors: {len(zones)}
Max Rainfall: {max_rainfall} mm
Max Flood Level: {max_flood} m
Total Affected Area: {total_area} sq km
Highest Risk Zone: {priority_zone.name} (Severity Score: {priority_zone.severity_score}/100, Risk: {priority_zone.risk_level})
Priority Zone Details: {priority_zone.critical} critical patients, {priority_zone.injured} injured, road access {priority_zone.road_access}.

Generate a 2-3 sentence Disaster Intelligence assessment explaining why {priority_zone.name} is the top priority zone based on environmental hazards (rainfall, flood level, affected area) and medical urgency. Do NOT claim exact future death predictions.
"""
        system_instruction = "You are an AI Disaster Intelligence analyst. Provide clear, objective hazard assessment summaries."
        explanation_text = llm_service.generate_chat_response(system_instruction, prompt, [])

        if not explanation_text or len(explanation_text.strip()) < 10:
            explanation_text = (
                f"Elevated hazard indicators in {location} ({max_rainfall}mm rainfall, {max_flood}m flood level) "
                f"combined with {priority_zone.critical} critical trauma casualties designate **{priority_zone.name}** "
                f"as the immediate priority sector (Prototype Severity Score: {priority_zone.severity_score}/100)."
            )

        intel_result = DisasterIntelligenceResult(
            overall_severity_score=overall_score,
            overall_risk_level=overall_risk,
            max_rainfall_mm=max_rainfall,
            max_flood_level_m=max_flood,
            total_affected_area_km2=total_area,
            priority_zone_id=priority_zone.id,
            priority_zone_name=priority_zone.name,
            contributing_factors=top_factors,
            explanation=explanation_text
        )

        insights = [
            f"🌧️ DISASTER INTELLIGENCE ASSESSMENT ({location.upper()}): Overall Risk is {overall_risk.upper()} (Prototype Severity Score: {overall_score}/100).",
            f"📍 Highest Risk Sector: {priority_zone.name} (Score: {priority_zone.severity_score}/100) — Rainfall: {priority_zone.rainfall_mm}mm, Flood Level: {priority_zone.flood_level_m}m.",
            f"📊 Key Contributing Risk Factors: Rainfall ({top_factors.get('Rainfall')}), Flood Level ({top_factors.get('Flood Level')}), Medical Urgency ({top_factors.get('Medical Urgency')})."
        ]

        rec = AgentRecommendation(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            timestamp=self.get_timestamp(),
            recommendations=[],
            insights=insights,
            priority_focus="Hazard Severity & Risk Factor Matrix"
        )

        return intel_result, rec
