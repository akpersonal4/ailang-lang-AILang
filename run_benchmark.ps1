# Minimal benchmark driver for AILang vs Python
# -------------------------------------------------
# Warm-up (3 runs each language)
Write-Host "Warm-up runs..."
for ($i = 1; $i -le 3; $i++) {
    # AILang warm-up: seed + report (output discarded)
    & ail run apps/inventory/main.ail seed > $null
    & ail run apps/inventory/main.ail report > $null
    # Python warm-up
    python apps/inventory_py/benchmark.py > $null
}

# Measured runs (10 iterations)
$results = @()
Write-Host "Measured runs..."
for ($i = 1; $i -le 10; $i++) {
    # ---- AILang ----
    # Ensure fresh state (seed again)
    & ail run apps/inventory/main.ail seed > $null
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $report = & ail run apps/inventory/main.ail report
    $stopwatch.Stop()
    $elapsed = $stopwatch.Elapsed.TotalSeconds
    $hash = [System.BitConverter]::ToString(
        [System.Security.Cryptography.SHA256]::Create().ComputeHash(
            [System.Text.Encoding]::UTF8.GetBytes($report)
        )
    ) -replace '-', ''
    $results += [pscustomobject]@{Lang='AILang';Run=$i;Time=$elapsed;Hash=$hash}

    # ---- Python ----
    $pyOut = python apps/inventory_py/benchmark.py
    # benchmark.py prints TIME:<sec> and SHA256:<hash>
    $pyTime = ($pyOut | Select-String -Pattern '^TIME:' | ForEach-Object { $_.Line.Split(":")[1].Trim() }) -as [double]
    $pyHash = ($pyOut | Select-String -Pattern '^SHA256:' | ForEach-Object { $_.Line.Split(":")[1].Trim() })
    $results += [pscustomobject]@{Lang='Python';Run=$i;Time=$pyTime;Hash=$pyHash}
}

# Save JSON results (raw list)
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$results | ConvertTo-Json -Depth 3 | Out-File -Encoding utf8 "benchmarks/results/benchmark_$timestamp.json"
Write-Host "Benchmark completed - results saved to benchmarks/results/benchmark_$timestamp.json"
