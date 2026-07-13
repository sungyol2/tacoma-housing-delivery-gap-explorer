"""Download ArcGIS FeatureServer layers in reproducible GeoJSON pages.

Raw responses are preserved page-by-page. A manifest records request parameters,
record counts, timestamps, byte sizes, and SHA-256 checksums. Full geometries are
never silently replaced by samples.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml


def load_source(config_path: Path, source_id: str) -> dict[str, Any]:
    registry = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    matches = [source for source in registry["sources"] if source["id"] == source_id]
    if not matches:
        raise ValueError(f"Unknown source id: {source_id}")
    source = matches[0]
    if not source.get("query"):
        raise ValueError(f"Source {source_id} has no query configuration")
    return source


def request_json(session: requests.Session, url: str, params: dict[str, Any]) -> bytes:
    for attempt in range(5):
        try:
            response = session.get(url, params=params, timeout=120)
            response.raise_for_status()
            content = response.content
            payload = response.json()
            if "error" in payload:
                raise RuntimeError(payload["error"])
            return content
        except (requests.RequestException, RuntimeError):
            if attempt == 4:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def query_params(source: dict[str, Any], offset: int) -> dict[str, Any]:
    query = source["query"]
    params: dict[str, Any] = {
        "where": query.get("where", "1=1"),
        "outFields": query.get("out_fields", "*"),
        "returnGeometry": "true",
        "resultOffset": offset,
        "resultRecordCount": query["page_size"],
        "orderByFields": "OBJECTID",
        "outSR": 4326,
        "f": "geojson",
    }
    if query.get("geometry"):
        params.update(
            {
                "geometry": query["geometry"],
                "geometryType": query.get("geometry_type", "esriGeometryEnvelope"),
                "inSR": query.get("in_sr", 2927),
                "spatialRel": "esriSpatialRelIntersects",
            }
        )
    return params


def download(source: dict[str, Any], raw_root: Path, force: bool = False) -> Path:
    source_dir = raw_root / source["id"]
    source_dir.mkdir(parents=True, exist_ok=True)
    existing_manifest = source_dir / "manifest.json"
    if existing_manifest.exists() and not force:
        raise FileExistsError(f"{existing_manifest} exists; pass --force to refresh")

    session = requests.Session()
    session.headers["User-Agent"] = "TacomaHousingDeliveryGap/0.1 public-data-audit"
    query_url = f"{source['url'].rstrip('/')}/query"
    page_size = int(source["query"]["page_size"])
    offset = 0
    pages: list[dict[str, Any]] = []
    total_features = 0

    while True:
        params = query_params(source, offset)
        content = request_json(session, query_url, params)
        payload = json.loads(content)
        features = payload.get("features", [])
        page_path = source_dir / f"page_{offset:07d}.geojson"
        page_path.write_bytes(content)
        pages.append(
            {
                "offset": offset,
                "features": len(features),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "file": page_path.name,
            }
        )
        total_features += len(features)
        print(f"{source['id']}: {total_features:,} features")
        if len(features) < page_size:
            break
        offset += page_size

    manifest = {
        "source_id": source["id"],
        "source_url": source["url"],
        "downloaded_at": datetime.now(UTC).isoformat(),
        "query": source["query"],
        "output_crs": "EPSG:4326",
        "total_features": total_features,
        "pages": pages,
    }
    existing_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return existing_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_ids", nargs="+")
    parser.add_argument("--config", type=Path, default=Path("config/data_sources.yaml"))
    parser.add_argument("--raw-root", type=Path, default=Path("data_raw"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    for source_id in args.source_ids:
        source = load_source(args.config, source_id)
        manifest = download(source, args.raw_root, args.force)
        print(f"Wrote {manifest}")


if __name__ == "__main__":
    main()
