"""
Pipeline Guardian — Data Pipeline Monitor
Monitors all Vueroo data silos for freshness, schema drift, and completeness.
"""

import json
import os
import sys
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Warning: 'schedule' module not installed. Continuous mode unavailable.")

# Configuration
BASE_DIR = Path("C:\\Users\\impro\\.openclaw\\workspace")
LOG_DIR = BASE_DIR / "logs" / "guardian"
ALERT_DIR = BASE_DIR / "alerts" / "pending"
DATA_DIR = BASE_DIR / "data"
GITHUB_RAW = "https://raw.githubusercontent.com/impro58-oss/rooquest1/master/data"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
ALERT_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PipelineGuardian')


@dataclass
class SiloConfig:
    name: str
    path: str
    github_url: str
    freshness_hours: int
    required_fields: List[str]
    schema_version: str


# Silo configurations
SILOS = {
    'cryptovue': SiloConfig(
        name='CryptoVue',
        path='crypto/crypto_latest.json',
        github_url=f'{GITHUB_RAW}/crypto/crypto_latest.json',
        freshness_hours=6,
        required_fields=['scan_timestamp', 'results', 'total_cryptos', 'signals_found'],
        schema_version='2.0'
    ),
    'stockvue': SiloConfig(
        name='StockVue',
        path='stocks/stocks_latest.json',
        github_url=f'{GITHUB_RAW}/stocks/stocks_latest.json',
        freshness_hours=6,
        required_fields=['scan_timestamp', 'results', 'total_stocks', 'signals_found'],
        schema_version='1.0'
    ),
    'neurovue': SiloConfig(
        name='NeuroVue',
        path='../medtech-intelligence/dashboard/data/epidemiology-comprehensive.json',
        github_url=f'{GITHUB_RAW}/medtech-intelligence/dashboard/data/epidemiology-comprehensive.json',
        freshness_hours=24,
        required_fields=['global', 'regions', 'metadata'],
        schema_version='2.0'
    ),
}


@dataclass
class CheckResult:
    silo: str
    timestamp: str
    status: str  # 'ok', 'warning', 'error', 'critical'
    freshness_ok: bool
    schema_ok: bool
    completeness_ok: bool
    github_sync_ok: bool
    message: str
    details: Dict


def load_json_file(path: Path) -> Optional[Dict]:
    """Load JSON file from local path."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return None


def fetch_github_json(url: str) -> Optional[Dict]:
    """Fetch JSON from GitHub raw URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def check_freshness(data: Dict, hours: int) -> Tuple[bool, str]:
    """Check if data is within freshness threshold."""
    try:
        scan_time_str = data.get('scan_timestamp')
        if not scan_time_str:
            return False, "No scan_timestamp found"
        
        scan_time = datetime.fromisoformat(scan_time_str.replace('Z', '+00:00'))
        age = datetime.now() - scan_time.replace(tzinfo=None)
        
        if age > timedelta(hours=hours):
            return False, f"Data is {age.total_seconds() / 3600:.1f}h old (threshold: {hours}h)"
        
        return True, f"Data is fresh ({age.total_seconds() / 3600:.1f}h old)"
    except Exception as e:
        return False, f"Freshness check error: {e}"


def check_schema(data: Dict, config: SiloConfig) -> Tuple[bool, str]:
    """Validate JSON schema matches expected structure."""
    try:
        missing_fields = [f for f in config.required_fields if f not in data]
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        # Check version if present
        if 'version' in data:
            if data['version'] != config.schema_version:
                return False, f"Schema version mismatch: {data['version']} vs {config.schema_version}"
        
        return True, "Schema validation passed"
    except Exception as e:
        return False, f"Schema check error: {e}"


def check_completeness(data: Dict) -> Tuple[bool, str]:
    """Check for null values and empty arrays in critical fields."""
    try:
        issues = []
        
        # Check results array
        results = data.get('results', [])
        if isinstance(results, list) and len(results) == 0:
            issues.append("results array is empty")
        
        # Check for null values in key metrics
        for field in ['total_cryptos', 'total_stocks', 'signals_found']:
            if field in data and data[field] is None:
                issues.append(f"{field} is null")
        
        if issues:
            return False, f"Completeness issues: {', '.join(issues)}"
        
        return True, "Completeness check passed"
    except Exception as e:
        return False, f"Completeness check error: {e}"


def check_silo(silo_key: str) -> CheckResult:
    """Run full check on a single silo."""
    config = SILOS.get(silo_key)
    if not config:
        return CheckResult(
            silo=silo_key,
            timestamp=datetime.now().isoformat(),
            status='error',
            freshness_ok=False,
            schema_ok=False,
            completeness_ok=False,
            github_sync_ok=False,
            message=f"Unknown silo: {silo_key}",
            details={}
        )
    
    logger.info(f"Checking {config.name}...")
    
    # Load local data
    local_path = DATA_DIR / config.path
    local_data = load_json_file(local_path)
    
    if not local_data:
        return CheckResult(
            silo=silo_key,
            timestamp=datetime.now().isoformat(),
            status='critical',
            freshness_ok=False,
            schema_ok=False,
            completeness_ok=False,
            github_sync_ok=False,
            message=f"Failed to load local data from {local_path}",
            details={'path': str(local_path)}
        )
    
    # Run checks
    freshness_ok, freshness_msg = check_freshness(local_data, config.freshness_hours)
    schema_ok, schema_msg = check_schema(local_data, config)
    completeness_ok, completeness_msg = check_completeness(local_data)
    
    # GitHub sync check
    github_data = fetch_github_json(config.github_url)
    github_sync_ok = github_data is not None
    
    # Determine overall status
    if not freshness_ok:
        status = 'warning'
    elif not schema_ok or not completeness_ok:
        status = 'error'
    elif not github_sync_ok:
        status = 'warning'
    else:
        status = 'ok'
    
    result = CheckResult(
        silo=silo_key,
        timestamp=datetime.now().isoformat(),
        status=status,
        freshness_ok=freshness_ok,
        schema_ok=schema_ok,
        completeness_ok=completeness_ok,
        github_sync_ok=github_sync_ok,
        message=f"{freshness_msg}; {schema_msg}; {completeness_msg}",
        details={
            'freshness': freshness_msg,
            'schema': schema_msg,
            'completeness': completeness_msg
        }
    )
    
    logger.info(f"{config.name}: {status.upper()} - {result.message}")
    
    # Save alert if not ok
    if status != 'ok':
        alert_file = ALERT_DIR / f"{silo_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alert_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
    
    return result


def check_all_silos() -> List[CheckResult]:
    """Run checks on all configured silos."""
    logger.info("=" * 60)
    logger.info("PIPELINE GUARDIAN — Full System Check")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    results = []
    for silo_key in SILOS.keys():
        result = check_silo(silo_key)
        results.append(result)
    
    # Summary
    ok_count = sum(1 for r in results if r.status == 'ok')
    warning_count = sum(1 for r in results if r.status == 'warning')
    error_count = sum(1 for r in results if r.status == 'error')
    critical_count = sum(1 for r in results if r.status == 'critical')
    
    logger.info("-" * 60)
    logger.info(f"SUMMARY: {ok_count} OK, {warning_count} warnings, {error_count} errors, {critical_count} critical")
    logger.info("=" * 60)
    
    return results


def generate_report() -> str:
    """Generate human-readable status report."""
    results = check_all_silos()
    
    report_lines = [
        "# Pipeline Guardian Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Status Summary",
        ""
    ]
    
    for result in results:
        icon = '✅' if result.status == 'ok' else '⚠️' if result.status == 'warning' else '❌'
        report_lines.append(f"{icon} **{result.silo.upper()}**: {result.status.upper()}")
        report_lines.append(f"   {result.message}")
        report_lines.append("")
    
    return '\n'.join(report_lines)


def run_continuous_monitoring():
    """Run guardian in continuous mode with hourly checks."""
    if not SCHEDULE_AVAILABLE:
        logger.error("Cannot run continuous mode: 'schedule' module not installed")
        logger.error("Install with: pip install schedule")
        return
    
    import time
    
    logger.info("Starting Pipeline Guardian continuous monitoring...")
    logger.info("Schedule: Check all silos every hour")
    
    schedule.every().hour.do(check_all_silos)
    
    # Run initial check
    check_all_silos()
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Pipeline Guardian — Data Pipeline Monitor')
    parser.add_argument('--check-all', action='store_true', help='Run full check on all silos')
    parser.add_argument('--silo', type=str, help='Check specific silo')
    parser.add_argument('--report', action='store_true', help='Generate status report')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous_monitoring()
    elif args.check_all:
        check_all_silos()
    elif args.silo:
        result = check_silo(args.silo)
        print(json.dumps(asdict(result), indent=2))
    elif args.report:
        print(generate_report())
    else:
        # Default: check all
        check_all_silos()
