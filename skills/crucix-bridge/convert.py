#!/usr/bin/env python3
"""
Crucix Data Bridge — Converts Crucix raw output to CycleVue format
"""

import json
from pathlib import Path

def main():
    raw_path = Path.home() / ".openclaw" / "workspace" / "vueroo-portal" / "public" / "data" / "crucix_raw.json"
    output_path = Path.home() / ".openclaw" / "workspace" / "vueroo-portal" / "public" / "data" / "crucix_feed.json"
    
    if not raw_path.exists():
        print(f"Raw data not found: {raw_path}")
        return
    
    # Read as UTF-16 (what Node.js outputs on Windows)
    with open(raw_path, 'r', encoding='utf-16') as f:
        data = json.load(f)
    
    crucix = data.get('crucix', {})
    sources = data.get('sources', {})
    
    # Extract data safely
    yf = sources.get('YFinance', {})
    fred = sources.get('FRED', {})
    acled = sources.get('ACLED', {})
    cisa = sources.get('CISA-KEV', {})
    firms = sources.get('FIRMS', {})
    
    # Markets - crypto is a list
    crypto_list = yf.get('crypto', [])
    btc = next((c.get('price') for c in crypto_list if c.get('symbol') == 'BTC-USD'), None)
    eth = next((c.get('price') for c in crypto_list if c.get('symbol') == 'ETH-USD'), None)
    
    indexes = yf.get('indexes', [])
    spy = next((i.get('price') for i in indexes if i.get('symbol') == 'SPY'), None)
    
    vol = yf.get('volatility', [])
    vix = next((v.get('price') for v in vol if v.get('symbol') == '^VIX'), None)
    
    comm = yf.get('commodities', [])
    gold = next((c.get('price') for c in comm if c.get('symbol') == 'GC=F'), None)
    wti = next((c.get('price') for c in comm if c.get('symbol') == 'CL=F'), None)
    
    # Economic
    treasury = fred.get('treasury', {})
    
    # Conflict
    acled_sum = acled.get('summary', {})
    hotspots = acled.get('hotspots', [])
    hotspot_locs = [h.get('location', 'Unknown') for h in hotspots[:5]]
    
    # CISA alerts
    signals = cisa.get('signals', [])
    alerts = [{'severity': s.get('severity'), 'message': s.get('signal'), 'source': 'CISA-KEV'} for s in signals[:3]]
    
    # Build output
    output = {
        "metadata": {
            "source": "Crucix",
            "version": crucix.get('version', '2.0.0'),
            "last_update": crucix.get('timestamp'),
            "sources_active": crucix.get('sourcesOk', 0),
            "sources_total": crucix.get('sourcesQueried', 0),
        },
        "markets": {
            "btc": btc,
            "eth": eth,
            "spy": spy,
            "vix": vix,
            "gold": gold,
            "wti": wti,
        },
        "economic": {
            "yield_10y": treasury.get('yield_10y'),
            "yield_2y": treasury.get('yield_2y'),
            "fed_funds": fred.get('fed_funds'),
            "unemployment": fred.get('unemployment'),
            "cpi_yoy": fred.get('cpi_yoy'),
            "m2_growth": fred.get('m2_growth'),
        },
        "conflict": {
            "events_24h": acled_sum.get('events_24h', 0),
            "hotspots": hotspot_locs,
        },
        "satellite": {
            "fires_count": firms.get('count', 0),
        },
        "alerts": alerts,
    }
    
    # Save as UTF-8
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print("Crucix data converted")
    print(f"Sources: {crucix.get('sourcesOk', 0)}/{crucix.get('sourcesQueried', 0)}")
    print(f"BTC: {btc} | VIX: {vix} | Gold: {gold}")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
