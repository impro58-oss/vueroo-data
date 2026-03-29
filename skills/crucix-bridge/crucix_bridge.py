#!/usr/bin/env python3
"""
Crucix Data Bridge — Captures Crucix sweep output and converts to CycleVue format
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def run_crucix_sweep():
    """Run Crucix sweep and capture output"""
    crucix_dir = Path.home() / ".openclaw" / "workspace" / "Crucix"
    
    try:
        # Run npm run sweep and capture JSON output
        result = subprocess.run(
            ["npm", "run", "sweep"],
            cwd=crucix_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse JSON from stdout (skip any error messages)
        lines = result.stdout.strip().split('\n')
        json_lines = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('{') or line.startswith('[')):
                json_lines.append(line)
        
        if json_lines:
            # Find the last complete JSON object
            for line in reversed(json_lines):
                try:
                    data = json.loads(line)
                    if 'crucix' in data or 'sources' in data:
                        return data
                except:
                    continue
        
        print("No valid JSON found in Crucix output")
        return None
        
    except Exception as e:
        print(f"Error running Crucix: {e}")
        return None

def convert_to_cyclevue(crucix_data):
    """Convert Crucix output to CycleVue format"""
    
    if not crucix_data or 'sources' not in crucix_data:
        print("Invalid Crucix data structure")
        return None
    
    sources = crucix_data.get('sources', {})
    
    # Extract economic data
    economic = {}
    if 'FRED' in sources:
        fred = sources['FRED']
        economic = {
            'yield_curve': fred.get('treasury', {}).get('yield_10y_2y'),
            'fed_funds': fred.get('fed_funds'),
            'vix': fred.get('vix'),
            'm2_growth': fred.get('m2_growth'),
            'unemployment': fred.get('unemployment'),
            'cpi': fred.get('cpi'),
        }
    
    # Extract market data
    markets = {}
    if 'YFinance' in sources:
        yf = sources['YFinance']
        markets = {
            'btc': yf.get('crypto', {}).get('BTC-USD', {}).get('price'),
            'eth': yf.get('crypto', {}).get('ETH-USD', {}).get('price'),
            'spy': yf.get('indexes', [{}])[0].get('price') if yf.get('indexes') else None,
            'vix': yf.get('volatility', [{}])[0].get('price') if yf.get('volatility') else None,
            'gold': yf.get('commodities', [{}])[0].get('price') if yf.get('commodities') else None,
            'wti': next((c.get('price') for c in yf.get('commodities', []) if c.get('symbol') == 'CL=F'), None),
        }
    
    # Extract conflict data
    conflict = {}
    if 'ACLED' in sources:
        acled = sources['ACLED']
        conflict = {
            'events_24h': acled.get('summary', {}).get('events_24h', 0),
            'hotspots': acled.get('hotspots', []),
        }
    
    # Extract satellite data
    satellite = {}
    if 'FIRMS' in sources:
        firms = sources['FIRMS']
        satellite = {
            'thermal_anomalies': firms.get('count', 0),
            'regions': firms.get('regions', []),
        }
    
    # Build alerts from CISA-KEV
    alerts = []
    if 'CISA-KEV' in sources:
        cisa = sources['CISA-KEV']
        for signal in cisa.get('signals', []):
            alerts.append({
                'severity': signal.get('severity', 'low'),
                'message': signal.get('signal', ''),
                'source': 'CISA-KEV',
                'timestamp': datetime.now().isoformat(),
            })
    
    cyclevue_data = {
        "metadata": {
            "source": "Crucix",
            "last_update": crucix_data.get('crucix', {}).get('timestamp', datetime.now().isoformat()),
            "sources_active": crucix_data.get('crucix', {}).get('sourcesOk', 0),
            "sources_total": crucix_data.get('crucix', {}).get('sourcesQueried', 0),
        },
        "economic": economic,
        "markets": markets,
        "conflict": conflict,
        "satellite": satellite,
        "alerts": alerts,
    }
    
    return cyclevue_data

def save_data(data):
    """Save converted data to vueroo-portal"""
    output_path = Path.home() / ".openclaw" / "workspace" / "vueroo-portal" / "public" / "data" / "crucix_feed.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Data saved to {output_path}")
    return output_path

if __name__ == "__main__":
    print("Running Crucix sweep...")
    crucix_data = run_crucix_sweep()
    
    if crucix_data:
        print(f"✓ Sweep complete: {crucix_data.get('crucix', {}).get('sourcesOk', 0)}/{crucix_data.get('crucix', {}).get('sourcesQueried', 0)} sources")
        
        print("Converting to CycleVue format...")
        cyclevue_data = convert_to_cyclevue(crucix_data)
        
        if cyclevue_data:
            save_data(cyclevue_data)
            print(f"\nActive sources: {cyclevue_data['metadata']['sources_active']}")
            print(f"Alerts: {len(cyclevue_data['alerts'])}")
        else:
            print("✗ Conversion failed")
    else:
        print("✗ Sweep failed")
