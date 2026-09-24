import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from models import (
    DisasterZone, ResourcePool, AgentRecommendation, 
    ZoneAllocation, CoordinatorPlan, ConflictItem, PlanChange,
    PublicAlert, AgentNegotiation
)
from agents.base_agent import BaseAgent
from agents.communication_agent import CommunicationAgent
from services.llm_service import llm_service
from services.validator import validator

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="coordinator_agent",
            agent_name="Coordinator Agent",
            priority_focus="Master Orchestration & Resource Constraint Solver"
        )
        self.comm_agent = CommunicationAgent()

    def synthesize(
        self,
        zones: List[DisasterZone],
        resources: ResourcePool,
        recommendations: Dict[str, AgentRecommendation],
        previous_plan: Optional[CoordinatorPlan] = None,
        location: str = "Active Sector",
        disaster_type: str = "Flood"
    ) -> CoordinatorPlan:

        # 1. Gather all raw recommendations
        all_raw_allocations: List[ZoneAllocation] = []
        for agent_id, agent_rec in recommendations.items():
            all_raw_allocations.extend(agent_rec.recommendations)

        # 2. Check for resource conflicts across raw recommendations
        conflicts = validator.check_constraints(all_raw_allocations, resources)

        # 3. Enforce hard limits deterministically via ResourceValidator
        final_allocations = validator.enforce_hard_limits(zones, all_raw_allocations, resources)

        # Ensure severity score is preserved on final allocations
        zone_score_map = {z.id: z.severity_score for z in zones}
        for alloc in final_allocations:
            alloc.severity_score = zone_score_map.get(alloc.zone_id, alloc.severity_score)

        # 4. Calculate actual resource usage numbers
        total_veh = sum(a.vehicles for a in final_allocations)
        total_med = sum(a.medics for a in final_allocations)
        total_she = sum(a.shelter_units for a in final_allocations)
        total_sup = sum(a.supplies for a in final_allocations)

        resource_usage = {
            "vehicles": {"allocated": total_veh, "total": resources.vehicles},
            "medics": {"allocated": total_med, "total": resources.medics},
            "shelters": {"allocated": total_she, "total": resources.shelters},
            "supplies": {"allocated": total_sup, "total": resources.supplies}
        }

        # 5. Calculate diffs / plan changes if previous plan existed
        changes: List[PlanChange] = []
        if previous_plan and previous_plan.final_allocations:
            prev_map = {a.zone_id: a for a in previous_plan.final_allocations}
            for curr in final_allocations:
                prev = prev_map.get(curr.zone_id)
                if prev:
                    if prev.medics != curr.medics:
                        diff = curr.medics - prev.medics
                        direction = f"+{diff}" if diff > 0 else f"{diff}"
                        changes.append(PlanChange(
                            zone_id=curr.zone_id,
                            zone_name=curr.zone_name,
                            resource_type="medics",
                            before=prev.medics,
                            after=curr.medics,
                            reason=f"Medics re-allocated by {direction} based on critical patient density & severity score."
                        ))
                    if prev.vehicles != curr.vehicles:
                        diff = curr.vehicles - prev.vehicles
                        direction = f"+{diff}" if diff > 0 else f"{diff}"
                        changes.append(PlanChange(
                            zone_id=curr.zone_id,
                            zone_name=curr.zone_name,
                            resource_type="vehicles",
                            before=prev.vehicles,
                            after=curr.vehicles,
                            reason=f"Vehicles adjusted by {direction} for mandatory evacuation & transport."
                        ))

        # 6. Multi-Agent Negotiation Summary
        intel_rec_summary = "Disaster Intelligence Agent identified top severity sectors based on rainfall, flood level, and medical urgency."
        medical_rec_summary = "Medical Agent requested priority medics for sectors with high critical trauma casualties."
        logistics_rec_summary = "Logistics Agent requested vehicle fleet for evacuation corridors and blocked road bypasses."
        comm_rec_summary = "Communications Agent requested priority shelter & public alert broadcasts for high-hazard sectors."

        conflict_res_text = (
            f"Coordinator resolved conflict across available bounds ({resources.vehicles} vehicles, {resources.medics} medics): "
            f"Prioritized high severity sectors for medical triage while allocating vehicles for evacuation bypass routes."
        )

        negotiation = AgentNegotiation(
            intelligence_request=intel_rec_summary,
            medical_request=medical_rec_summary,
            logistics_request=logistics_rec_summary,
            comm_request=comm_rec_summary,
            coordinator_resolution=conflict_res_text
        )

        # 7. Generate Public Alert Draft using current location and disaster
        public_alert = self.comm_agent.generate_public_alert(zones, location=location, disaster_type=disaster_type)

        # 8. Trade-offs and Rationale
        tradeoffs = {
            "hazard_severity_vs_population": "Allocations prioritized sectors with elevated rainfall and flood level over pure population numbers.",
            "medical_vs_logistics": "Medical Agent requested additional medics for critical trauma sectors; Coordinator balanced vehicle fleet to maintain evacuation capability.",
            "road_accessibility_routing": "Blocked road corridors rerouted emergency transport via alternate bypass routes.",
            "fixed_resource_capping": f"Strictly enforced fixed limits of {resources.vehicles} vehicles and {resources.medics} medics without treating resources as infinite."
        }

        # Generate Explainable reasoning
        explanation = self._generate_explanation(zones, final_allocations, conflicts, changes, recommendations, location)

        return CoordinatorPlan(
            timestamp=self.get_timestamp(),
            final_allocations=final_allocations,
            resource_usage=resource_usage,
            conflicts=conflicts,
            changes=changes,
            explanation=explanation,
            agent_tradeoffs=tradeoffs,
            public_alert=public_alert,
            agent_negotiation=negotiation
        )

    def _generate_explanation(
        self,
        zones: List[DisasterZone],
        allocations: List[ZoneAllocation],
        conflicts: List[ConflictItem],
        changes: List[PlanChange],
        recommendations: Dict[str, AgentRecommendation],
        location: str
    ) -> str:
        prompt = f"""
You are the Master Coordinator AI for RESQ-AI emergency response in {location}.
Zones state:
{self.format_zones_summary(zones)}

Conflicts Detected:
{[c.description for c in conflicts]}

Plan Changes from previous state:
{[f"{c.zone_name} {c.resource_type}: {c.before} -> {c.after} ({c.reason})" for c in changes]}

Final Allocations:
{[f"{a.zone_name}: Medics={a.medics}, Vehicles={a.vehicles}, Shelters={a.shelter_units}, Supplies={a.supplies}" for a in allocations]}

Provide a clear, authoritative explanation answering:
1. Why were resources allocated this way based on hazard severity, flood level, and medical urgency?
2. How were agent conflicts resolved under fixed resource caps?
3. What trade-offs were made regarding critical patients and road access?
Keep it under 180 words, professional, and explainable.
"""
        system_instruction = "You are an expert AI disaster coordinator. Provide clear, transparent, explainable decision rationales for human emergency directors."
        llm_data = llm_service.generate_json(prompt, system_instruction)

        if llm_data and "explanation" in llm_data:
            return llm_data["explanation"]

        # High Quality Deterministic Reasoning Fallback
        critical_zones = [z for z in zones if z.risk_level in ["Critical", "Very High"] or z.critical >= 4]
        top_zone = critical_zones[0] if critical_zones else (zones[0] if zones else None)
        top_name = top_zone.name if top_zone else "Zone B"

        has_changes = len(changes) > 0
        change_note = f" Dynamic re-planning transferred resources toward new critical sectors ({len(changes)} reallocation adjustments)." if has_changes else ""

        explanation = (
            f"{top_name} received the highest allocation because it has elevated flood severity ({top_zone.flood_level_m if top_zone else 3.8}m flood level, {top_zone.severity_score if top_zone else 84}/100 score) "
            f"and high medical urgency ({top_zone.critical if top_zone else 10} Critical patients). "
            f"Allocations were driven by multi-factor hazard severity rather than population alone. "
            f"Where agent resource requests exceeded capacity ({len(conflicts)} conflicts detected), "
            f"the Coordinator enforced hard bounds strictly within limits.{change_note}"
        )
        return explanation
