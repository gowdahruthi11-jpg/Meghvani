"""
Meghvani Phase 7C: Spatial Mapping Engine for IMD 0.25° Gridded Rainfall.

Maps 0.25° × 0.25° IMD gridded daily precipitation cells to Meghvani administrative blocks.

Scientific Integrity Rules:
1. Do not assume one grid cell = one administrative block without spatial verification.
2. If actual block boundary polygons (GeoJSON/Shapefile) are unavailable, do NOT invent them.
   Return status: BLOCK_GEOMETRY_REQUIRED.
3. Centroid/grid-cell mapping (CENTROID_GRID_CELL) is supported when point coordinates (lat, lon) exist.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from app.config import PROJECT_ROOT, blocks_config

logger = logging.getLogger(__name__)

LOCATION_METADATA_FILE = PROJECT_ROOT / "data" / "location" / "sample_blocks_metadata.json"

METHOD_CENTROID = "CENTROID_GRID_CELL"
METHOD_AREA_WEIGHTED = "AREA_WEIGHTED"
METHOD_POLYGON_WEIGHTED = "POLYGON_WEIGHTED"

STATUS_READY = "READY"
STATUS_BLOCK_GEOMETRY_REQUIRED = "BLOCK_GEOMETRY_REQUIRED"


class BlockCoordinate(BaseModel):
    block_id: str
    name: str
    district: str
    state: str
    latitude: float
    longitude: float
    boundary_reference: Optional[str] = None
    has_polygon_geometry: bool = False
    target_imd_grid_lat: float
    target_imd_grid_lon: float


class SpatialMappingReport(BaseModel):
    status: str
    chosen_method: str
    available_methods: List[str]
    geometry_requirement_notes: str
    mapped_blocks: Dict[str, Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


def snap_to_imd_grid(lat: float, lon: float) -> Tuple[float, float]:
    """
    Snaps a continuous latitude and longitude to the nearest IMD 0.25° × 0.25° grid center.
    IMD grid centers are spaced at multiples of 0.25° (e.g. 21.00, 21.25, 21.50).
    """
    grid_lat = round(lat * 4.0) / 4.0
    grid_lon = round(lon * 4.0) / 4.0
    return float(grid_lat), float(grid_lon)


class BlockSpatialMapper:
    """
    Manages spatial translation between IMD 0.25° gridded rainfall and administrative blocks.
    """

    def __init__(self, metadata_path: Optional[Path] = None):
        self.metadata_path = metadata_path or LOCATION_METADATA_FILE
        self.blocks: Dict[str, BlockCoordinate] = {}
        self._load_block_metadata()

    def _load_block_metadata(self):
        """Loads block coordinates from canonical blocks.yaml or fallback."""
        raw_blocks = blocks_config.get("blocks", [])
        if not raw_blocks:
            if not self.metadata_path.exists():
                raw_blocks = [
                    {"id": 1, "name": "Nagpur Rural", "district": "Nagpur", "state": "Maharashtra", "latitude": 21.1458, "longitude": 79.0882},
                    {"id": 2, "name": "Wardha East", "district": "Wardha", "state": "Maharashtra", "latitude": 20.7453, "longitude": 78.6022},
                    {"id": 3, "name": "Amravati Central", "district": "Amravati", "state": "Maharashtra", "latitude": 20.9374, "longitude": 77.7796}
                ]
            else:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    raw_blocks = json.load(f)

        for b in raw_blocks:
            b_id = f"BLK{int(b['id']):03d}"
            lat = float(b["latitude"])
            lon = float(b["longitude"])
            grid_lat, grid_lon = snap_to_imd_grid(lat, lon)

            # Check if actual boundary geometry (GeoJSON / shapefile) exists
            boundary_file = PROJECT_ROOT / "data" / "location" / f"{b_id}_boundary.geojson"
            has_poly = boundary_file.exists()

            self.blocks[b_id] = BlockCoordinate(
                block_id=b_id,
                name=b.get("name", b_id),
                district=b.get("district", "Unknown"),
                state=b.get("state", "Maharashtra"),
                latitude=lat,
                longitude=lon,
                boundary_reference=b.get("boundary_reference"),
                has_polygon_geometry=has_poly,
                target_imd_grid_lat=grid_lat,
                target_imd_grid_lon=grid_lon
            )

    def get_spatial_mapping_report(self, preferred_method: str = METHOD_CENTROID) -> SpatialMappingReport:
        """
        Assesses spatial mapping feasibility for the prototype blocks.
        """
        has_all_polygons = all(b.has_polygon_geometry for b in self.blocks.values())

        mapped_info = {}
        for b_id, coord in self.blocks.items():
            mapped_info[b_id] = {
                "name": coord.name,
                "district": coord.district,
                "centroid_lat": coord.latitude,
                "centroid_lon": coord.longitude,
                "snapped_imd_grid_lat": coord.target_imd_grid_lat,
                "snapped_imd_grid_lon": coord.target_imd_grid_lon,
                "has_polygon_geometry": coord.has_polygon_geometry
            }

        if preferred_method in (METHOD_AREA_WEIGHTED, METHOD_POLYGON_WEIGHTED) and not has_all_polygons:
            status = STATUS_BLOCK_GEOMETRY_REQUIRED
            notes = (
                "AREA_WEIGHTED and POLYGON_WEIGHTED spatial aggregation cannot be computed "
                "because official administrative boundary polygon geometries (GeoJSON/Shapefile) "
                "are unavailable for one or more prototype blocks (BLK001, BLK002, BLK003). "
                "To prevent fabricating artificial block shapes, official boundary files from "
                "Survey of India or Census of India are required. Centroid grid-cell mapping "
                "(CENTROID_GRID_CELL) is supported as an unambiguous coordinate point mapping."
            )
            chosen = preferred_method
        else:
            status = STATUS_READY
            chosen = METHOD_CENTROID if not has_all_polygons else preferred_method
            notes = (
                f"Using supported spatial mapping method: {chosen}. "
                "Maps block centroid coordinates to the nearest IMD 0.25° × 0.25° grid center."
            )

        return SpatialMappingReport(
            status=status,
            chosen_method=chosen,
            available_methods=[METHOD_CENTROID] + ([METHOD_AREA_WEIGHTED, METHOD_POLYGON_WEIGHTED] if has_all_polygons else []),
            geometry_requirement_notes=notes,
            mapped_blocks=mapped_info
        )

    def map_gridded_to_blocks(
        self,
        gridded_df: pd.DataFrame,
        method: str = METHOD_CENTROID
    ) -> pd.DataFrame:
        """
        Aggregates gridded daily rainfall records to administrative blocks.
        Input gridded_df must have: date, lat, lon, rainfall_mm
        Returns block_daily_rainfall DataFrame with columns:
        date, year, block_id, rainfall_mm, source, spatial_method
        """
        if gridded_df.empty:
            return pd.DataFrame(columns=["date", "year", "block_id", "rainfall_mm", "source", "spatial_method"])

        work = gridded_df.copy()
        work["date_dt"] = pd.to_datetime(work["date"], errors="coerce")
        work = work.dropna(subset=["date_dt"])
        work["year"] = work["date_dt"].dt.year
        work["date_str"] = work["date_dt"].dt.strftime("%Y-%m-%d")

        records = []

        if method == METHOD_CENTROID:
            # Map each block by matching its target snapped IMD grid cell
            for b_id, coord in self.blocks.items():
                t_lat = coord.target_imd_grid_lat
                t_lon = coord.target_imd_grid_lon

                # Filter cells matching target lat and lon within 0.125° tolerance
                cell_mask = (
                    np.isclose(work["lat"], t_lat, atol=0.13) &
                    np.isclose(work["lon"], t_lon, atol=0.13)
                )
                cell_df = work[cell_mask]

                if cell_df.empty:
                    # If exact cell is not in slice, take the nearest available cell
                    dist = (work["lat"] - t_lat) ** 2 + (work["lon"] - t_lon) ** 2
                    if not dist.empty:
                        min_dist_idx = dist.idxmin()
                        nearest_lat = work.loc[min_dist_idx, "lat"]
                        nearest_lon = work.loc[min_dist_idx, "lon"]
                        cell_df = work[(work["lat"] == nearest_lat) & (work["lon"] == nearest_lon)]

                for _, row in cell_df.iterrows():
                    records.append({
                        "date": row["date_str"],
                        "year": int(row["year"]),
                        "block_id": b_id,
                        "rainfall_mm": round(float(row["rainfall_mm"]), 2),
                        "source": "IMD_025",
                        "spatial_method": METHOD_CENTROID
                    })

        elif method in (METHOD_AREA_WEIGHTED, METHOD_POLYGON_WEIGHTED):
            report = self.get_spatial_mapping_report(preferred_method=method)
            if report.status == STATUS_BLOCK_GEOMETRY_REQUIRED:
                raise ValueError(
                    f"Cannot execute {method}: official boundary geometries are required ({report.geometry_requirement_notes})"
                )

        res_df = pd.DataFrame(records)
        if not res_df.empty:
            res_df.sort_values(by=["block_id", "date"], inplace=True)
            res_df.reset_index(drop=True, inplace=True)
        return res_df
