from models import SystemState, DisasterZone
from services.scenario_manager import scenario_manager

class DisasterResponsePlanner:
    def get_state(self) -> SystemState:
        return scenario_manager.get_state()

    def add_disaster_zone(self, zone: DisasterZone) -> SystemState:
        existing = [z for z in scenario_manager.zones if z.id == zone.id]
        if existing:
            scenario_manager.zones = [zone if z.id == zone.id else z for z in scenario_manager.zones]
        else:
            scenario_manager.zones.append(zone)
            scenario_manager._add_activity("system", "🚨 NEW DISASTER DETECTED", f"{zone.name} added to crisis map.", "warning")
        return scenario_manager.get_state()

    def remove_disaster_zone(self, zone_id: str) -> SystemState:
        scenario_manager.zones = [z for z in scenario_manager.zones if z.id != zone_id]
        scenario_manager._add_activity("system", "Zone Removed", f"Zone {zone_id} cleared.", "info")
        return scenario_manager.get_state()

    def run_multi_agent_pipeline(self, is_replan: bool = False) -> SystemState:
        return scenario_manager.run_full_pipeline(is_replan=is_replan)

    def reset_system(self) -> SystemState:
        return scenario_manager.reset_system()

planner_service = DisasterResponsePlanner()
