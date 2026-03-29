#!/usr/bin/env python3
"""
CycleVue Pro — Historical Data Collector
Builds JSON datasets from FRED, Yahoo Finance, and other sources
"""

import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import Dict, List, Optional

class CycleDataCollector:
    def __init__(self, data_dir: str = "data/cyclevue"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # API Keys from environment
        self.fred_api_key = os.getenv('FRED_API_KEY', 'YOUR_FRED_KEY')
        self.alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'YOUR_ALPHA_KEY')
        
        # FRED Series IDs
        self.fred_series = {
            'yield_curve': 'T10Y2Y',      # 10Y-2Y Spread
            'fed_funds': 'FEDFUNDS',       # Fed Funds Rate
            'm2_growth': 'M2SL',           # M2 Money Supply
            'credit_spread': 'BAA10Y',     # BAA-10Y Spread
            'unemployment': 'UNRATE',      # Unemployment
            'inflation': 'CPIAUCSL',       # CPI
            'gdp': 'GDPC1',                # Real GDP
            'debt_gdp': 'GFDEGDQ188S',     # Federal Debt/GDP
        }
        
    def fetch_fred_series(self, series_id: str, start_date: str = '2000-01-01') -> Optional[pd.DataFrame]:
        """Fetch historical data from FRED"""
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'observation_start': start_date,
            'frequency': 'm'  # Monthly
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if 'observations' not in data:
                print(f"Error fetching {series_id}: {data.get('error_message', 'Unknown error')}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            
            return df
            
        except Exception as e:
            print(f"Error fetching {series_id}: {e}")
            return None
    
    def fetch_yahoo_finance(self, symbol: str, period: str = '10y') -> Optional[pd.DataFrame]:
        """Fetch historical data from Yahoo Finance"""
        try:
            # Yahoo Finance API endpoint
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': int((datetime.now() - timedelta(days=3650)).timestamp()),
                'period2': int(datetime.now().timestamp()),
                'interval': '1mo'
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart']:
                return None
            
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            prices = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'date': pd.to_datetime(timestamps, unit='s'),
                'open': prices['open'],
                'high': prices['high'],
                'low': prices['low'],
                'close': prices['close'],
                'volume': prices['volume']
            }).dropna()
            
            return df
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def calculate_m2_growth(self, m2_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate YoY M2 growth rate"""
        m2_df = m2_df.sort_values('date')
        m2_df['m2_growth'] = m2_df['value'].pct_change(periods=12) * 100
        return m2_df.dropna(subset=['m2_growth'])
    
    def calculate_cycle_score(self, row: Dict) -> int:
        """Calculate cycle score from indicator values"""
        score = 0
        
        # Yield curve (25 points)
        yield_val = row.get('yield_curve', 0)
        if yield_val > 1.0: score += 25
        elif yield_val > 0: score += 20
        elif yield_val > -0.5: score += 15
        elif yield_val > -1.0: score += 10
        else: score += 5
        
        # Fed funds (25 points)
        rates_val = row.get('fed_funds', 5)
        if rates_val < 2.0: score += 25
        elif rates_val < 4.0: score += 20
        elif rates_val < 6.0: score += 15
        elif rates_val < 8.0: score += 10
        else: score += 5
        
        # M2 growth (25 points)
        m2_val = row.get('m2_growth', 0)
        if m2_val > 8: score += 25
        elif m2_val > 4: score += 20
        elif m2_val > 0: score += 15
        elif m2_val > -2: score += 10
        else: score += 5
        
        # Credit spread (25 points)
        credit_val = row.get('credit_spread', 2)
        if credit_val < 1.0: score += 25
        elif credit_val < 2.0: score += 20
        elif credit_val < 3.0: score += 15
        elif credit_val < 5.0: score += 10
        else: score += 5
        
        return score
    
    def build_historical_dataset(self) -> Dict:
        """Build complete historical dataset"""
        print("Building CycleVue historical dataset...")
        
        # Fetch all FRED data
        print("\nFetching FRED data...")
        fred_data = {}
        for name, series_id in self.fred_series.items():
            print(f"  Fetching {name} ({series_id})...")
            df = self.fetch_fred_series(series_id)
            if df is not None:
                fred_data[name] = df
        
        # Calculate M2 growth
        if 'm2_growth' in fred_data:
            print("\nCalculating M2 growth rates...")
            fred_data['m2_growth'] = self.calculate_m2_growth(fred_data['m2_growth'])
        
        # Fetch market data
        print("\nFetching market data...")
        vix_df = self.fetch_yahoo_finance('^VIX')
        spx_df = self.fetch_yahoo_finance('^GSPC')
        
        # Combine into monthly dataset
        print("\nBuilding monthly composite...")
        
        # Use yield curve as base (has data since 1976)
        base_df = fred_data.get('yield_curve', pd.DataFrame())
        if base_df.empty:
            print("ERROR: No base data available")
            return {}
        
        base_df = base_df.rename(columns={'value': 'yield_curve'})
        
        # Merge other indicators
        for name, df in fred_data.items():
            if name != 'yield_curve' and name != 'm2_growth':
                df = df.rename(columns={'value': name})
                base_df = base_df.merge(df[['date', name]], on='date', how='left')
        
        # Add M2 growth
        if 'm2_growth' in fred_data:
            m2_df = fred_data['m2_growth'][['date', 'm2_growth']]
            base_df = base_df.merge(m2_df, on='date', how='left')
        
        # Add market data
        if vix_df is not None:
            vix_monthly = vix_df.groupby(vix_df['date'].dt.to_period('M')).agg({
                'close': 'last'
            }).reset_index()
            vix_monthly['date'] = vix_monthly['date'].dt.to_timestamp()
            vix_monthly = vix_monthly.rename(columns={'close': 'vix'})
            base_df = base_df.merge(vix_monthly, on='date', how='left')
        
        if spx_df is not None:
            spx_monthly = spx_df.groupby(spx_df['date'].dt.to_period('M')).agg({
                'close': 'last'
            }).reset_index()
            spx_monthly['date'] = spx_monthly['date'].dt.to_timestamp()
            spx_monthly = spx_monthly.rename(columns={'close': 'sp500'})
            base_df = base_df.merge(spx_monthly, on='date', how='left')
        
        # Forward fill missing values
        base_df = base_df.fillna(method='ffill')
        
        # Calculate cycle scores
        print("\nCalculating cycle scores...")
        base_df['cycle_score'] = base_df.apply(self.calculate_cycle_score, axis=1)
        
        # Determine phase
        def get_phase(score):
            if score >= 80: return 'expansion'
            elif score >= 60: return 'late_cycle'
            elif score >= 40: return 'risk_zone'
            else: return 'crisis'
        
        base_df['phase'] = base_df['cycle_score'].apply(get_phase)
        
        # Convert to JSON format
        print("\nConverting to JSON...")
        
        dataset = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'sources': ['FRED', 'Yahoo Finance'],
                'indicators': list(self.fred_series.keys()) + ['vix', 'sp500'],
                'total_records': len(base_df)
            },
            'data': []
        }
        
        for _, row in base_df.iterrows():
            record = {
                'date': row['date'].strftime('%Y-%m-%d'),
                'yield_curve': round(row.get('yield_curve', 0), 2),
                'fed_funds': round(row.get('fed_funds', 0), 2),
                'm2_growth': round(row.get('m2_growth', 0), 2),
                'credit_spread': round(row.get('credit_spread', 0), 2),
                'unemployment': round(row.get('unemployment', 0), 2),
                'inflation': round(row.get('inflation', 0), 2),
                'debt_gdp': round(row.get('debt_gdp', 0), 2),
                'vix': round(row.get('vix', 0), 2),
                'sp500': round(row.get('sp500', 0), 2),
                'cycle_score': int(row['cycle_score']),
                'phase': row['phase']
            }
            dataset['data'].append(record)
        
        return dataset
    
    def save_dataset(self, dataset: Dict, filename: str = 'cycle_historical.json'):
        """Save dataset to JSON file"""
        filepath = self.data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"\nDataset saved to: {filepath}")
        print(f"Total records: {len(dataset['data'])}")
        print(f"Date range: {dataset['data'][0]['date']} to {dataset['data'][-1]['date']}")
        
        return filepath
    
    def update_daily(self):
        """Update with today's data"""
        print("Fetching today's data...")
        
        # This would fetch latest values and append to existing dataset
        # For now, placeholder
        
        today_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'yield_curve': -0.35,
            'fed_funds': 5.50,
            'm2_growth': -1.2,
            'credit_spread': 2.8,
            'vix': 18.5,
            'sp500': 5200,
            'cycle_score': 58,
            'phase': 'risk_zone'
        }
        
        return today_data


def main():
    """Main execution"""
    collector = CycleDataCollector()
    
    # Build historical dataset
    dataset = collector.build_historical_dataset()
    
    if dataset:
        collector.save_dataset(dataset)
        print("\n✓ Historical dataset built successfully")
    else:
        print("\n✗ Failed to build dataset")


if __name__ == '__main__':
    main()
