# update-notion-next-bets.ps1
# Updates Notion Next Bets database with latest scan results

$NOTION_KEY = Get-Content "$env:USERPROFILE\.config\notion\api_key" -ErrorAction SilentlyContinue
if (!$NOTION_KEY) { exit }

$Headers = @{
    "Authorization" = "Bearer $NOTION_KEY"
    "Notion-Version" = "2022-06-28"
    "Content-Type" = "application/json"
}

# Get latest hot bets file
$Today = Get-Date -Format "yyyy-MM-dd"
$HotBetsFile = Get-ChildItem "C:\Users\impro\Documents\Polymarket-Scans\$Today\hot-bets-*.txt" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (!$HotBetsFile) { exit }

# Parse hot bets and add to Notion
$Content = Get-Content $HotBetsFile.FullName

foreach ($Line in $Content) {
    if ($Line -match "\[(.+?)\] Odds: (\d+%) \| Volume: (.+)") {
        $Category = $Matches[1]
        $Odds = $Matches[2]
        $Volume = $Matches[3]
        
        # Check if already exists
        $QueryBody = @{
            filter = @{
                property = "Volume"
                rich_text = @{ equals = $Volume }
            }
        } | ConvertTo-Json
        
        try {
            $Existing = Invoke-RestMethod -Uri "https://api.notion.com/v1/databases/32304917-58dd-81f2-ad8a-c8254af3d9a9/query" -Method POST -Headers $Headers -Body $QueryBody
            
            if ($Existing.results.Count -eq 0) {
                # Add new bet
                $AddBody = @{
                    parent = @{ database_id = "32304917-58dd-81f2-ad8a-c8254af3d9a9" }
                    properties = @{
                        Name = @{ title = @(@{ text = @{ content = "Auto-detected $Category Opportunity" } }) }
                        Market = @{ url = "https://polymarket.com/predictions/$Category" }
                        "Current Odds" = @{ number = ([int]($Odds -replace '%','')) / 100 }
                        Volume = @{ rich_text = @(@{ text = @{ content = $Volume } }) }
                        Category = @{ select = @{ name = $Category.Substring(0,1).ToUpper() + $Category.Substring(1).ToLower() } }
                        Priority = @{ select = @{ name = "High" } }
                        Status = @{ select = @{ name = "Pending" } }
                        "Date Added" = @{ date = @{ start = (Get-Date -Format "yyyy-MM-dd") } }
                        "Recommended Position" = @{ select = @{ name = "WATCH" } }
                    }
                } | ConvertTo-Json -Depth 10
                
                Invoke-RestMethod -Uri "https://api.notion.com/v1/pages" -Method POST -Headers $Headers -Body $AddBody | Out-Null
            }
        } catch {}
    }
}
