import json

import duckdb
import polars as pl
from fastapi import APIRouter, Query

from flowfile_core import flow_file_handler

router = APIRouter(prefix="/spatial", tags=["spatial"])

GEOM_COL = "_flowfile_geom"


@router.get("/preview")
def get_spatial_preview(
    flow_id: int = Query(...),
    node_id: int = Query(...),
    geom_col: str = Query(default=GEOM_COL),
    max_polygons: int = Query(default=5000, le=10000),
    tolerance: float = Query(default=0.001, ge=0),
):
    """Returns a downsampled, simplified GeoJSON FeatureCollection for map preview."""
    flow = flow_file_handler.get_flow(flow_id)
    if flow is None:
        return {"type": "FeatureCollection", "features": []}

    node = flow.get_node(node_id)
    if node is None or node.results.resulting_data is None:
        return {"type": "FeatureCollection", "features": []}

    engine = node.results.resulting_data
    df = engine.data_frame
    if isinstance(df, pl.LazyFrame):
        df = df.collect()

    if geom_col not in df.columns:
        return {"type": "FeatureCollection", "features": []}

    total_rows = df.height
    if total_rows == 0:
        return {"type": "FeatureCollection", "features": []}

    if total_rows > max_polygons:
        sample_step = total_rows // max_polygons
        indices = list(range(0, total_rows, sample_step))[:max_polygons]
        preview_df = df[indices]
    else:
        preview_df = df

    attr_cols = [c for c in preview_df.columns if c != geom_col]
    attr_select = ", ".join([f"\"{c}\"" for c in attr_cols])
    if attr_select:
        attr_select = ", " + attr_select

    con = duckdb.connect()
    con.execute("LOAD spatial;")
    rows = con.execute(f"""
        SELECT ST_AsGeoJSON(
            ST_SimplifyPreserveTopology(ST_GeomFromWKB("{geom_col}"), {tolerance})
        ) AS geojson{attr_select}
        FROM preview_df
        WHERE "{geom_col}" IS NOT NULL
    """).fetchall()
    con.close()

    col_names = ["geojson"] + attr_cols
    features = []
    for row in rows:
        geojson_str = row[0]
        if not geojson_str:
            continue
        try:
            geometry = json.loads(geojson_str)
            properties = {col_names[i + 1]: row[i + 1] for i in range(len(attr_cols))}
            # Convert any bytes in properties to hex for JSON safety
            for k, v in properties.items():
                if isinstance(v, (bytes, bytearray)):
                    properties[k] = v.hex()
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": properties,
            })
        except Exception:
            continue

    return {"type": "FeatureCollection", "features": features}
