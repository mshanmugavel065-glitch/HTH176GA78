import csv
import json
import io
from typing import List, Dict, Any, Tuple, Optional
from models import DisasterZone, DatasetMetadata

class DatasetService:
    @staticmethod
    def process_file_content(file_bytes: bytes, filename: str) -> Tuple[DatasetMetadata, List[DisasterZone]]:
        text_content = file_bytes.decode('utf-8', errors='ignore')
        filename_lower = filename.lower()

        if filename_lower.endswith('.json'):
            return DatasetService._parse_json(text_content, filename)
        else:
            return DatasetService._parse_csv(text_content, filename)

    @staticmethod
    def _parse_csv(csv_text: str, filename: str) -> Tuple[DatasetMetadata, List[DisasterZone]]:
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        
        if not rows:
            raise ValueError("The uploaded CSV dataset is empty.")

        detected_cols = [c.strip() for c in (reader.fieldnames or [])]
        detected_cols_lower = [c.lower() for c in detected_cols]

        warnings = []
        expected_cols = ["rainfall_mm", "flood_level_m", "affected_area_km2", "injured", "critical_patients", "road_access"]
        missing_cols = [col for col in expected_cols if not any(col in c for c in detected_cols_lower)]

        if missing_cols:
            warnings.append("Some disaster indicators are unavailable. The assessment will use the available data.")

        zones: List[DisasterZone] = []
        for idx, row in enumerate(rows):
            # Normalize row keys
            row_norm = {k.strip().lower(): str(v).strip() for k, v in row.items() if k}

            # Location / Zone name extraction
            zone_name = (
                row_norm.get("zone_name") or 
                row_norm.get("zone") or 
                row_norm.get("location") or 
                row_norm.get("name") or 
                f"Zone {chr(65 + idx)}"
            )
            zone_id = f"zone-{chr(97 + idx)}"

            # Parse numeric fields safely (using 0.0 or default if missing, without inventing data)
            rainfall = DatasetService._safe_float(row_norm, ["rainfall_mm", "rainfall", "rain_mm"], 0.0)
            flood_lvl = DatasetService._safe_float(row_norm, ["flood_level_m", "flood_level", "water_level_m", "flood_m"], 0.0)
            area_km2 = DatasetService._safe_float(row_norm, ["affected_area_km2", "affected_area", "area_km2"], 0.0)
            injured = DatasetService._safe_int(row_norm, ["injured", "casualties", "injured_count"], 0)
            critical = DatasetService._safe_int(row_norm, ["critical_patients", "critical", "severe_cases"], 0)
            road_access = DatasetService._safe_float(row_norm, ["road_access", "road_accessibility", "accessibility"], 1.0)
            population = DatasetService._safe_int(row_norm, ["population", "pop"], 100)

            road_status = "Open"
            if road_access <= 0.3:
                road_status = "Blocked"
            elif road_access <= 0.7:
                road_status = "Congested"

            zone = DisasterZone(
                id=zone_id,
                name=zone_name,
                population=population,
                injured=injured,
                critical=critical,
                risk="Moderate",
                rainfall_mm=rainfall,
                flood_level_m=flood_lvl,
                affected_area_km2=area_km2,
                road_access=road_access,
                severity_score=0.0,
                risk_level="Moderate",
                evacuation_required=(flood_lvl >= 2.5 or critical >= 5),
                road_name=f"Road {idx + 1} -> Relief Hub",
                road_status=road_status,
                alternate_route=f"Bypass Track {idx + 1}",
                description=f"Sector parsed from uploaded dataset ({filename})."
            )
            zones.append(zone)

        metadata = DatasetMetadata(
            filename=filename,
            data_type="UPLOADED DATASET",
            columns_detected=detected_cols,
            row_count=len(zones),
            warnings=warnings,
            summary_stats={
                "zones_count": len(zones),
                "columns_count": len(detected_cols)
            }
        )

        return metadata, zones

    @staticmethod
    def _parse_json(json_text: str, filename: str) -> Tuple[DatasetMetadata, List[DisasterZone]]:
        data = json.loads(json_text)
        items = data if isinstance(data, list) else data.get("zones", data.get("initial_zones", []))

        if not items:
            raise ValueError("The uploaded JSON dataset contains no valid zone items.")

        detected_cols = list(items[0].keys()) if items else []
        warnings = []

        zones: List[DisasterZone] = []
        for idx, item in enumerate(items):
            item_norm = {k.lower(): v for k, v in item.items()}

            zone_name = str(item_norm.get("name") or item_norm.get("zone") or item_norm.get("location") or f"Zone {chr(65 + idx)}")
            zone_id = str(item_norm.get("id") or f"zone-{chr(97 + idx)}")

            rainfall = float(item_norm.get("rainfall_mm", item_norm.get("rainfall", 0.0)))
            flood_lvl = float(item_norm.get("flood_level_m", item_norm.get("flood_level", 0.0)))
            area_km2 = float(item_norm.get("affected_area_km2", item_norm.get("affected_area", 0.0)))
            injured = int(item_norm.get("injured", 0))
            critical = int(item_norm.get("critical_patients", item_norm.get("critical", 0)))
            road_access = float(item_norm.get("road_access", 1.0))
            population = int(item_norm.get("population", 100))

            road_status = item.get("road_status", "Open" if road_access > 0.7 else ("Congested" if road_access > 0.3 else "Blocked"))

            zone = DisasterZone(
                id=zone_id,
                name=zone_name,
                population=population,
                injured=injured,
                critical=critical,
                risk="Moderate",
                rainfall_mm=rainfall,
                flood_level_m=flood_lvl,
                affected_area_km2=area_km2,
                road_access=road_access,
                severity_score=0.0,
                risk_level="Moderate",
                evacuation_required=(flood_lvl >= 2.5 or critical >= 5),
                road_name=item.get("road_name", f"Road {idx + 1} -> Primary Relief Sector"),
                road_status=road_status,
                alternate_route=item.get("alternate_route", f"Bypass Route {idx + 1}"),
                description=item.get("description", f"Sector loaded from dataset ({filename}).")
            )
            zones.append(zone)

        metadata = DatasetMetadata(
            filename=filename,
            data_type="UPLOADED DATASET",
            columns_detected=detected_cols,
            row_count=len(zones),
            warnings=warnings,
            summary_stats={"zones_count": len(zones)}
        )

        return metadata, zones

    @staticmethod
    def _safe_float(d: Dict[str, str], keys: List[str], default: float) -> float:
        for k in keys:
            if k in d and d[k] != "":
                try:
                    return float(d[k])
                except ValueError:
                    pass
        return default

    @staticmethod
    def _safe_int(d: Dict[str, str], keys: List[str], default: int) -> int:
        for k in keys:
            if k in d and d[k] != "":
                try:
                    return int(float(d[k]))
                except ValueError:
                    pass
        return default

dataset_service = DatasetService()
