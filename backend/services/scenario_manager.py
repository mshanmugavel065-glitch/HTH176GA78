import re
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from models import (
    DisasterZone, ResourcePool, SystemState, 
    ActivityLog, AgentRecommendation, CoordinatorPlan, ChatMessage, PublicAlert,
    DatasetMetadata, DisasterIntelligenceResult, PlanDifference
)
from agents.location_agent import LocationAgent
from agents.situation_agent import SituationAgent
from agents.disaster_intelligence_agent import DisasterIntelligenceAgent
from agents.medical_agent import MedicalAgent
from agents.logistics_agent import LogisticsAgent
from agents.communication_agent import CommunicationAgent
from agents.coordinator_agent import CoordinatorAgent
from services.llm_service import llm_service
from services.dataset_service import dataset_service

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
        self.intelligence_agent = DisasterIntelligenceAgent()
        self.medical_agent = MedicalAgent()
        self.logistics_agent = LogisticsAgent()
        self.communication_agent = CommunicationAgent()
        self.coordinator_agent = CoordinatorAgent()

        self.location = ""
        self.disaster_type = "Flood"
        self.situation_query = ""
        self.data_source_mode = "SIMULATED DISASTER SCENARIO"
        self.dataset_metadata: Optional[DatasetMetadata] = None
        self.intelligence_result: Optional[DisasterIntelligenceResult] = None

        self.resources = ResourcePool(vehicles=5, medics=10, shelters=3, supplies=100)
        self.zones: List[DisasterZone] = []
        self.current_plan: Optional[CoordinatorPlan] = None
        self.previous_plan: Optional[CoordinatorPlan] = None
        self.plan_differences: List[PlanDifference] = []
        
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
                DisasterZone(id="zone-a", name="Zone A", population=80, injured=12, critical=4, risk="High", rainfall_mm=140, flood_level_m=1.8, affected_area_km2=10.5, road_access=0.85, severity_score=58.0, risk_level="High", evacuation_required=False, road_name="Road 1 -> Hospital", road_status="Open", alternate_route="Direct Highway 1", description="Residential sector with minor grid disruption."),
                DisasterZone(id="zone-b", name="Zone B", population=40, injured=25, critical=10, risk="Critical", rainfall_mm=240, flood_level_m=3.8, affected_area_km2=25.0, road_access=0.30, severity_score=84.0, risk_level="Critical", evacuation_required=True, road_name="Road 2 -> Shelter", road_status="Congested", alternate_route="River Bypass Road", description="Industrial river sector with chemical hazard."),
                DisasterZone(id="zone-c", name="Zone C", population=100, injured=8, critical=2, risk="High", rainfall_mm=180, flood_level_m=2.4, affected_area_km2=15.0, road_access=0.20, severity_score=72.0, risk_level="Very High", evacuation_required=True, road_name="Road 3 -> Shelter", road_status="Blocked", alternate_route="Road 4 (North Ridge Bypass)", description="Low-lying coastal sector flooded. Primary Road 3 is BLOCKED.")
            ]

        self.activity_logs = []
        self.agent_recommendations = {}
        self.current_plan = None
        self.previous_plan = None
        self.plan_differences = []
        self.is_pending_replan = False
        self.last_referenced_zone_id = "zone-b"
        self.data_source_mode = "SIMULATED DISASTER SCENARIO"
        self.dataset_metadata = DatasetMetadata(
            filename="Simulated Hazard Data",
            data_type="SIMULATED DISASTER SCENARIO",
            columns_detected=["location", "rainfall_mm", "flood_level_m", "affected_area_km2", "injured", "critical_patients", "road_access"],
            row_count=len(self.zones),
            warnings=[]
        )

    def reset_scenario_for_new_location(self, new_location: str, disaster_type: Optional[str] = None):
        """Reset scenario state for a new city location to prevent cross-location data leakage."""
        self.location = new_location
        if disaster_type:
            self.disaster_type = disaster_type.title() if "flood" not in disaster_type.lower() else "Flood"
            self.situation_query = f"{disaster_type} affecting multiple sectors"

        self.load_initial_data()
        self.is_analyzed = True
        self._add_activity("system", "Location Scenario Initialized", f"Active response scenario set to {self.location} ({self.situation_query}).", "info")

    def upload_dataset(self, file_bytes: bytes, filename: str) -> SystemState:
        meta, parsed_zones = dataset_service.process_file_content(file_bytes, filename)
        self.dataset_metadata = meta
        self.data_source_mode = "UPLOADED DATASET"
        self.zones = parsed_zones
        self.is_analyzed = True

        self._add_activity("dataset", "Dataset Uploaded & Parsed", f"Loaded '{filename}' with {len(parsed_zones)} zones ({len(meta.columns_detected)} indicators detected).", "success")

        # Run pipeline with new dataset
        self.run_full_pipeline(is_replan=False)

        asst_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="assistant",
            content=f"📁 **DATASET LOADED**: '{filename}' ({len(parsed_zones)} disaster sectors parsed).\n\n"
                    f"- **Indicators Detected**: {', '.join(meta.columns_detected[:6])}\n"
                    f"- **Highest Severity Sector**: {self.intelligence_result.priority_zone_name if self.intelligence_result else 'Zone B'} "
                    f"(Score: {self.intelligence_result.overall_severity_score if self.intelligence_result else 84}/100).\n"
                    f"{'⚠️ *' + meta.warnings[0] + '*' if meta.warnings else ''}",
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent_name="Disaster Intelligence Agent",
            suggested_actions=["CREATE RESPONSE PLAN", "WHICH ZONE IS HIGHEST RISK?", "GENERATE PUBLIC ALERT"]
        )
        self.chat_history.append(asst_msg)

        return self.get_state()

    def simulate_hazard_update(self, rainfall_increase: float = 50.0, flood_increase: float = 0.5) -> SystemState:
        """Simulate dynamic environmental hazard changes (e.g. rainfall surge)."""
        for zone in self.zones:
            zone.rainfall_mm += rainfall_increase
            zone.flood_level_m = round(zone.flood_level_m + flood_increase, 2)
            if zone.flood_level_m >= 3.0:
                zone.evacuation_required = True

        self._add_activity("system", "🌧️ HAZARD TELEMETRY UPDATE", f"Rainfall increased by +{rainfall_increase}mm across all sectors. Flood levels elevated.", "warning")
        self.is_pending_replan = True

        # Re-run disaster intelligence analysis
        intel_res, intel_rec = self.intelligence_agent.analyze_disaster(self.zones, self.location or "Active Scenario", self.disaster_type)
        self.intelligence_result = intel_res
        self.agent_recommendations["disaster_intelligence_agent"] = intel_rec

        asst_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="assistant",
            content=f"🌧️ **ENVIRONMENTAL HAZARD UPDATE ({self.location or 'SCENARIO'})**\n\n"
                    f"Rainfall increased by **+{rainfall_increase}mm**. Peak flood level reached **{intel_res.max_flood_level_m}m**.\n"
                    f"Overall Prototype Severity Score increased to **{intel_res.overall_severity_score}/100 ({intel_res.overall_risk_level})**.\n\n"
                    f"Click **[ 🔄 RE-PLAN RESPONSE ]** to trigger multi-agent re-allocation.",
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent_name="Disaster Intelligence Agent",
            suggested_actions=["RE-PLAN RESPONSE", "WHY DID THE SEVERITY INCREASE?"]
        )
        self.chat_history.append(asst_msg)

        return self.get_state()

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

        # 2. Match patterns if not in known cities
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
            disaster_type=self.disaster_type,
            situation_query=self.situation_query,
            data_source_mode=self.data_source_mode,
            dataset_metadata=self.dataset_metadata,
            intelligence_result=self.intelligence_result,
            zones=self.zones,
            resources=self.resources,
            current_plan=self.current_plan,
            previous_plan=self.previous_plan,
            plan_differences=self.plan_differences,
            agent_activity=self.activity_logs,
            agent_recommendations=self.agent_recommendations,
            chat_history=self.chat_history,
            active_agents_count=5,
            is_analyzed=self.is_analyzed,
            is_pending_replan=self.is_pending_replan,
            last_updated=datetime.now().strftime("%H:%M:%S")
        )

    def analyze_location_and_situation(self, location: str, situation: str) -> SystemState:
        loc_trimmed = location.strip() if location else ""
        sit_trimmed = situation.strip() if situation else ""

        if not loc_trimmed:
            raise ValueError("Which location should I analyze? Please provide a city or region.")
        if not sit_trimmed:
            raise ValueError("Please describe the disaster situation.")

        self.reset_scenario_for_new_location(loc_trimmed, sit_trimmed)
        self.situation_query = sit_trimmed

        self._add_activity("location", "Location Intelligence", f"Mapped geographic sectors for {self.location}", "info")
        self._add_activity("situation", "Situation Agent", f"Parsed disaster situation: '{self.situation_query}'", "info")

        # Run multi-agent pipeline
        self.run_full_pipeline(is_replan=False)

        top_zone = self.intelligence_result.priority_zone_name if self.intelligence_result else "Zone B"
        top_score = self.intelligence_result.overall_severity_score if self.intelligence_result else 84.0

        welcome_msg = ChatMessage(
            id=str(uuid.uuid4())[:8],
            sender="assistant",
            content=f"Understood. **{self.location}** is set as the active disaster-response location for this scenario: *\"{self.situation_query}\"*\n\n"
                    f"- **Disaster Intelligence**: Prototype Severity Score **{top_score}/100**. Priority Sector: **{top_zone}**.\n"
                    f"- **Medical Triage**: Prioritizing sectors with high critical patients.\n"
                    f"- **Road Network**: Zone C Road 3 is **BLOCKED**. Logistics Agent rerouted via Road 4.\n"
                    f"- **Resource Caps**: Enforced under fixed bounds ({self.resources.vehicles} Vehicles, {self.resources.medics} Medics).\n\n"
                    f"What would you like to inspect or execute next?",
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent_name="Coordinator Agent",
            suggested_actions=["CREATE RESPONSE PLAN", "GENERATE PUBLIC ALERT", "SHOW RESOURCE CONFLICTS", "+ ADD NEW DISASTER ZONE"]
        )
        self.chat_history = [welcome_msg]

        return self.get_state()

    def run_full_pipeline(self, is_replan: bool = False) -> SystemState:
        prefix = "Dynamic Re-planning" if is_replan else "Response Planning"
        loc_str = self.location if self.location else "Active Scenario"

        if is_replan and self.current_plan:
            self.previous_plan = self.current_plan

        self._add_activity("coordinator", f"Initiating {prefix}", f"Executing 5-agent coordination pipeline for {len(self.zones)} sectors in {loc_str}.", "info")

        # 1. Run Disaster Intelligence Agent
        self._add_activity("disaster_intelligence", "Disaster Intelligence Analyzing", "Evaluating rainfall, flood level, affected area & medical urgency...", "info")
        intel_res, intel_rec = self.intelligence_agent.analyze_disaster(self.zones, loc_str, self.disaster_type)
        self.intelligence_result = intel_res
        self.agent_recommendations["disaster_intelligence_agent"] = intel_rec

        # 2. Run Medical Agent
        self._add_activity("medical", "Medical Agent Triaging", "Prioritizing critical trauma casualties & field medics...", "info")
        medical_rec = self.medical_agent.analyze(self.zones, self.resources)
        self.agent_recommendations["medical_agent"] = medical_rec

        # 3. Run Logistics Agent
        self._add_activity("logistics", "Logistics Agent Analyzing", "Evaluating road accessibility & rescue fleet routing...", "info")
        logistics_rec = self.logistics_agent.analyze(self.zones, self.resources)
        self.agent_recommendations["logistics_agent"] = logistics_rec

        # 4. Run Communication Agent
        self._add_activity("communication", "Communications Agent Advising", "Drafting public safety alerts for active location...", "info")
        comm_rec = self.communication_agent.analyze(self.zones, self.resources)
        self.agent_recommendations["communication_agent"] = comm_rec

        # 5. Run Coordinator Agent
        self._add_activity("coordinator", "Coordinator Agent Synthesizing", "Resolving multi-agent conflicts & validating hard resource bounds...", "info")
        new_plan = self.coordinator_agent.synthesize(
            zones=self.zones,
            resources=self.resources,
            recommendations=self.agent_recommendations,
            previous_plan=self.previous_plan,
            location=loc_str,
            disaster_type=self.disaster_type
        )

        if new_plan.conflicts:
            for c in new_plan.conflicts:
                self._add_activity("coordinator", "Resource Conflict Detected", c.description, "conflict")
                self._add_activity("coordinator", "Conflict Resolved", c.resolution, "success")

        # Calculate BEFORE vs AFTER differences if re-planning occurred
        if is_replan and self.previous_plan and self.previous_plan.final_allocations:
            diffs: List[PlanDifference] = []
            prev_alloc_map = {a.zone_id: a for a in self.previous_plan.final_allocations}
            for curr_alloc in new_plan.final_allocations:
                prev_alloc = prev_alloc_map.get(curr_alloc.zone_id)
                curr_zone = next((z for z in self.zones if z.id == curr_alloc.zone_id), None)
                before_risk = prev_alloc.priority if prev_alloc else "Low"
                after_risk = curr_alloc.priority
                before_veh = prev_alloc.vehicles if prev_alloc else 0
                after_veh = curr_alloc.vehicles
                before_med = prev_alloc.medics if prev_alloc else 0
                after_med = curr_alloc.medics

                reason_text = curr_alloc.reason or "Resource re-allocation based on updated hazard severity."
                diffs.append(PlanDifference(
                    zone_id=curr_alloc.zone_id,
                    zone_name=curr_alloc.zone_name,
                    before_risk=before_risk,
                    after_risk=after_risk,
                    before_priority=before_risk,
                    after_priority=after_risk,
                    before_vehicles=before_veh,
                    after_vehicles=after_veh,
                    before_medics=before_med,
                    after_medics=after_med,
                    reason=reason_text
                ))
            self.plan_differences = diffs

        self.current_plan = new_plan
        self.is_pending_replan = False
        self._add_activity("coordinator", "Response Plan Validated", f"Plan confirmed for {loc_str} under fixed limits ({self.resources.vehicles} vehicles, {self.resources.medics} medics).", "success")

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
            rainfall_mm=290.0,
            flood_level_m=4.2,
            affected_area_km2=32.0,
            road_access=0.10,
            severity_score=92.0,
            risk_level="Critical",
            evacuation_required=True,
            road_name="Road 5 -> Hospital Precinct",
            road_status="Blocked",
            alternate_route="South Ridge Relief Track",
            description="Newly detected emergency: Hospital precinct hit by secondary landslide & severe flooding."
        )
        existing_d = any(z.id == "zone-d" for z in self.zones)
        if not existing_d:
            self.zones.append(zone_d)
            self.is_pending_replan = True
            self.last_referenced_zone_id = "zone-d"

            # Re-evaluate disaster intelligence
            intel_res, intel_rec = self.intelligence_agent.analyze_disaster(self.zones, self.location or "Active Scenario", self.disaster_type)
            self.intelligence_result = intel_res
            self.agent_recommendations["disaster_intelligence_agent"] = intel_rec

            self._add_activity("system", "⚠️ NEW DISASTER ZONE DETECTED", "Zone D (Hospital Landslide) added to crisis roster. Ready for Re-Planning.", "warning")

            asst_msg = ChatMessage(
                id=str(uuid.uuid4())[:8],
                sender="assistant",
                content=f"⚠️ **NEW DISASTER ZONE DETECTED IN {self.location.upper() if self.location else 'SCENARIO'}**\n\n"
                        f"**Zone D (Hospital Landslide)**: 8 Critical, 20 Injured, Flood Level: 4.2m, Prototype Severity Score: **92/100 (CRITICAL)**.\n\n"
                        f"Click **[ 🔄 RE-PLAN RESPONSE ]** or say 'Re-plan' to trigger multi-agent re-allocation.",
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

        # STEP 2: IF NEW LOCATION EXTRACTED, UPDATE SCENARIO STATE BEFORE AGENT REASONING
        if extracted_loc and (extracted_loc != self.location or not self.is_analyzed):
            self.reset_scenario_for_new_location(extracted_loc, extracted_disaster or "Flood affecting multiple areas")

            reply = f"Understood. **{self.location}** is now the active disaster-response location for this scenario ({self.situation_query}). I've initialized the crisis sectors and prepared the Disaster Intelligence pipeline."
            asst_msg = ChatMessage(
                id=str(uuid.uuid4())[:8],
                sender="assistant",
                content=reply,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                agent_name="Coordinator Agent",
                suggested_actions=["CREATE RESPONSE PLAN", "WHICH ZONE IS HIGHEST RISK?", "GENERATE PUBLIC ALERT"]
            )
            self.chat_history.append(asst_msg)
            return self.get_state()

        # If location is still empty and user hasn't set one yet
        if not self.location and not self.is_analyzed:
            reply = "Which location should I analyze? Please enter a city or region (e.g., 'Flood affecting Coimbatore' or 'Chennai')."
            asst_msg = ChatMessage(
                id=str(uuid.uuid4())[:8],
                sender="assistant",
                content=reply,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                agent_name="Coordinator Agent",
                suggested_actions=["Analyze Coimbatore", "Analyze Chennai", "Analyze Mumbai"]
            )
            self.chat_history.append(asst_msg)
            return self.get_state()

        loc_str = self.location or "Active Scenario"

        # 3. CREATE RESPONSE PLAN
        if "plan" in text_lower or "coordinate" in text_lower or "allocate" in text_lower:
            if not self.current_plan or self.is_pending_replan:
                self.run_full_pipeline(is_replan=self.is_pending_replan)

            alloc_summary = "\n".join([
                f"- **{a.zone_name}**: 🚑 {a.vehicles} Vehicles | 🏥 {a.medics} Medics | ⛺ {a.shelter_units} Shelters (Priority: **{a.priority}**, Score: {a.severity_score}/100)"
                for a in self.current_plan.final_allocations
            ])
            reply_text = f"📋 **COORDINATED RESPONSE PLAN FOR {loc_str.upper()}**\n\n{alloc_summary}\n\n**Decision Rationale**: {self.current_plan.explanation}"
            actions = ["GENERATE PUBLIC ALERT", "WHY?", "SHOW RESOURCE CONFLICTS", "+ ADD NEW DISASTER ZONE"]

        # 4. GENERATE PUBLIC ALERT
        elif "alert" in text_lower or "public" in text_lower or "warning" in text_lower or "evacuate" in text_lower:
            alert = self.communication_agent.generate_public_alert(self.zones, location=loc_str, disaster_type=self.disaster_type)
            if self.current_plan:
                self.current_plan.public_alert = alert

            reply_text = f"📢 **PUBLIC EMERGENCY ALERT DRAFT — {loc_str.upper()}**\n\n**Title**: {alert.title}\n**Target Sector**: {alert.target_zone}\n**Approved Route**: {alert.approved_route}\n\n*\"{alert.message}\"*\n\n*(Label: {alert.label})*"
            actions = ["CREATE RESPONSE PLAN", "WHICH ZONE IS HIGHEST RISK?"]

        # 5. DATASET / HAZARD METRIC QUESTIONS
        elif "rainfall" in text_lower or "flood level" in text_lower or "dataset" in text_lower or "highest flood" in text_lower or "average rainfall" in text_lower or "affected area" in text_lower:
            max_rain_zone = max(self.zones, key=lambda z: z.rainfall_mm)
            max_flood_zone = max(self.zones, key=lambda z: z.flood_level_m)
            max_area_zone = max(self.zones, key=lambda z: z.affected_area_km2)
            avg_rain = round(sum(z.rainfall_mm for z in self.zones) / len(self.zones), 1)

            if "highest rainfall" in text_lower or "max rainfall" in text_lower:
                reply_text = f"🌧️ **HIGHEST RAINFALL RECORDED ({loc_str})**:\n- **{max_rain_zone.name}** has the highest rainfall at **{max_rain_zone.rainfall_mm} mm** (Flood level: {max_rain_zone.flood_level_m}m, Severity Score: {max_rain_zone.severity_score}/100)."
            elif "highest flood" in text_lower or "flood level" in text_lower:
                reply_text = f"🌊 **HIGHEST FLOOD LEVEL RECORDED ({loc_str})**:\n- **{max_flood_zone.name}** has the highest flood level at **{max_flood_zone.flood_level_m} m** (Rainfall: {max_flood_zone.rainfall_mm}mm, Risk: **{max_flood_zone.risk_level}**)."
            elif "average rainfall" in text_lower:
                reply_text = f"📊 **AVERAGE RAINFALL ({loc_str})**:\n- Average rainfall across {len(self.zones)} sectors is **{avg_rain} mm**."
            elif "affected area" in text_lower:
                reply_text = f"📐 **LARGEST AFFECTED AREA ({loc_str})**:\n- **{max_area_zone.name}** has the largest affected area at **{max_area_zone.affected_area_km2} km²**."
            else:
                reply_text = f"📊 **DISASTER DATASET ANALYSIS ({loc_str})**:\n- Data Source: **{self.data_source_mode}**\n- Max Rainfall: **{max_rain_zone.rainfall_mm} mm** ({max_rain_zone.name})\n- Max Flood Level: **{max_flood_zone.flood_level_m} m** ({max_flood_zone.name})\n- Total Affected Area: **{sum(z.affected_area_km2 for z in self.zones)} km²**"

            actions = ["WHICH ZONE IS HIGHEST RISK?", "CREATE RESPONSE PLAN"]

        # 6. ASK CRITICAL / HIGHEST RISK ZONE
        elif "risk" in text_lower or "critical" in text_lower or "priority" in text_lower or "urgent" in text_lower:
            crit_zone = max(self.zones, key=lambda z: (z.severity_score, z.critical))
            self.last_referenced_zone_id = crit_zone.id
            factors = self.intelligence_result.contributing_factors if self.intelligence_result else {}
            factor_str = ", ".join([f"{k}: {v}" for k, v in factors.items()]) or "High rainfall & flood severity"

            reply_text = f"🔴 **HIGHEST RISK SECTOR IN {loc_str.upper()}**:\n- **Sector**: {crit_zone.name}\n- **Prototype Severity Score**: **{crit_zone.severity_score} / 100 ({crit_zone.risk_level})**\n- **Hazard Telemetry**: Rainfall {crit_zone.rainfall_mm}mm | Flood Level {crit_zone.flood_level_m}m | Affected Area {crit_zone.affected_area_km2}km²\n- **Casualties**: {crit_zone.critical} Critical, {crit_zone.injured} Injured\n- **Contributing Factors**: {factor_str}"
            actions = ["WHY?", "CREATE RESPONSE PLAN", "HOW MANY VEHICLES ARE AVAILABLE?"]

        # 7. ASK WHY / EXPLAIN DECISION
        elif "why" in text_lower or "explain" in text_lower or "tradeoff" in text_lower:
            ref_zone = next((z for z in self.zones if z.id == self.last_referenced_zone_id), self.zones[0])
            if self.current_plan:
                exp = self.current_plan.explanation
            else:
                exp = f"{ref_zone.name} in {loc_str} received priority due to a Prototype Severity Score of {ref_zone.severity_score}/100 ({ref_zone.rainfall_mm}mm rainfall, {ref_zone.flood_level_m}m flood level, {ref_zone.critical} critical patients)."

            reply_text = f"💡 **EXPLAINABILITY RATIONALE**\n\n{exp}"
            actions = ["HOW MANY VEHICLES ARE LEFT?", "+ ADD NEW DISASTER ZONE"]

        # 8. ASK RESOURCE COUNT / VEHICLES LEFT
        elif "vehicle" in text_lower or "medic" in text_lower or "resource" in text_lower or "left" in text_lower or "remaining" in text_lower or "available" in text_lower:
            alloc_veh = sum(a.vehicles for a in self.current_plan.final_allocations) if self.current_plan else 0
            alloc_med = sum(a.medics for a in self.current_plan.final_allocations) if self.current_plan else 0
            unalloc_veh = max(0, self.resources.vehicles - alloc_veh)
            unalloc_med = max(0, self.resources.medics - alloc_med)

            reply_text = f"⚡ **RESOURCE INVENTORY ({loc_str.upper()})**:\n- **Rescue Vehicles**: {self.resources.vehicles} Total ({alloc_veh} Allocated, {unalloc_veh} Unallocated)\n- **Medical Staff**: {self.resources.medics} Total ({alloc_med} Allocated, {unalloc_med} Unallocated)\n- **Shelters**: {self.resources.shelters} Units | **Supplies**: {self.resources.supplies} Units"
            actions = ["CREATE RESPONSE PLAN", "SHOW RESOURCE CONFLICTS"]

        # 9. ASK ROAD CONDITIONS / ROUTES
        elif "road" in text_lower or "route" in text_lower or "bypass" in text_lower:
            blocked = [z for z in self.zones if z.road_status == "Blocked"]
            congested = [z for z in self.zones if z.road_status == "Congested"]
            blocked_str = ", ".join([f"{z.name} ({z.road_name})" for z in blocked]) or "None"

            reply_text = f"🛣️ **ROAD NETWORK TELEMETRY ({loc_str.upper()})**:\n- **Blocked Roads**: {blocked_str}\n- **Alternate Bypass**: Zone C Road 3 is Blocked; Logistics Agent rerouted traffic via **Road 4 (North Ridge Bypass)**."
            actions = ["GENERATE PUBLIC ALERT", "CREATE RESPONSE PLAN"]

        # 10. RE-PLAN / WHAT CHANGED
        elif "replan" in text_lower or "re-plan" in text_lower or "change" in text_lower:
            self.run_full_pipeline(is_replan=True)
            diff_text = "\n".join([f"- **{d.zone_name}**: Vehicles ({d.before_vehicles} -> {d.after_vehicles}), Medics ({d.before_medics} -> {d.after_medics}). Reason: {d.reason}" for d in self.plan_differences]) or "No allocation changes required."

            reply_text = f"🔄 **DYNAMIC RE-PLANNING EXECUTED ({loc_str.upper()})**:\n\n**WHAT CHANGED?**\n{diff_text}\n\n**WHY?**\n{self.current_plan.explanation}"
            actions = ["GENERATE PUBLIC ALERT", "SHOW RESOURCE CONFLICTS"]

        # 11. GENERAL CONVERSATIONAL / LLM GENERATED
        else:
            system_ctx = f"Location: {loc_str}. Disaster: {self.disaster_type}. Zones: {[z.name for z in self.zones]}. Overall Severity: {self.intelligence_result.overall_severity_score if self.intelligence_result else 84}/100."
            llm_text = llm_service.generate_chat_response(system_ctx, user_text, [m.dict() for m in self.chat_history])

            if llm_text:
                reply_text = llm_text
            else:
                reply_text = f"I am monitoring **{loc_str}** with 5 specialized AI agents (Disaster Intelligence, Medical, Logistics, Communications, Coordinator). Ask me about risk levels, rainfall data, public alerts, or response plans."
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
