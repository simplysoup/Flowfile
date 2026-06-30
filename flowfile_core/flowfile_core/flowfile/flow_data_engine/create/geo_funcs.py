import polars as pl
import duckdb

from flowfile_core.schemas import input_schema

GEOM_COL = "_flowfile_geom"


def _get_spatial_con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    return con


def create_from_path_shapefile(received_table: input_schema.ReceivedTable) -> pl.DataFrame:
    if not isinstance(received_table.table_settings, input_schema.InputShapefileTable):
        raise ValueError("Received table settings are not of type InputShapefileTable")

    con = _get_spatial_con()
    path = received_table.abs_file_path.replace("\\", "/")
    arrow = con.execute(f"""
        SELECT * REPLACE (ST_AsWKB(geom) AS geom)
        FROM ST_Read('{path}')
    """).arrow()
    con.close()

    df = pl.from_arrow(arrow)
    if "geom" in df.columns:
        df = df.rename({"geom": GEOM_COL})
    return df


def create_from_path_geoparquet(received_table: input_schema.ReceivedTable) -> pl.DataFrame:
    if not isinstance(received_table.table_settings, input_schema.InputGeoParquetTable):
        raise ValueError("Received table settings are not of type InputGeoParquetTable")

    con = _get_spatial_con()
    path = received_table.abs_file_path.replace("\\", "/")
    arrow = con.execute(f"""
        SELECT * REPLACE (ST_AsWKB(geometry) AS geometry)
        FROM '{path}'
    """).arrow()
    con.close()

    df = pl.from_arrow(arrow)
    for col in ("geometry", "geom", "wkb_geometry"):
        if col in df.columns:
            df = df.rename({col: GEOM_COL})
            break
    return df


def create_from_path_geojson(received_table: input_schema.ReceivedTable) -> pl.DataFrame:
    if not isinstance(received_table.table_settings, input_schema.InputGeoJsonTable):
        raise ValueError("Received table settings are not of type InputGeoJsonTable")

    con = _get_spatial_con()
    path = received_table.abs_file_path.replace("\\", "/")
    arrow = con.execute(f"""
        SELECT * REPLACE (ST_AsWKB(geom) AS geom)
        FROM ST_Read('{path}')
    """).arrow()
    con.close()

    df = pl.from_arrow(arrow)
    if "geom" in df.columns:
        df = df.rename({"geom": GEOM_COL})
    return df
