from typing import List, Dict, Tuple, Any
from models import DisasterZone, ResourcePool, ZoneAllocation, ConflictItem, PlanChange

class ResourceValidator:
    def check_constraints(
        self,
        allocations: List[ZoneAllocation],
        resources: ResourcePool
    ) -> List[ConflictItem]:
        conflicts = []
        
        total_veh = sum(a.vehicles for a in allocations)
        total_med = sum(a.medics for a in allocations)
        total_she = sum(a.shelter_units for a in allocations)
        total_sup = sum(a.supplies for a in allocations)

        if total_veh > resources.vehicles:
            exceeded_zones = [a.zone_name for a in allocations if a.vehicles > 0]
            conflicts.append(ConflictItem(
                id="conflict-vehicles",
                resource_type="vehicles",
                description=f"Rescue Vehicle over-allocation: Recommended total is {total_veh} units, but only {resources.vehicles} are available in total fleet.",
                zones_involved=exceeded_zones,
                demanded=total_veh,
                available=resources.vehicles,
                resolution=f"Cap total vehicle distribution to {resources.vehicles} units, prioritizing evacuation zones."
            ))

        if total_med > resources.medics:
            exceeded_zones = [a.zone_name for a in allocations if a.medics > 0]
            conflicts.append(ConflictItem(
                id="conflict-medics",
                resource_type="medics",
                description=f"Medical Personnel deficit: Recommended total is {total_med} medics, but maximum available team size is {resources.medics}.",
                zones_involved=exceeded_zones,
                demanded=total_med,
                available=resources.medics,
                resolution=f"Rebalance {resources.medics} medics to highest critical-patient zones."
            ))

        if total_she > resources.shelters:
            exceeded_zones = [a.zone_name for a in allocations if a.shelter_units > 0]
            conflicts.append(ConflictItem(
                id="conflict-shelters",
                resource_type="shelters",
                description=f"Shelter Capacity exceeded: Recommended {total_she} emergency shelters, max capacity is {resources.shelters}.",
                zones_involved=exceeded_zones,
                demanded=total_she,
                available=resources.shelters,
                resolution=f"Allocate {resources.shelters} available shelters exclusively to active evacuation sectors."
            ))

        if total_sup > resources.supplies:
            exceeded_zones = [a.zone_name for a in allocations if a.supplies > 0]
            conflicts.append(ConflictItem(
                id="conflict-supplies",
                resource_type="supplies",
                description=f"Supply Stockpile deficit: Recommended {total_sup} supply units, total inventory is {resources.supplies}.",
                zones_involved=exceeded_zones,
                demanded=total_sup,
                available=resources.supplies,
                resolution=f"Proportionally scale supply packages to stay within the {resources.supplies} limit."
            ))

        return conflicts

    def enforce_hard_limits(
        self,
        zones: List[DisasterZone],
        raw_allocations: List[ZoneAllocation],
        resources: ResourcePool
    ) -> List[ZoneAllocation]:
        """Strictly adjusts allocations to guarantee hard limits are never breached."""
        zone_map = {z.id: z for z in zones}
        
        # Calculate priorities for each zone
        weighted_zones = []
        alloc_dict = {a.zone_id: a for a in raw_allocations}

        for z in zones:
            # Score for medics: heavy weight on critical & injured
            med_score = z.critical * 4.0 + z.injured * 1.5 + (10.0 if z.risk == "Critical" else 3.0)
            # Score for vehicles: heavy weight on evacuation & critical
            veh_score = (30.0 if z.evacuation_required else 5.0) + z.critical * 2.5 + z.population * 0.1
            # Score for shelters: heavy weight on evacuation & population
            shelter_score = (50.0 if z.evacuation_required else 10.0) + z.population * 0.2
            
            weighted_zones.append({
                "zone": z,
                "med_score": med_score,
                "veh_score": veh_score,
                "shelter_score": shelter_score,
                "orig_alloc": alloc_dict.get(z.id)
            })

        # Distribute Medics (max resources.medics)
        sorted_by_med = sorted(weighted_zones, key=lambda x: x["med_score"], reverse=True)
        medics_remaining = resources.medics
        medic_alloc = {z.id: 0 for z in zones}
        
        # First pass: give at least 1 medic to any zone with critical patients
        for item in sorted_by_med:
            z = item["zone"]
            if z.critical > 0 and medics_remaining > 0:
                medic_alloc[z.id] += 1
                medics_remaining -= 1
        
        # Second pass: distribute remaining according to score proportion
        while medics_remaining > 0:
            for item in sorted_by_med:
                if medics_remaining == 0:
                    break
                z = item["zone"]
                medic_alloc[z.id] += 1
                medics_remaining -= 1

        # Distribute Vehicles (max resources.vehicles)
        sorted_by_veh = sorted(weighted_zones, key=lambda x: x["veh_score"], reverse=True)
        vehicles_remaining = resources.vehicles
        veh_alloc = {z.id: 0 for z in zones}

        # Evacuation zones get primary vehicle priority
        for item in sorted_by_veh:
            z = item["zone"]
            if z.evacuation_required and vehicles_remaining >= 2:
                veh_alloc[z.id] += 2
                vehicles_remaining -= 2
            elif z.evacuation_required and vehicles_remaining == 1:
                veh_alloc[z.id] += 1
                vehicles_remaining -= 1

        # Fill remaining vehicles
        for item in sorted_by_veh:
            if vehicles_remaining == 0:
                break
            z = item["zone"]
            veh_alloc[z.id] += 1
            vehicles_remaining -= 1

        # Distribute Shelters (max resources.shelters)
        sorted_by_shelter = sorted(weighted_zones, key=lambda x: x["shelter_score"], reverse=True)
        shelter_remaining = resources.shelters
        shelter_alloc = {z.id: 0 for z in zones}

        for item in sorted_by_shelter:
            if shelter_remaining == 0:
                break
            z = item["zone"]
            shelter_alloc[z.id] += 1
            shelter_remaining -= 1

        # Distribute Supplies (max resources.supplies)
        total_pop = sum(z.population for z in zones) or 1
        supplies_remaining = resources.supplies
        supply_alloc = {}
        for z in zones:
            prop = z.population / total_pop
            if z.risk == "Critical":
                prop *= 1.3
            allocated = int(round(prop * resources.supplies))
            supply_alloc[z.id] = allocated
        
        # Adjust sum to exactly resources.supplies
        current_sum = sum(supply_alloc.values())
        diff = resources.supplies - current_sum
        if diff != 0 and zones:
            supply_alloc[zones[0].id] = max(0, supply_alloc[zones[0].id] + diff)

        # Build final validated ZoneAllocation objects
        validated_allocations = []
        for z in zones:
            orig = alloc_dict.get(z.id)
            priority = z.risk
            
            # Determine reason
            reasons = []
            if medic_alloc[z.id] > 0:
                reasons.append(f"Allocated {medic_alloc[z.id]} medics for {z.critical} critical patients")
            if veh_alloc[z.id] > 0:
                reasons.append(f"{veh_alloc[z.id]} vehicles assigned for transport/evac")
            if shelter_alloc[z.id] > 0:
                reasons.append(f"{shelter_alloc[z.id]} shelter units assigned")
            
            reason_str = "; ".join(reasons) if reasons else "Base monitoring allocation"

            validated_allocations.append(ZoneAllocation(
                zone_id=z.id,
                zone_name=z.name,
                vehicles=veh_alloc[z.id],
                medics=medic_alloc[z.id],
                shelter_units=shelter_alloc[z.id],
                supplies=supply_alloc[z.id],
                priority=priority,
                reason=reason_str
            ))

        return validated_allocations

validator = ResourceValidator()
