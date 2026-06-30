from typing import Literal

from flowfile_worker.create.funcs import (
    create_from_path_avro,
    create_from_path_csv,
    create_from_path_excel,
    create_from_path_ipc,
    create_from_path_json,
    create_from_path_ndjson,
    create_from_path_parquet,
)
from flowfile_worker.create.geo_funcs import (
    create_from_path_geojson,
    create_from_path_geoparquet,
    create_from_path_shapefile,
)

FileType = Literal["csv", "parquet", "json", "excel", "ipc", "ndjson", "avro", "shapefile", "geoparquet", "geojson"]


def table_creator_factory_method(file_type: FileType) -> callable:
    match file_type:
        case "csv":
            return create_from_path_csv
        case "parquet":
            return create_from_path_parquet
        case "excel":
            return create_from_path_excel
        case "json":
            return create_from_path_json
        case "ipc":
            return create_from_path_ipc
        case "ndjson":
            return create_from_path_ndjson
        case "avro":
            return create_from_path_avro
        case "shapefile":
            return create_from_path_shapefile
        case "geoparquet":
            return create_from_path_geoparquet
        case "geojson":
            return create_from_path_geojson
        case _:
            raise ValueError(f"Unsupported file type: {file_type}")
