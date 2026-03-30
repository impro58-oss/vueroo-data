$path = 'C:\Users\impro\Downloads\MedTech Europe Data All.xlsx'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$workbook = $excel.Workbooks.Open($path)

Write-Output "=== SHEETS FOUND ==="
$workbook.Sheets | ForEach-Object { Write-Output $_.Name }

# Get data from first sheet
$sheet = $workbook.Sheets.Item(1)
$range = $sheet.UsedRange
$rowCount = $range.Rows.Count
$colCount = $range.Columns.Count

Write-Output ""
Write-Output "=== SHEET 1: $($sheet.Name) ==="
Write-Output "Rows: $rowCount, Columns: $colCount"
Write-Output ""

# Get headers
$headers = @()
for ($col = 1; $col -le $colCount; $col++) {
    $headers += $range.Cells.Item(1, $col).Text
}
Write-Output "HEADERS:"
Write-Output ($headers -join " | ")
Write-Output ""

# Show first 15 rows
Write-Output "FIRST 15 ROWS:"
for ($row = 1; $row -le [Math]::Min(15, $rowCount); $row++) {
    $rowData = @()
    for ($col = 1; $col -le $colCount; $col++) {
        $value = $range.Cells.Item($row, $col).Text
        if ($value -eq "") { $value = "[empty]" }
        $rowData += $value
    }
    Write-Output ($rowData -join " | ")
}

$workbook.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
