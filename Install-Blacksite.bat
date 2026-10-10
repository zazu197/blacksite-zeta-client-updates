@echo off
setlocal
rem Blacksite Zeta: readable client scanner and updater. No backups are made.
rem Close Minecraft, then double-click. You may pass a profile folder as argument 1.
rem Set BLACKSITE_OPTIMIZATIONS below to 0 to skip the four optional performance mods.
set "BLACKSITE_SELF=%~f0"
set "BLACKSITE_PROFILE=%~1"
set "BLACKSITE_OPTIMIZATIONS=1"
set "BLACKSITE_MANIFEST_URL=https://raw.githubusercontent.com/zazu197/blacksite-zeta-client-updates/main/client-manifest.json"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$s=[IO.File]::ReadAllText($env:BLACKSITE_SELF); $code=$s.Substring($s.IndexOf(([char]10+'# POWERSHELL START'))+1); & ([scriptblock]::Create($code))"
set "BLACKSITE_EXIT=%ERRORLEVEL%"
if not "%BLACKSITE_NO_PAUSE%"=="1" pause
exit /b %BLACKSITE_EXIT%
# POWERSHELL START
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Add-Type -AssemblyName System.IO.Compression.FileSystem
$taskTemporaryFiles = [Collections.Generic.List[string]]::new()
function Get-Sha256([string]$Path) {
    $hasher = [Security.Cryptography.SHA256]::Create(); $stream = [IO.File]::OpenRead($Path)
    try { return [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $hasher.Dispose() }
}
function Get-SafeChild([string]$Root, [string]$Relative) {
    if (-not $Relative -or $Relative -match '(^|/)\.\.(/|$)|[\\:]|^/|[<>"|?*\x00-\x1F]') { throw "Unsafe file path: $Relative" }
    $resolved = [IO.Path]::GetFullPath((Join-Path $Root $Relative))
    $prefix = [IO.Path]::GetFullPath($Root).TrimEnd('\')+'\'
    if (-not $resolved.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { throw 'File path leaves its folder.' }
    return $resolved
}
function Assert-DownloadUrl([string]$Url) {
    $uri = [uri]$Url
    if ($env:BLACKSITE_TEST_MODE -eq '1' -and $uri.Scheme -eq 'http' -and $uri.Host -eq '127.0.0.1') { return }
    if ($uri.Scheme -ne 'https' -or $uri.UserInfo) { throw 'Downloads must use HTTPS.' }
    $github = $uri.Host -eq 'github.com' -and $uri.AbsolutePath.StartsWith('/zazu197/blacksite-zeta-client-updates/releases/download/')
    $raw = $uri.Host -eq 'raw.githubusercontent.com' -and $uri.AbsolutePath -eq '/zazu197/blacksite-zeta-client-updates/main/client-manifest.json'
    $author = $uri.Host -eq 'cdn.modrinth.com' -and $uri.AbsolutePath.StartsWith('/data/')
    $curseforge = $uri.Host -eq 'edge.forgecdn.net' -and $uri.AbsolutePath.StartsWith('/files/')
    if (-not ($github -or $raw -or $author -or $curseforge)) { throw 'Unexpected download source.' }
}
function Download-File([string]$Url,[string]$Path) {
    Assert-DownloadUrl $Url
    for ($attempt=1; $attempt -le 3; $attempt++) {
        $client = [Net.WebClient]::new(); $client.Headers['User-Agent']='Blacksite-Zeta-Client-Updater/1'
        try { $client.DownloadFile($Url,$Path); return }
        catch { if ($attempt -eq 3) { throw }; Start-Sleep -Seconds $attempt }
        finally { $client.Dispose() }
    }
}
function Test-Bytes([string]$Path,$File) {
    return (Test-Path -LiteralPath $Path -PathType Leaf) -and (Get-Item -LiteralPath $Path).Length -eq $File.size -and (Get-Sha256 $Path) -eq $File.sha256
}
function Get-ModIds([string]$Path) {
    $archive = $null
    try {
        $archive = [IO.Compression.ZipFile]::OpenRead($Path)
        foreach ($name in @('META-INF/neoforge.mods.toml','META-INF/mods.toml')) {
            $entry=$archive.GetEntry($name)
            if ($entry) {
                $reader=[IO.StreamReader]::new($entry.Open())
                try { $text=$reader.ReadToEnd() } finally { $reader.Dispose() }
                foreach ($part in [regex]::Split($text,'(?m)^\s*\[\[mods\]\]\s*$') | Select-Object -Skip 1) {
                    $body=([regex]::Split($part,'(?m)^\s*\['))[0]
                    $match=[regex]::Match($body,'(?m)^\s*modId\s*=\s*["'']([A-Za-z0-9_-]+)["'']')
                    if ($match.Success) { $match.Groups[1].Value }
                }
                return
            }
        }
        $entry=$archive.GetEntry('fabric.mod.json')
        if ($entry) { $reader=[IO.StreamReader]::new($entry.Open()); try { ($reader.ReadToEnd() | ConvertFrom-Json).id } finally { $reader.Dispose() } }
    } catch { return } finally { if ($archive) { $archive.Dispose() } }
}
function Test-BlacksiteProfile([string]$Path,[bool]$Explicit=$false) {
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $false }
    $metadata=Join-Path $Path 'minecraftinstance.json'; $version=$null; $neo=$false
    if (Test-Path -LiteralPath $metadata) {
        try { $json=[IO.File]::ReadAllText($metadata); $instance=$json | ConvertFrom-Json; $version=$instance.gameVersion; $neo=$json -match 'neoforge' } catch { return $false }
        if ($version -and $version -ne '1.21.1') { return $false }
    }
    $mods=Join-Path $Path 'mods'; $anchors=0
    foreach ($name in @('Mekanism-1.21.1-10.7.19.85.jar','ars_nouveau-1.21.1-5.13.3.jar','create-1.21.1-6.0.10.jar')) {
        if (Test-Path -LiteralPath (Join-Path $mods $name)) { $anchors++ }
    }
    if ($anchors -ge 2) { return $true }
    if ($version -eq '1.21.1' -and $neo -and ($Explicit -or (Split-Path $Path -Leaf) -match 'Blacksite|Magitech|All of Create')) { return $true }
    return $false
}
function Find-BlacksiteProfile {
    if ($env:BLACKSITE_PROFILE) {
        $path=(Resolve-Path -LiteralPath $env:BLACKSITE_PROFILE).Path
        if (-not (Test-BlacksiteProfile $path $true)) { throw 'Choose your Blacksite Minecraft 1.21.1 NeoForge profile.' }
        return $path
    }
    $roots=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($base in @($env:USERPROFILE,[Environment]::GetFolderPath('MyDocuments'),$env:OneDrive,$env:LOCALAPPDATA)) {
        if ($base) { [void]$roots.Add((Join-Path $base 'curseforge/minecraft/Instances')) }
    }
    $storage=Join-Path $env:APPDATA 'CurseForge/storage.json'
    if (Test-Path -LiteralPath $storage) {
        try {
            $text=[IO.File]::ReadAllText($storage); $stored=$text | ConvertFrom-Json; $settings=$stored.'minecraft-settings'
            if ($settings -is [string]) { $settings=$settings | ConvertFrom-Json }
            if ($settings.minecraftRoot) { [void]$roots.Add((Join-Path $settings.minecraftRoot 'Instances')) }
            foreach ($match in [regex]::Matches($text,'"(?:[^"\\]|\\.)*"')) {
                try { $value=ConvertFrom-Json $match.Value } catch { continue }
                if ($value -is [string] -and $value -match '^[A-Za-z]:[\\/]') {
                    foreach ($suffix in @('Instances','minecraft/Instances','')) {
                        $candidate=if ($suffix) { Join-Path $value $suffix } else { $value }
                        if ((Split-Path $candidate -Leaf) -eq 'Instances') { [void]$roots.Add($candidate) }
                    }
                }
            }
        } catch { Write-Host 'Could not read CurseForge custom-folder settings; checking standard locations.' }
    }
    $matches=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($root in $roots) {
        if (Test-Path -LiteralPath $root) {
            foreach ($folder in Get-ChildItem -LiteralPath $root -Directory) { if (Test-BlacksiteProfile $folder.FullName) { [void]$matches.Add($folder.FullName) } }
        }
    }
    $candidates=@($matches | Sort-Object)
    if ($candidates.Count -eq 1) { return $candidates[0] }
    if ($candidates.Count -gt 1) {
        for ($i=0;$i -lt $candidates.Count;$i++) { Write-Host "$($i+1). $($candidates[$i])" }
        $choice=Read-Host 'Choose the Blacksite profile number'; $number=0
        if (-not [int]::TryParse($choice,[ref]$number) -or $number -lt 1 -or $number -gt $candidates.Count) { throw 'Invalid profile selection.' }
        return $candidates[$number-1]
    }
    $manual=(Read-Host 'Paste the full folder path of your CurseForge Blacksite profile').Trim('"')
    if (-not (Test-BlacksiteProfile $manual $true)) { throw 'No compatible Minecraft 1.21.1 NeoForge profile found.' }
    return [IO.Path]::GetFullPath($manual)
}
function Test-Config([string]$Path,$File) {
    if ($File.policy -eq 'ifMissing') { return Test-Path -LiteralPath $Path -PathType Leaf }
    if ($File.policy -eq 'mergeJsonValues' -and (Test-Path -LiteralPath $Path)) {
        try { $existing=[IO.File]::ReadAllText($Path) | ConvertFrom-Json
            foreach ($key in $File.requiredValues.PSObject.Properties.Name) { if ($existing.$key -cne $File.requiredValues.$key) { return $false } }
            return $true
        } catch { return $false }
    }
    if ($File.policy -eq 'mergeTomlSettings' -and (Test-Path -LiteralPath $Path)) {
        $text=[IO.File]::ReadAllText($Path)
        foreach ($key in $File.requiredValues.PSObject.Properties.Name) {
            $matches=[regex]::Matches($text,('(?m)^\s*'+[regex]::Escape($key)+'\s*=\s*'+[regex]::Escape([string]$File.requiredValues.$key)+'\s*(?:#.*)?$'))
            if ($matches.Count -ne 1) { return $false }
        }
        return $true
    }
    if ($File.policy -eq 'mergeJsonArrays' -and (Test-Path -LiteralPath $Path)) {
        try {
            $existing=[IO.File]::ReadAllText($Path) | ConvertFrom-Json
            foreach ($key in $File.mergeKeys) { foreach ($value in $File.requiredArrays.$key) { if (@($existing.$key) -notcontains $value) { return $false } } }
            return $true
        } catch { return $false }
    }
    return Test-Bytes $Path $File
}
try {
    Write-Host 'Blacksite Zeta - scan, download missing mods, apply current client files'
    if ($env:BLACKSITE_TEST_MODE -ne '1') {
        $running=@(Get-CimInstance Win32_Process -Filter "Name='java.exe' OR Name='javaw.exe'" | Where-Object { $_.CommandLine -match 'minecraft|neoforge|BootstrapLauncher' })
        if ($running.Count) { throw 'Close Minecraft and run this BAT again. CurseForge may remain open.' }
    }
    $taskProfile=Find-BlacksiteProfile; Write-Host "Profile: $taskProfile"
    $taskTemp=Join-Path ([IO.Path]::GetTempPath()) ('blacksite-scan-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $taskTemp | Out-Null
    $manifestPath=Join-Path $taskTemp 'client-manifest.json'; $taskTemporaryFiles.Add($manifestPath)
    if ($env:BLACKSITE_TEST_MODE -eq '1' -and $env:BLACKSITE_TEST_MANIFEST) { Copy-Item -LiteralPath $env:BLACKSITE_TEST_MANIFEST -Destination $manifestPath }
    else { Download-File $env:BLACKSITE_MANIFEST_URL $manifestPath }
    $manifest=[IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    if ($manifest.schemaVersion -ne 1 -or $manifest.minimumInstallerVersion -gt 2 -or $manifest.minecraft -ne '1.21.1' -or $manifest.neoforge -ne '21.1.250') { throw 'Download the latest Install-Blacksite.bat from the client-update repository; this release requires a newer installer or loader.' }
    $taskMods=Join-Path $taskProfile 'mods'; $operations=[Collections.Generic.List[object]]::new(); $expectedIds=@{}; $expectedFiles=@{}; $paths=@{}
    $selected=@($manifest.mods | Where-Object { -not $_.optional -or $env:BLACKSITE_OPTIMIZATIONS -ne '0' })
    Write-Host "Checking every required mod ($($selected.Count) files including selected optimizations)..."
    $correct=0
    foreach ($mod in $selected) {
        if ($mod.file -match '[/\\]' -or $mod.file -notmatch '\.jar$' -or $mod.sha256 -notmatch '^[a-f0-9]{64}$' -or $mod.size -le 0) { throw 'Invalid mod manifest.' }
        $target=Get-SafeChild $taskProfile ('mods/'+$mod.file)
        if ($paths.ContainsKey($target)) { throw 'Duplicate mod manifest path.' }; $paths[$target]=$true; $expectedFiles[$mod.file]=$true
        foreach ($id in $mod.modIds) { if ($expectedIds.ContainsKey($id)) { throw 'Duplicate mod identity in manifest.' }; $expectedIds[$id]=$mod.file }
        Assert-DownloadUrl $mod.url
        if (Test-Bytes $target $mod) { $correct++; continue }
        Write-Host "Download/repair: $($mod.name)"
        $download=Get-SafeChild $taskTemp $mod.file; $taskTemporaryFiles.Add($download)
        Download-File $mod.url $download
        if (-not (Test-Bytes $download $mod)) { throw "Download checksum failed: $($mod.file). No profile files changed." }
        $operations.Add(@{Source=$download;Target=$target})
    }
    $configChanges=[Collections.Generic.List[object]]::new()
    foreach ($file in $manifest.files) {
        if ($file.optional -and $env:BLACKSITE_OPTIMIZATIONS -eq '0') { continue }
        if ($file.path -notmatch '^(config|defaultconfigs|kubejs|resourcepacks|shaderpacks|configureddefaults|blacksite-guides)/' -or $file.policy -notin @('replace','ifMissing','mergeJsonArrays','mergeJsonValues','mergeTomlSettings') -or $file.sha256 -notmatch '^[a-f0-9]{64}$' -or $file.size -lt 0) { throw 'Invalid configuration manifest.' }
        $target=Get-SafeChild $taskProfile $file.path
        if ($paths.ContainsKey($target)) { throw 'Duplicate client file path.' }; $paths[$target]=$true
        if (-not (Test-Config $target $file)) { $configChanges.Add(@{File=$file;Target=$target}) }
    }
    if ($configChanges.Count) {
        Write-Host "Fetching current configs, quests and resources ($($configChanges.Count) files to update)..."
        $archiveInfo=$manifest.configArchive; $zip=Join-Path $taskTemp 'client-files.zip'; $taskTemporaryFiles.Add($zip)
        Download-File $archiveInfo.url $zip
        if (-not (Test-Bytes $zip $archiveInfo)) { throw 'Client-files archive checksum failed. No profile files changed.' }
        $archive=[IO.Compression.ZipFile]::OpenRead($zip)
        try {
            foreach ($entry in $archive.Entries) { [void](Get-SafeChild $taskTemp $entry.FullName.TrimEnd('/')) }
            foreach ($op in $configChanges) {
                $entry=$archive.GetEntry($op.File.path); if (-not $entry) { throw "Missing archive entry: $($op.File.path)" }
                $source=Get-SafeChild (Join-Path $taskTemp 'files') $op.File.path; $taskTemporaryFiles.Add($source)
                New-Item -ItemType Directory -Path (Split-Path -Parent $source) -Force | Out-Null
                $inputStream=$entry.Open(); $outputStream=[IO.File]::Create($source)
                try { $inputStream.CopyTo($outputStream) } finally { $inputStream.Dispose();$outputStream.Dispose() }
                if (-not (Test-Bytes $source $op.File)) { throw "Client-file checksum failed: $($op.File.path). No profile files changed." }
                if ($op.File.policy -eq 'mergeJsonValues' -and (Test-Path -LiteralPath $op.Target)) {
                    $existing=[IO.File]::ReadAllText($op.Target) | ConvertFrom-Json
                    foreach ($key in $op.File.requiredValues.PSObject.Properties.Name) { $existing | Add-Member -NotePropertyName $key -NotePropertyValue $op.File.requiredValues.$key -Force }
                    [IO.File]::WriteAllText($source,($existing | ConvertTo-Json -Depth 30),[Text.UTF8Encoding]::new($false))
                }
                if ($op.File.policy -eq 'mergeTomlSettings' -and (Test-Path -LiteralPath $op.Target)) {
                    $text=[IO.File]::ReadAllText($op.Target)
                    foreach ($key in $op.File.requiredValues.PSObject.Properties.Name) {
                        $pattern='(?m)^(\s*'+[regex]::Escape($key)+'\s*=\s*)[^\r\n#]+(\s*(?:#.*)?)$'
                        if ([regex]::Matches($text,$pattern).Count -ne 1) { throw "Expected exactly one TOML setting: $key" }
                        $text=[regex]::Replace($text,$pattern,('${1}'+[string]$op.File.requiredValues.$key+'${2}'))
                    }
                    [IO.File]::WriteAllText($source,$text,[Text.UTF8Encoding]::new($false))
                }
                if ($op.File.policy -eq 'mergeJsonArrays' -and (Test-Path -LiteralPath $op.Target)) {
                    $existing=[IO.File]::ReadAllText($op.Target) | ConvertFrom-Json; $required=[IO.File]::ReadAllText($source) | ConvertFrom-Json
                    foreach ($key in $op.File.mergeKeys) {
                        $values=@(@($existing.$key)+@($required.$key) | Where-Object { $null -ne $_ } | Sort-Object -Unique)
                        $existing | Add-Member -NotePropertyName $key -NotePropertyValue $values -Force
                    }
                    [IO.File]::WriteAllText($source,($existing | ConvertTo-Json -Depth 30),[Text.UTF8Encoding]::new($false))
                }
                $operations.Add(@{Source=$source;Target=$op.Target})
            }
        } finally { $archive.Dispose() }
    }
    # Identify only known superseded/removed pack JARs; unrelated player mods stay.
    $remove=[Collections.Generic.List[string]]::new()
    if (Test-Path -LiteralPath $taskMods) {
        foreach ($jar in Get-ChildItem -LiteralPath $taskMods -Filter '*.jar' -File) {
            if ($expectedFiles.ContainsKey($jar.Name)) { continue }
            $obsolete=$false
            foreach ($prefix in $manifest.removePrefixes) { if ($jar.Name.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -and @($manifest.keepFiles) -notcontains $jar.Name) { $obsolete=$true } }
            foreach ($id in @(Get-ModIds $jar.FullName)) { if ($expectedIds.ContainsKey($id)) { $obsolete=$true } }
            foreach ($rule in $manifest.modPrefixes) { if ($expectedFiles.ContainsKey($rule.file) -and $jar.Name -match ('^'+[regex]::Escape($rule.prefix)+'[0-9]')) { $obsolete=$true } }
            if ($obsolete) { $remove.Add($jar.FullName) }
        }
    }
    Write-Host "$correct mod files already correct; $($operations.Count) files to install; $($remove.Count) obsolete pack JARs to remove."
    # Every required download has passed validation. Apply directly, with no backups.
    foreach ($op in $operations) { New-Item -ItemType Directory -Path (Split-Path -Parent $op.Target) -Force | Out-Null; Copy-Item -LiteralPath $op.Source -Destination $op.Target -Force }
    foreach ($path in $remove) { [void](Get-SafeChild $taskMods (Split-Path $path -Leaf)); Remove-Item -LiteralPath $path }
    foreach ($mod in $selected) { if (-not (Test-Bytes (Get-SafeChild $taskProfile ('mods/'+$mod.file)) $mod)) { throw "Installed file check failed: $($mod.file). Run the updater again to repair it." } }
    Write-Host "Client is current: $($manifest.version). No backups created."
    Write-Host 'Saves, screenshots, maps, controls, shader selections and unrelated mods are preserved.'
    if ($manifest.activationPending) { Write-Host 'The matching server update is still staged. Wait for the owner to activate it before joining.' -ForegroundColor Yellow }
    Write-Host 'Electric Blaze superheat: add a second Blaze Capacitor, supply 1,063 FE/t, and remove redstone signals.'
    exit 0
} catch { Write-Host ('Update stopped: '+$_.Exception.Message) -ForegroundColor Red; Write-Host 'No backups are made. Fix the reported issue and run this BAT again to repair incomplete updates.'; exit 1 }
finally { foreach ($path in $taskTemporaryFiles) { if (Test-Path -LiteralPath $path -PathType Leaf) { Remove-Item -LiteralPath $path -ErrorAction SilentlyContinue } } }
