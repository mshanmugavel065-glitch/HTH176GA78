import re
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

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

KNOWN_CITIES = [
    "coimbatore", "chennai", "mumbai", "bengaluru", "kochi", "hyderabad", 
    "delhi", "ooty", "madurai", "kolkata", "pune", "ahmedabad", "jaipur", 
    "thiruvananthapuram", "mysuru", "salem", "trichy", "tirunelveli", "vellore"
]

KNOWN_DISASTERS = [
    "flood", "flooding", "earthquake", "cyclone", "landslide", "wildfire", 
    "tsunami", "chemical spill", "industrial accident", "storm", "hurricane"
]

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
        self.last_referenced_zone_id: Optional[str] = "zone-b"

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

        self.activity_logs = []
        self.agent_recommendations = {}
        self.current_plan = None
        self.is_pending_replan = False
        self.last_referenced_zone_id = "zone-b"

    def reset_scenario_for_new_location(self, new_location: str, disaster_type: Optional[str] = None):
        """Reset scenario state for a new city location to prevent cross-location data leakage."""
        self.location = new_location
        if disaster_type:
            self.situation_query = f"{disaster_type} affecting multiple sectors"

        self.load_initial_data()
        self.is_analyzed = True
        self._add_activity("system", "Location Scenario Initialized", f"Active response scenario set to {self.location} ({self.situation_query}).", "info")

    def extract_location_and_disaster(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        text_lower = text.lower().strip()
        extracted_loc = None
        extracted_disaster = None

        # 1. Match known city list
        for city in KNOWN_CITIES:
            if re.search(r'\b' + re.escape(city) + r'(?:\s*,\s*[a-zA-Z\s]+)?\b', text_lower):
                m = re.search(r'\b' + re.escape(city) + r'(?:\s*,\s*[a-zA-Z\s]+)?\b', text, re.IGNORECASE)
                if m:
                    extracted_loc = m.group(0).strip().title()
                    break

        # 2. Match patterns if not in known cities (e.g., "in Ooty", "around Salem", "switch to Chennai")
        if not extracted_loc:
            pats = [
                r'(?:in|near|around|at|for|switch to|location is|set location to)\s+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)?)',
                r'([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)?)\s+is\s+affected'
            ]
            for pat in pats:
                m = re.search(pat, text)
                if m:
                    cand = m.group(1).strip()
                    words = [w for w in cand.split() if w.lower() not in ["multiple", "areas", "sectors", "a", "the", "several", "some", "many", "all", "disaster", "flood", "cyclone", "earthquake"]]
                    if words:
                        extracted_loc = " ".join(words).title()
                        break

        # 3. Match disaster type
        for d in KNOWN_DISASTERS:
            if d in text_lower:
                extracted_disaster = "Flood" if "flood" in d else d.title()
                break

        return extracted_loc, extracted_disaster

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

        self.reset_scenario_for_new_location(loc_trimmed, sit_trimmed)
        self.situation_query = sit_trimmed

        self._add_activity("location", "Location Intelligence", f"Mapped geographic sectors for {self.location}", "info")
        self._add_activity("situation", "Situation Agent", f"Parsed disaster situation: '{self.situation_query}'", "info")

        # Run multi-agent pipeline
        self.run_full_pipeline(is_replan=False)

        # Welcome assistant message
        welcome_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="assistant",
            content=f"Understood. I'll use **{self.location}** as the active disaster-response location for this simulated scenario: *\"{self.situation_query}\"*\n\n- **Medical Triage**: Zone B has the highest priority with 10 critical patients.\n- **Road Access**: Zone C Road 3 is **BLOCKED**. Logistics Agent rerouted evacuation via Road 4.\n- **Coordinated Plan**: Synthesized under fixed bounds ({self.resources.vehicles} Vehicles, {self.resources.medics} Medics).\n\nWhat would you like to inspect or execute next?",
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent_name="Coordinator Agent",
            suggested_actions=["CREATE RESPONSE PLAN", "GENERATE PUBLIC ALERT", "SHOW RESOURCE CONFLICTS", "+ ADD NEW DISASTER ZONE"]
        )
        self.chat_history = [welcome_msg]

        return self.get_state()

    def run_full_pipeline(self, is_replan: bool = False) -> SystemState:
        prefix = "Dynamic Re-planning" if is_replan else "Response Planning"
        loc_str = self.location if self.location else "Active Scenario"
        self._add_activity("coordinator", f"Initiating {prefix}", f"Executing multi-agent negotiation for {len(self.zones)} zones in {loc_str}.", "info")

        # 1. Run Medical Agent
        self._add_activity("medical", "Medical Agent Triaging", "Prioritizing injured & critical casualty density...", "info")
        medical_rec = self.medical_agent.analyze(self.zones, self.resources)
        self.agent_recommendations["medical_agent"] = medical_rec

        # 2. Run Logistics Agent
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
            self.last_referenced_zone_id = "zone-d"
            self._add_activity("system", "⚠️ NEW DISASTER ZONE DETECTED", "Zone D (Hospital Landslide) added to crisis roster. Ready for Re-Planning.", "warning")
            
            asst_msg = ChatMessage(
                id=str(uuid.uuid4())[:8],
                sender="assistant",
                content=f"⚠️ **NEW DISASTER ZONE DETECTED IN {self.location.upper() if self.location else 'SCENARIO'}**\n\n**Zone D (Hospital Landslide)**: 8 Critical, 20 Injured, Evacuation Required.\n\nClick **[ RE-PLAN RESPONSE ]** or say 'Re-plan' to trigger multi-agent re-allocation.",
                timestamp=datetime.now().strftime("%H:%M:%S"),
                agent_name="Coordinator Agent",
                suggested_actions=["RE-PLAN RESPONSE", "SHOW RESOURCE CONFLICTS"]
            )
            self.chat_history.append(asst_msg)

        return self.get_state()

    def process_chat_message(self, user_text: str) -> SystemState:
        # Add user message to history
        user_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="user",
            content=user_text,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        self.chat_history.append(user_msg)

        text_lower = user_text.lower().strip()

        # STEP 1: PARSE LOCATION & DISASTER FROM NATURAL LANGUAGE FIRST
        extracted_loc, extracted_disaster = self.extract_location_and_disaster(user_text)

        print(f"[DEBUG] USER MESSAGE: {user_text}")
        print(f"[DEBUG] EXTRACTED LOCATION: {extracted_loc}")
        print(f"[DEBUG] EXTRACTED DISASTER: {extracted_disaster}")

        # STEP 2: IF NEW LOCATION EXTRACTED, UPDATE SCENARIO STATE BEFORE AGENT REASONING
        if extracted_loc and (extracted_loc != self.location or not self.is_analyzed):
            old_loc = self.location
            self.reset_scenario_for_new_location(extracted_loc, extracted_disaster or "Flood affecting multiple areas")
            
            reply = f"Understood. **{self.location}** is now the active disaster-response location for this simulated {self.situation_query}. I've initialized the 3 affected zones and prepared the multi-agent coordinator."
            asst_msg = ChatMessage(
                id=str(uuid.uuid4())[:8],
                sender="assistant",
                content=reply,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                agent_name="Coordinator Agent",
                suggested_actions=["CREATE RESPONSE PLAN", "WHICH ZONE IS MOST CRITICAL?", "GENERATE PUBLIC ALERT"]
            )
            self.chat_history.append(asst_msg)
            return self.get_state()

        # If location is still empty and user hasn't set one yet
        if not self.location and not self.is_analyzed:
            reply = "I’m ready to coordinate a disaster-response scenario. Tell me the location and disaster situation you want to analyze (e.g., 'Flood affecting multiple areas in Coimbatore')."
            asst_msg = ChatMessage(
                id=str(uuid.uuid4())[:8],
                sender="assistant",
                content=reply,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                agent_name="Coordinator Agent"
            )
            self.chat_history.append(asst_msg)
            return self.get_state()

        loc_str = self.location if self.location else "Active Location"

        # Check for resource constraint changes
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
            self._add_activity("system", "Resource Limit Set", f"Updated resource bounds to {self.resources.vehicles} vehicles and {self.resources.medics} medics.", "warning")

        # Intent Recognition Matrix

        # 1. ADD NEW DISASTER ZONE
        if "new disaster" in text_lower or "add zone d" in text_lower or "new incident" in text_lower or "landslide" in text_lower or "new emergency" in text_lower:
            self.add_preset_zone_d()
            return self.get_state()

        # 2. TRIGGER RE-PLANNING / DO IT
        elif "re-plan" in text_lower or "replan" in text_lower or text_lower == "do it" or "reallocate" in text_lower or "update plan" in text_lower:
            self.run_full_pipeline(is_replan=True)
            
            reply_text = (
                f"⚡ **DYNAMIC RE-PLANNING EXECUTED FOR {loc_str.upper()}**\n\n"
                f"The Medical, Logistics, and Communications agents re-evaluated priorities under fixed limits ({self.resources.vehicles} Vehicles, {self.resources.medics} Medics).\n\n"
                f"**WHY DID THE PLAN CHANGE?**\n{self.current_plan.explanation}"
            )
            actions = ["WHY DID THE PLAN CHANGE?", "GENERATE PUBLIC ALERT", "SHOW RESOURCE CONFLICTS"]

        # 3. GENERATE PUBLIC ALERT
        elif "alert" in text_lower or "public message" in text_lower or "broadcast" in text_lower or "evacuation message" in text_lower:
            if not self.current_plan:
                self.run_full_pipeline(is_replan=False)
            
            alert = self.current_plan.public_alert
            reply_text = (
                f"📢 **PUBLIC EMERGENCY ALERT DRAFT — {loc_str.upper()}**\n\n"
                f"**Title**: {alert.title}\n"
                f"**Target Sector**: {alert.target_zone}\n"
                f"**Approved Route**: {alert.approved_route}\n\n"
                f"**Message Body**:\n\"{alert.message}\"\n\n"
                f"*Label*: `{alert.label}`"
            )
            actions = ["COPY ALERT", "WHY THIS PLAN?", "+ ADD NEW DISASTER ZONE"]

        # 4. CREATE / SHOW RESPONSE PLAN
        elif "create" in text_lower and "plan" in text_lower or "make a plan" in text_lower or "response plan" in text_lower or "what should we do" in text_lower or "give me an emergency plan" in text_lower or updated_resources:
            self.run_full_pipeline(is_replan=bool(self.current_plan))
            
            plan_summary = []
            for a in self.current_plan.final_allocations:
                plan_summary.append(f"- **{a.zone_name}**: 🚑 {a.vehicles} Vehicles | 🏥 {a.medics} Medics | 🏠 {a.shelter_units} Shelters | Priority: **{a.priority}**")

            reply_text = (
                f"🧠 **COORDINATED RESPONSE PLAN FOR {loc_str.upper()}**\n\n"
                + "\n".join(plan_summary) +
                f"\n\n📊 **RESOURCE USAGE**: Vehicles: {self.current_plan.resource_usage['vehicles']['allocated']}/{self.resources.vehicles} | Medics: {self.current_plan.resource_usage['medics']['allocated']}/{self.resources.medics}\n\n"
                f"💡 **WHY THIS PLAN?**\n{self.current_plan.explanation}"
            )
            actions = ["+ ADD NEW DISASTER ZONE", "GENERATE PUBLIC ALERT", "WHY THIS PLAN?"]

        # 5. ASK CRITICAL ZONE / MEDICAL PRIORITY
        elif "critical" in text_lower or "medical support" in text_lower or "medical priority" in text_lower or "most urgent" in text_lower:
            crit_zone = max(self.zones, key=lambda z: (z.critical, z.injured))
            self.last_referenced_zone_id = crit_zone.id
            reply_text = f"**{crit_zone.name}** currently has the highest medical priority in **{loc_str}** because it has **{crit_zone.critical} critical patients** and {crit_zone.injured} total injured casualties."
            actions = ["WHY?", "HOW MANY VEHICLES ARE AVAILABLE?", "CREATE RESPONSE PLAN"]

        # 6. ASK WHY / EXPLAIN DECISION
        elif "why" in text_lower or "explain" in text_lower or "tradeoff" in text_lower:
            ref_zone = next((z for z in self.zones if z.id == self.last_referenced_zone_id), self.zones[0])
            if self.current_plan:
                exp = self.current_plan.explanation
            else:
                exp = f"{ref_zone.name} in {loc_str} received priority because it has {ref_zone.critical} critical patients. Since resources are strictly limited ({self.resources.medics} medics available), the Coordinator prioritized high-severity trauma sectors."
            
            reply_text = f"💡 **EXPLAINABILITY RATIONALE**\n\n{exp}"
            actions = ["HOW MANY VEHICLES ARE LEFT?", "+ ADD NEW DISASTER ZONE"]

        # 7. ASK RESOURCE COUNT / VEHICLES LEFT
        elif "vehicle" in text_lower or "medic" in text_lower or "resource" in text_lower or "left" in text_lower or "remaining" in text_lower or "available" in text_lower:
            alloc_veh = sum(a.vehicles for a in self.current_plan.final_allocations) if self.current_plan else 0
            alloc_med = sum(a.medics for a in self.current_plan.final_allocations) if self.current_plan else 0
            unalloc_veh = max(0, self.resources.vehicles - alloc_veh)
            unalloc_med = max(0, self.resources.medics - alloc_med)

            if "what if" in text_lower or "only have 3" in text_lower or "reduce" in text_lower:
                reply_text = f"With only {self.resources.vehicles} vehicles available in {loc_str}, the current allocation would exceed capacity. I recommend re-planning the vehicle allocation across all affected zones."
                actions = ["RE-PLAN RESPONSE", "SHOW RESOURCE CONFLICTS"]
            else:
                reply_text = f"We currently have **{self.resources.vehicles} total rescue vehicles** ({alloc_veh} allocated across active zones in {loc_str}, {unalloc_veh} unallocated) and **{self.resources.medics} total medics** ({alloc_med} allocated)."
                actions = ["CREATE RESPONSE PLAN", "WHAT IF WE ONLY HAVE 3 VEHICLES?"]

        # 8. ASK ROAD CONDITIONS / EVACUATION ROUTES
        elif "road" in text_lower or "blocked" in text_lower or "route" in text_lower or "evacuation" in text_lower:
            blocked = [z for z in self.zones if z.road_status == "Blocked"]
            congested = [z for z in self.zones if z.road_status == "Congested"]
            
            blocked_str = ", ".join([f"{z.name} ({z.road_name})" for z in blocked]) or "None"
            congested_str = ", ".join([f"{z.name} ({z.road_name})" for z in congested]) or "None"

            reply_text = f"🛣️ **ROAD NETWORK STATUS ({loc_str.upper()})**:\n- **Blocked Roads**: {blocked_str}\n- **Congested Roads**: {congested_str}\n- **Alternate Bypass**: Zone C Road 3 is Blocked; Logistics Agent rerouted traffic via **Road 4 (North Ridge Bypass)**."
            actions = ["GENERATE PUBLIC ALERT", "CREATE RESPONSE PLAN"]

        # 9. ASK SPECIFIC ZONE DETAILS
        elif "zone a" in text_lower or "zone b" in text_lower or "zone c" in text_lower or "zone d" in text_lower:
            target_id = "zone-a" if "zone a" in text_lower else ("zone-b" if "zone b" in text_lower else ("zone-c" if "zone c" in text_lower else "zone-d"))
            self.last_referenced_zone_id = target_id
            target_zone = next((z for z in self.zones if z.id == target_id), None)

            if target_zone:
                alloc = next((a for a in (self.current_plan.final_allocations if self.current_plan else []) if a.zone_id == target_id), None)
                alloc_str = f"Assigned: 🚑 {alloc.vehicles} Vehicles, 🏥 {alloc.medics} Medics." if alloc else "No resources assigned yet."
                reply_text = f"📍 **{target_zone.name} STATUS ({loc_str})**:\n- Population: {target_zone.population}\n- Casualties: {target_zone.injured} Injured ({target_zone.critical} Critical)\n- Risk: **{target_zone.risk}**\n- Road Status: {target_zone.road_name} ({target_zone.road_status})\n- {alloc_str}"
            else:
                reply_text = f"That zone is not currently in the active crisis map for {loc_str}."
            actions = ["WHY?", "CREATE RESPONSE PLAN"]

        # 10. SHOW RESOURCE CONFLICTS
        elif "conflict" in text_lower:
            if self.current_plan and self.current_plan.conflicts:
                conf_descs = "\n".join([f"- **{c.resource_type.upper()}**: {c.description}" for c in self.current_plan.conflicts])
                reply_text = f"⚠️ **RESOURCE CONFLICTS DETECTED IN {loc_str.upper()}**:\n{conf_descs}\n\n**Coordinator Resolution**: {self.current_plan.agent_negotiation.coordinator_resolution if self.current_plan.agent_negotiation else 'Allocations scaled strictly to fixed bounds.'}"
            else:
                reply_text = f"No active resource conflicts in {loc_str}. All allocations are within the fixed resource limits."
            actions = ["CREATE RESPONSE PLAN", "RE-PLAN RESPONSE"]

        # 11. GENERAL CONVERSATIONAL / LLM GENERATED
        else:
            system_ctx = f"Location: {loc_str}. Situation: {self.situation_query}. Zones: {[z.name for z in self.zones]}. Resources: {self.resources.vehicles} vehicles, {self.resources.medics} medics."
            llm_text = llm_service.generate_chat_response(system_ctx, user_text, [m.dict() for m in self.chat_history])
            
            if llm_text:
                reply_text = llm_text
            else:
                reply_text = f"I am monitoring **{loc_str}** with 4 core agents (Medical, Logistics, Communications, Coordinator). You can ask me about critical zones, road blockages, resource counts, public alerts, or response plans."
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
