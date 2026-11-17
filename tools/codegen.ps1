# Generate from the user-provided game, then apply the port's worker backoff.
param([Parameter(Mandatory=$true)][string]$Rexglue)
$ErrorActionPreference = 'Stop'
$portRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location (Join-Path $portRoot 'app')
try {
    New-Item -ItemType Directory -Force (Join-Path $portRoot 'out') | Out-Null
    $env:REX_MAX_JUMP_TABLE_ENTRIES = '4096'
    $env:REXGLUE_DUMP_IMAGE = Join-Path $portRoot 'out/default_image.bin'
    & $Rexglue codegen mtg12_manifest.toml
    if ($LASTEXITCODE -ne 0) { throw 'Code generation failed' }
    py -3 (Join-Path $PSScriptRoot 'prepare_codegen.py')
    if ($LASTEXITCODE -ne 0) { throw 'Worker preparation failed' }
    [IO.File]::WriteAllText((Join-Path $portRoot 'app/generated/codegen_profile.txt'), 'optimised+worker-backoff')
} finally { Pop-Location }
