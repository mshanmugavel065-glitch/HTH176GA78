import re
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from models import (
    DisasterZone, ResourcePool, SystemState, 
    ActivityLog, AgentRecommendation, CoordinatorPlan, ChatMessage, PublicAlert
)
from agents.location_agent import LocationAgent
from agents.situation_agent import SituationAgent
from agents.medical_agent import MedicalAgent
from agents.logistics_agent import LogisticsAgent
from agents.risk_agent import RiskAgent
from agents.communication_agent import CommunicationAgent
from agents.coordinator_agent import CoordinatorAgent
from services.llm_service import llm_service

class ScenarioManager:
    def __init__(self):
        self.location_agent = LocationAgent()
        self.situation_agent = SituationAgent()
        self.medical_agent = MedicalAgent()
        self.logistics_agent = LogisticsAgent()
        self.risk_agent = RiskAgent()
        self.communication_agent = CommunicationAgent()
        self.coordinator_agent = CoordinatorAgent()

        self.location = ""
        self.situation_query = ""
        self.resources = ResourcePool(vehicles=5, medics=10, shelters=3, supplies=100)
        self.zones: List[DisasterZone] = []
        self.current_plan: Optional[CoordinatorPlan] = None
        self.activity_logs: List[ActivityLog] = []
        self.agent_recommendations: Dict[str, AgentRecommendation] = {}
        self.chat_history: List[ChatMessage] = []
        self.is_analyzed = False
        self.is_pending_replan = False

        self.load_initial_data()

    def load_initial_data(self):
        try:
            with open("data/disaster_data.json", "r") as f:
                data = json.load(f)
                res = data.get("resources", {})
                self.resources = ResourcePool(
                    vehicles=res.get("vehicles", 5),
                    medics=res.get("medics", 10),
                    shelters=res.get("shelters", 3),
                    supplies=res.get("supplies", 100)
                )
                self.zones = [DisasterZone(**z) for z in data.get("initial_zones", [])]
        except Exception:
            self.resources = ResourcePool(vehicles=5, medics=10, shelters=3, supplies=100)
            self.zones = [
                DisasterZone(id="zone-a", name="Zone A", population=80, injured=12, critical=4, risk="High", evacuation_required=False, road_name="Road 1 -> Hospital", road_status="Open", alternate_route="Direct Highway 1", description="Residential district with partial grid outage."),
                DisasterZone(id="zone-b", name="Zone B", population=40, injured=25, critical=10, risk="Critical", evacuation_required=True, road_name="Road 2 -> Shelter", road_status="Congested", alternate_route="River Bypass Road", description="Industrial river sector with chemical hazard."),
                DisasterZone(id="zone-c", name="Zone C", population=100, injured=8, critical=2, risk="High", evacuation_required=True, road_name="Road 3 -> Shelter", road_status="Blocked", alternate_route="Road 4 (North Ridge Bypass)", description="Flash flood evacuation sector. Primary Road 3 is BLOCKED.")
            ]

        self.location = ""
        self.situation_query = ""
        self.activity_logs = []
        self.agent_recommendations = {}
        self.chat_history = []
        self.current_plan = None
        self.is_analyzed = False
        self.is_pending_replan = False
        self._add_activity("system", "System Initialized", "RESQ-AI Command Center ready for Response Simulation.", "info")

    def _add_activity(self, agent: str, action: str, details: str, log_type: str = "info"):
        log = ActivityLog(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent=agent,
            action=action,
            details=details,
            type=log_type
        )
        self.activity_logs.insert(0, log)
        if len(self.activity_logs) > 50:
            self.activity_logs.pop()

    def get_state(self) -> SystemState:
        return SystemState(
            location=self.location,
            situation_query=self.situation_query,
            data_source_mode="SIMULATED DISASTER SCENARIO",
            zones=self.zones,
            resources=self.resources,
            current_plan=self.current_plan,
            agent_activity=self.activity_logs,
            agent_recommendations=self.agent_recommendations,
            chat_history=self.chat_history,
            active_agents_count=4,
            is_analyzed=self.is_analyzed,
            is_pending_replan=self.is_pending_replan,
            last_updated=datetime.now().strftime("%H:%M:%S")
        )

    def analyze_location_and_situation(self, location: str, situation: str) -> SystemState:
        loc_trimmed = location.strip() if location else ""
        sit_trimmed = situation.strip() if situation else ""

        if not loc_trimmed:
            raise ValueError("Please enter a disaster-response location.")
        if not sit_trimmed:
            raise ValueError("Please describe the disaster situation.")

        self.location = loc_trimmed
        self.situation_query = sit_trimmed
        self.is_analyzed = True

        self._add_activity("location", "Location Intelligence", f"Mapped geographic sectors for {self.location}", "info")
        self._add_activity("situation", "Situation Agent", f"Parsed disaster situation: '{self.situation_query}'", "info")

        # Run multi-agent pipeline
        self.run_full_pipeline(is_replan=False)

        # Welcome chat message with active location
        welcome_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="assistant",
            content=f"📍 **LOCATION SET**: {self.location}\n\n**Simulated Disaster Scenario**: *\"{self.situation_query}\"*\n\n**Multi-Agent Coordination Active:**\n- 🩺 **Medical Agent**: Prioritizing Zone B (10 Critical patients)\n- 🚑 **Logistics Agent**: Road 3 is **BLOCKED**. Alternate route Road 4 assigned\n- 📢 **Communications Agent**: Evacuation alert drafted\n- 🧠 **Coordinator Agent**: Response plan synthesized under fixed resource limits ({self.resources.vehicles} Vehicles, {self.resources.medics} Medics)\n\nAsk me any questions or click **[ + ADD NEW DISASTER ZONE ]** to simulate an escalating crisis.",
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent_name="Coordinator Agent",
            suggested_actions=["▶ START RESPONSE SIMULATION", "CREATE RESPONSE PLAN", "GENERATE PUBLIC ALERT", "+ ADD NEW DISASTER ZONE"]
        )
        self.chat_history = [welcome_msg]

        return self.get_state()

    def run_full_pipeline(self, is_replan: bool = False) -> SystemState:
        prefix = "Dynamic Re-planning" if is_replan else "Response Planning"
        loc_str = self.location or "Active Scenario"
        self._add_activity("coordinator", f"Initiating {prefix}", f"Executing multi-agent negotiation for {len(self.zones)} zones in {loc_str}.", "info")

        # 1. Run Medical Agent
        self._add_activity("medical", "Medical Agent Triaging", "Prioritizing injured & critical casualty density...", "info")
        medical_rec = self.medical_agent.analyze(self.zones, self.resources)
        self.agent_recommendations["medical_agent"] = medical_rec

        # 2. Run Logistics Agent (Road network & vehicle allocation)
        self._add_activity("logistics", "Logistics Agent Analyzing", "Evaluating road accessibility & vehicle routing...", "info")
        logistics_rec = self.logistics_agent.analyze(self.zones, self.resources)
        self.agent_recommendations["logistics_agent"] = logistics_rec

        # 3. Run Communication Agent
        self._add_activity("communication", "Communications Agent Advising", "Drafting public safety alerts and evacuation advisories...", "info")
        comm_rec = self.communication_agent.analyze(self.zones, self.resources)
        self.agent_recommendations["communication_agent"] = comm_rec

        # 4. Run Coordinator Agent
        self._add_activity("coordinator", "Coordinator Agent Synthesizing", "Resolving multi-agent conflicts & validating hard resource bounds...", "info")
        new_plan = self.coordinator_agent.synthesize(
            zones=self.zones,
            resources=self.resources,
            recommendations=self.agent_recommendations,
            previous_plan=self.current_plan
        )

        if new_plan.conflicts:
            for c in new_plan.conflicts:
                self._add_activity("coordinator", "Resource Conflict Detected", c.description, "conflict")
                self._add_activity("coordinator", "Conflict Resolved", c.resolution, "success")

        self.current_plan = new_plan
        self.is_pending_replan = False
        self._add_activity("coordinator", "Response Plan Validated", f"Plan validated for {loc_str} under fixed limits ({self.resources.vehicles} vehicles, {self.resources.medics} medics).", "success")

        return self.get_state()

    def add_preset_zone_d(self) -> SystemState:
        """Adds Zone D but DOES NOT automatically re-plan until user triggers RE-PLAN RESPONSE."""
        zone_d = DisasterZone(
            id="zone-d",
            name="Zone D",
            population=60,
            injured=20,
            critical=8,
            risk="Critical",
            evacuation_required=True,
            road_name="Road 5 -> Hospital Precinct",
            road_status="Blocked",
            alternate_route="South Ridge Relief Track",
            description="Newly detected emergency: Hospital precinct hit by secondary landslide."
        )
        existing_d = any(z.id == "zone-d" for z in self.zones)
        if not existing_d:
            self.zones.append(zone_d)
            self.is_pending_replan = True
            self._add_activity("system", "⚠️ NEW DISASTER ZONE DETECTED", "Zone D (Hospital Landslide) added to crisis roster. Ready for Re-Planning.", "warning")
            
            # Notify chatbot
            asst_msg = ChatMessage(
                id=str(uuid.uuid4())[:8],
                sender="assistant",
                content=f"⚠️ **NEW DISASTER ZONE DETECTED IN {self.location.upper() if self.location else 'SCENARIO'}**\n\n**Zone D (Hospital Landslide)**: 8 Critical, 20 Injured, Evacuation Required.\n\nClick **[ RE-PLAN RESPONSE ]** to trigger multi-agent re-allocation.",
                timestamp=datetime.now().strftime("%H:%M:%S"),
                agent_name="Coordinator Agent",
                suggested_actions=["RE-PLAN RESPONSE", "SHOW RESOURCE CONFLICTS"]
            )
            self.chat_history.append(asst_msg)

        return self.get_state()

    def process_chat_message(self, user_text: str) -> SystemState:
        user_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="user",
            content=user_text,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        self.chat_history.append(user_msg)

        text_lower = user_text.lower()
        loc_str = self.location if self.location else "Active Location"

        # Parse resource constraint mentions (e.g. "3 vehicles", "6 medics")
        veh_match = re.search(r'(\d+)\s*(?:rescue\s*)?vehicles?', text_lower)
        med_match = re.search(r'(\d+)\s*medics?', text_lower)

        updated_resources = False
        if veh_match:
            new_veh = int(veh_match.group(1))
            self.resources.vehicles = new_veh
            updated_resources = True
        if med_match:
            new_med = int(med_match.group(1))
            self.resources.medics = new_med
            updated_resources = True

        if updated_resources:
            self._add_activity("system", "Resource Limit Set", f"Set resource bounds to {self.resources.vehicles} vehicles and {self.resources.medics} medics.", "warning")

        if "new disaster" in text_lower or "add zone d" in text_lower or "new incident" in text_lower or "landslide" in text_lower:
            self.add_preset_zone_d()
            return self.get_state()

        elif "re-plan" in text_lower or "replan" in text_lower:
            self.run_full_pipeline(is_replan=True)
            reply_text = (
                f"⚡ **DYNAMIC RE-PLANNING EXECUTED FOR {loc_str.upper()}**\n\n"
                f"The Medical, Logistics, and Communications agents re-evaluated priorities. "
                f"Resource conflicts were resolved by transferring medical resources to Zone D while enforcing the fixed cap of {self.resources.medics} medics.\n\n"
                f"**WHY DID THE PLAN CHANGE?**\n{self.current_plan.explanation}"
            )
            actions = ["WHY DID THE PLAN CHANGE?", "GENERATE PUBLIC ALERT", "SHOW RESOURCE CONFLICTS"]

        elif "alert" in text_lower or "public message" in text_lower or "broadcast" in text_lower:
            if not self.current_plan:
                self.run_full_pipeline(is_replan=False)
            
            alert = self.current_plan.public_alert
            reply_text = (
                f"📢 **PUBLIC EMERGENCY ALERT DRAFT**\n\n"
                f"**Title**: {alert.title}\n"
                f"**Target Zone**: {alert.target_zone}\n"
                f"**Approved Route**: {alert.approved_route}\n\n"
                f"**Message Body**:\n\"{alert.message}\"\n\n"
                f"*Label*: `{alert.label}`"
            )
            actions = ["COPY ALERT", "WHY THIS PLAN?", "+ ADD NEW DISASTER ZONE"]

        elif "plan" in text_lower or "what should we do" in text_lower or "allocate" in text_lower or updated_resources:
            self.run_full_pipeline(is_replan=bool(self.current_plan))
            
            plan_summary = []
            for a in self.current_plan.final_allocations:
                plan_summary.append(f"- **{a.zone_name}**: 🚑 {a.vehicles} Vehicles | 🏥 {a.medics} Medics | 🏠 {a.shelter_units} Shelters | Priority: **{a.priority}**")

            reply_text = (
                f"🧠 **COORDINATED RESPONSE PLAN FOR {loc_str.upper()}**\n\n"
                + "\n".join(plan_summary) +
                f"\n\n📊 **RESOURCE FEASIBILITY**: Vehicles: {self.current_plan.resource_usage['vehicles']['allocated']}/{self.resources.vehicles} | Medics: {self.current_plan.resource_usage['medics']['allocated']}/{self.resources.medics}\n\n"
                f"💡 **WHY THIS PLAN?**\n{self.current_plan.explanation}"
            )
            actions = ["+ ADD NEW DISASTER ZONE", "GENERATE PUBLIC ALERT", "WHY THIS PLAN?"]

        elif "why" in text_lower or "explain" in text_lower or "tradeoff" in text_lower:
            exp = self.current_plan.explanation if self.current_plan else "Zone B received highest medical priority due to 10 critical patients. Zone C received evacuation routing priority because Road 3 is BLOCKED."
            reply_text = f"💡 **EXPLAINABLE AI DECISION RATIONALE**\n\n{exp}\n\n**Multi-Agent Negotiation**: Medical Agent requested priority medics for Zone B; Logistics Agent rerouted evacuation via Road 4; Coordinator enforced hard resource limits."
            actions = ["GENERATE PUBLIC ALERT", "+ ADD NEW DISASTER ZONE"]

        else:
            reply_text = f"RESQ-AI Command Center active for **{loc_str}**. 4 core agents (Medical, Logistics, Communications, Coordinator) monitored. Current resource bounds: {self.resources.vehicles} vehicles, {self.resources.medics} medics. How can I assist?"
            actions = ["CREATE RESPONSE PLAN", "GENERATE PUBLIC ALERT", "+ ADD NEW DISASTER ZONE"]

        asst_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="assistant",
            content=reply_text,
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent_name="Coordinator Agent",
            suggested_actions=actions
        )
        self.chat_history.append(asst_msg)

        return self.get_state()

    def reset_system(self) -> SystemState:
        self.load_initial_data()
        return self.get_state()

scenario_manager = ScenarioManager()
