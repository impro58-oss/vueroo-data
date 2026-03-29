#!/usr/bin/env python3
"""
Crucix Data Bridge — Pipes Crucix output to CycleVue Pro
Reads latest.json and converts to CycleVue-compatible format
"""

import json
import os
from pathlib import Path
from datetime import datetime

def convert_crucix_to_cyclevue():
    """Convert Crucix latest.json to CycleVue format"""
    
    crucix_path = Path.home() / ".openclaw" / "workspace" / "Crucix" / "runs" / "latest.json"
    output_path = Path.home() / ".openclaw" / "workspace" / "vueroo-portal" / "public" / "data" / "crucix_feed.json"
    
    if not crucix_path.exists():
        print(f"Crucix data not found at {crucix_path}")
        print("Run 'npm run sweep' in Crucix directory first")
        return None
    
    # Load Crucix data
    with open(crucix_path, 'r') as f:
        crucix_data = json.load(f)
    
    # Extract relevant fields for CycleVue
    cyclevue_data = {
        "metadata": {
            "source": "Crucix",
            "last_update": crucix_data.get("timestamp", datetime.now().isoformat()),
            "sources_active": len(crucix_data.get("sources", [])),
        },
        "economic": {
            "yield_curve": crucix_data.get("economic", {}).get("yield_curve"),
            "fed_funds": crucix_data.get("economic", {}).get("fed_funds"),
            "vix": crucix_data.get("economic", {}).get("vix"),
            "credit_spread": crucix_data.get("economic", {}).get("credit_spread"),
            "m2_growth": crucix_data.get("economic", {}).get("m2_growth"),
        },
        "conflict": {
            "acled_events_24h": crucix_data.get("conflict", {}).get("events_24h", 0),
            "hotspots": crucix_data.get("conflict", {}).get("hotspots", []),
        },
        "satellite": {
            "thermal_anomalies": crucix_data.get("satellite", {}).get("fires_count", 0),
            "regions": crucix_data.get("satellite", {}).get("regions", []),
        },
        "markets": {
            "btc": crucix_data.get("markets", {}).get("btc_usd"),
            "spy": crucix_data.get("markets", {}).get("spy"),
            "gold": crucix_data.get("markets", {}).get("gold"),
            "wti": crucix_data.get("markets", {}).get("wti"),
        },
        "alerts": crucix_data.get("alerts", []),
    }
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save converted data
    with open(output_path, 'w') as f:
        json.dump(cyclevue_data, f, indent=2)
    
    print(f"Crucix data converted and saved to {output_path}")
    return cyclevue_data

if __name__ == "__main__":
    result = convert_crucix_to_cyclevue()
    if result:
        print(f"Sources active: {result['metadata']['sources_active']}")
        print(f"Alerts: {len(result['alerts'])}")
