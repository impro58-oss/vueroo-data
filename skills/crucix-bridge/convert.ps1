# Convert UTF-8 BOM to standard JSON and extract data
$rawPath = "$env:USERPROFILE\.openclaw\workspace\vueroo-portal\public\data\crucix_raw.json"
$outputPath = "$env:USERPROFILE\.openclaw\workspace\vueroo-portal\public\data\crucix_feed.json"

# Read and strip BOM
$bytes = [System.IO.File]::ReadAllBytes($rawPath)
if ($bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
    $bytes = $bytes[3..($bytes.Length-1)]
}
$jsonText = [System.Text.Encoding]::UTF8.GetString($bytes)

# Parse JSON
$data = $jsonText | ConvertFrom-Json

# Extract key data
$crucix = $data.crucix
$sources = $data.sources

$yf = $sources.YFinance
$fred = $sources.FRED
$acled = $sources.ACLED
$cisa = $sources.'CISA-KEV'
$firms = $sources.FIRMS

$btc = $yf.crypto.'BTC-USD'.price
$eth = $yf.crypto.'ETH-USD'.price
$spy = ($yf.indexes | Where-Object { $_.symbol -eq 'SPY' }).price
$vix = ($yf.volatility | Where-Object { $_.symbol -eq '^VIX' }).price
$gold = ($yf.commodities | Where-Object { $_.symbol -eq 'GC=F' }).price
$wti = ($yf.commodities | Where-Object { $_.symbol -eq 'CL=F' }).price

# Build output
$output = @{
    metadata = @{
        source = "Crucix"
        version = $crucix.version
        last_update = $crucix.timestamp
        sources_active = $crucix.sourcesOk
        sources_total = $crucix.sourcesQueried
    }
    markets = @{
        btc = $btc
        eth = $eth
        spy = $spy
        vix = $vix
        gold = $gold
        wti = $wti
    }
    economic = @{
        yield_10y = $fred.treasury.yield_10y
        yield_2y = $fred.treasury.yield_2y
        fed_funds = $fred.fed_funds
        unemployment = $fred.unemployment
        cpi_yoy = $fred.cpi_yoy
        m2_growth = $fred.m2_growth
    }
    conflict = @{
        events_24h = $acled.summary.events_24h
        hotspots = $acled.hotspots[0..4] | ForEach-Object { $_.location }
    }
    satellite = @{
        fires_count = $firms.count
    }
    alerts = @($cisa.signals[0..2] | ForEach-Object { @{ severity = $_.severity; message = $_.signal; source = "CISA-KEV" } })
}

# Save
$output | ConvertTo-Json -Depth 5 | Set-Content -Path $outputPath

Write-Host "Crucix data converted"
Write-Host "Sources: $($crucix.sourcesOk)/$($crucix.sourcesQueried)"
Write-Host "BTC: $btc | VIX: $vix | Gold: $gold"
Write-Host "Saved: $outputPath"
