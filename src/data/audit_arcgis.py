"""Run lightweight availability checks against configured ArcGIS feature layers.

This script records service metadata, record counts, field names, and a one-record
attribute sample without downloading full geometries. It is intended for Phase 1
source auditing, not production ingestion.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import yaml


def get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"ArcGIS error for {response.url}: {payload['error']}")
    return payload


def audit_layer(url: str) -> dict[str, Any]:
    metadata = get_json(url, {"f": "json"})
    count = get_json(
        f"{url.rstrip('/')}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )["count"]
    sample = get_json(
        f"{url.rstrip('/')}/query",
        {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "false",
            "resultRecordCount": 1,
            "f": "json",
        },
    )
    return {
        "name": metadata.get("name"),
        "geometry_type": metadata.get("geometryType"),
        "spatial_reference": metadata.get("extent", {}).get("spatialReference"),
        "max_record_count": metadata.get("maxRecordCount"),
        "record_count": count,
        "fields": [field["name"] for field in metadata.get("fields", [])],
        "sample_attributes": (sample.get("features") or [{}])[0].get("attributes", {}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/data_sources.yaml"))
    parser.add_argument("--output", type=Path, default=Path("outputs/data_audit/arcgis.json"))
    args = parser.parse_args()

    registry = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    results: dict[str, Any] = {
        "checked_at": datetime.now(UTC).isoformat(),
        "sources": {},
    }
    for source in registry["sources"]:
        url = source.get("layer_url") or source.get("url")
        if source.get("service_type", "").startswith("ArcGIS FeatureServer") and url:
            try:
                results["sources"][source["id"]] = {"ok": True, **audit_layer(url)}
            except Exception as exc:  # preserve per-source failures in the audit artifact
                results["sources"][source["id"]] = {"ok": False, "error": str(exc)}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
