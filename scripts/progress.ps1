#requires -Version 7
<#
.SYNOPSIS
  Regenerates PROGRESS.md from the state files. A viewer, not state.

.DESCRIPTION
  Reads ROADMAP.md, topics/*/mastery.md, topics/*/gaps.md,
  topics/*/sessions/*.md (frontmatter + Grades table), review/queue.md,
  review/log.md and review/weekly/*.md, and writes PROGRESS.md.

  Run from anywhere:  pwsh scripts/progress.ps1
  Formats are the ones fixed in .claude/skills/*/SKILL.md. If a file does
  not parse, the script says which line and stops — it never guesses.

.PARAMETER Today
  Override the date (yyyy-MM-dd). For testing.
#>
[CmdletBinding()]
param(
    [string]$Today
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# Dashboard numbers use "." regardless of the machine's locale.
[System.Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture

$Root  = Split-Path -Parent $PSScriptRoot
$Now   = if ($Today) { [datetime]::ParseExact($Today, 'yyyy-MM-dd', $null) } else { (Get-Date).Date }
$OutFile = Join-Path $Root 'PROGRESS.md'

# ---------------------------------------------------------------- helpers

function Read-Lines([string]$Path) {
    if (-not (Test-Path $Path)) { return @() }
    return [System.IO.File]::ReadAllLines($Path, [System.Text.Encoding]::UTF8)
}

# Parses a markdown table row into trimmed cells. Returns $null for
# non-rows and separator rows.
function Parse-Row([string]$Line) {
    $t = $Line.Trim()
    if (-not $t.StartsWith('|')) { return $null }
    if ($t -match '^\|\s*-{3,}') { return $null }
    $cells = $t.Trim('|').Split('|') | ForEach-Object { $_.Trim() }
    return ,$cells
}

function Parse-Date([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s) -or $s -eq '—' -or $s -eq '-') { return $null }
    # "2026-09-14 [[link]]" -> take the leading date
    if ($s -match '^(\d{4}-\d{2}-\d{2})') { return [datetime]::ParseExact($Matches[1], 'yyyy-MM-dd', $null) }
    return $null
}

function Parse-Level([string]$s) {
    if ($s -match '^L([0-5])$') { return [int]$Matches[1] }
    return $null
}

function Strip-Link([string]$s) {
    if ($s -match '^\[\[(.+?)\]\]$') { return $Matches[1] }
    return $s
}

function Fmt-Avg($values) {
    if (-not $values -or $values.Count -eq 0) { return '—' }
    return ('{0:N2}' -f (($values | Measure-Object -Average).Average))
}

function Fmt-Date($d) { if ($d) { $d.ToString('yyyy-MM-dd') } else { '—' } }

# Reads YAML-ish frontmatter: scalar keys and [a, b] lists only.
function Read-Frontmatter([string]$Path) {
    $lines = Read-Lines $Path
    if ($lines.Count -lt 2 -or $lines[0].Trim() -ne '---') { return $null }
    $fm = @{}
    for ($i = 1; $i -lt $lines.Count; $i++) {
        $l = $lines[$i]
        if ($l.Trim() -eq '---') { break }
        if ($l -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$') {
            $k = $Matches[1]; $v = $Matches[2].Trim()
            if ($v -match '^\[(.*)\]$') {
                $inner = $Matches[1].Trim()
                $fm[$k] = if ($inner -eq '') { @() } else { @($inner.Split(',') | ForEach-Object { $_.Trim() }) }
            } else {
                $fm[$k] = $v
            }
        }
    }
    return $fm
}

# ---------------------------------------------------------------- roadmap

$roadmapLines = Read-Lines (Join-Path $Root 'ROADMAP.md')
$focusTopic   = ($roadmapLines | Where-Object { $_ -match '^\*\*Focus topic:\*\*\s*(.+)$' } | ForEach-Object { $Matches[1].Trim() } | Select-Object -First 1)
$focusCluster = ($roadmapLines | Where-Object { $_ -match '^\*\*Focus cluster:\*\*\s*(.+)$' } | ForEach-Object { $Matches[1].Trim() } | Select-Object -First 1)
if (-not $focusTopic)   { $focusTopic   = '—' }
if (-not $focusCluster) { $focusCluster = 'none' }

# ---------------------------------------------------------------- topics

$topics = @()
$topicDirs = Get-ChildItem (Join-Path $Root 'topics') -Directory -ErrorAction SilentlyContinue | Sort-Object Name
foreach ($dir in $topicDirs) {
    $slug = $dir.Name
    $topicFm = Read-Frontmatter (Join-Path $dir.FullName 'TOPIC.md')
    $name = if ($topicFm -and $topicFm.ContainsKey('name')) { $topicFm['name'] } else { $slug }

    # mastery
    $clusters = @()
    $cluster = $null
    $mPath = Join-Path $dir.FullName 'mastery.md'
    $lineNo = 0
    foreach ($line in (Read-Lines $mPath)) {
        $lineNo++
        if ($line -match '^##\s+(.+)$') {
            $cluster = [ordered]@{ Name = $Matches[1].Trim(); Concepts = @() }
            $clusters += $cluster
            continue
        }
        $cells = Parse-Row $line
        if (-not $cells -or $cells[0] -eq 'Concept') { continue }
        if (-not $cluster) { throw "$mPath line ${lineNo}: table row before any '## cluster' heading" }
        if ($cells.Count -lt 4) { throw "$mPath line ${lineNo}: expected 4 cells, got $($cells.Count)" }
        $lvl = Parse-Level $cells[1]
        if ($null -eq $lvl) { throw "$mPath line ${lineNo}: level '$($cells[1])' is not L0–L5" }
        $cluster.Concepts += [pscustomobject]@{
            Slug     = Strip-Link $cells[0]
            Level    = $lvl
            Since    = Parse-Date $cells[2]
            Evidence = $cells[3]
        }
    }

    # gaps
    $gaps = @()
    $gPath = Join-Path $dir.FullName 'gaps.md'
    $lineNo = 0
    foreach ($line in (Read-Lines $gPath)) {
        $lineNo++
        $cells = Parse-Row $line
        if (-not $cells -or $cells[0] -eq 'Date') { continue }
        if ($cells.Count -lt 6) { throw "$gPath line ${lineNo}: expected 6 cells, got $($cells.Count)" }
        $gaps += [pscustomobject]@{
            Date    = Parse-Date $cells[0]
            Concept = Strip-Link $cells[1]
            Miss    = $cells[2]
            Status  = $cells[4]
            Updated = Parse-Date $cells[5]
        }
    }

    # sessions
    $sessions = @()
    $sDir = Join-Path $dir.FullName 'sessions'
    foreach ($f in (Get-ChildItem $sDir -Filter '*.md' -File -ErrorAction SilentlyContinue)) {
        $fm = Read-Frontmatter $f.FullName
        if (-not $fm) { throw "$($f.FullName): missing frontmatter" }
        foreach ($k in 'date', 'mode') { if (-not $fm.ContainsKey($k)) { throw "$($f.FullName): frontmatter missing '$k'" } }

        # Grades table: rows after '## Grades' until the next heading
        $grades = @(); $inGrades = $false
        foreach ($line in (Read-Lines $f.FullName)) {
            if ($line -match '^##\s+Grades') { $inGrades = $true; continue }
            if ($inGrades -and $line -match '^##\s+') { break }
            if (-not $inGrades) { continue }
            $cells = Parse-Row $line
            if (-not $cells -or $cells[0] -eq 'Q') { continue }
            if ($cells.Count -lt 6) { continue }
            $grades += [pscustomobject]@{
                Q       = $cells[0]
                Concept = Strip-Link $cells[1]
                Target  = Parse-Level $cells[2]
                Awarded = Parse-Level $cells[3]
                Weak    = ($cells[4] -eq 'weak')
                Dispute = ($cells[5] -ne '—' -and $cells[5] -ne '-' -and $cells[5] -ne '')
            }
        }

        $sessions += [pscustomobject]@{
            File       = $f.BaseName
            Date       = Parse-Date $fm['date']
            Mode       = $fm['mode']
            Excursion  = ($fm.ContainsKey('excursion') -and $fm['excursion'] -eq 'true')
            AvgTarget  = if ($fm.ContainsKey('avg_target'))  { [double]$fm['avg_target'] }  else { $null }
            AvgAwarded = if ($fm.ContainsKey('avg_awarded')) { [double]$fm['avg_awarded'] } else { $null }
            Disputes   = if ($fm.ContainsKey('disputes'))    { [int]$fm['disputes'] }       else { 0 }
            Grades     = $grades
        }
    }

    $topics += [pscustomobject]@{
        Slug     = $slug
        Name     = $name
        Clusters = $clusters
        Gaps     = $gaps
        Sessions = $sessions | Sort-Object Date
    }
}

# ---------------------------------------------------------------- queue

$queue = @()
$qPath = Join-Path $Root 'review/queue.md'
$lineNo = 0
foreach ($line in (Read-Lines $qPath)) {
    $lineNo++
    $cells = Parse-Row $line
    if (-not $cells -or $cells[0] -eq 'Concept') { continue }
    if ($cells.Count -lt 4) { throw "$qPath line ${lineNo}: expected 4 cells, got $($cells.Count)" }
    $queue += [pscustomobject]@{
        Concept = Strip-Link $cells[0]
        Topic   = $cells[1]
        Last    = Parse-Date $cells[2]
        Next    = Parse-Date $cells[3]
    }
}

# ---------------------------------------------------------------- log

$log = @()
$lPath = Join-Path $Root 'review/log.md'
$lineNo = 0
foreach ($line in (Read-Lines $lPath)) {
    $lineNo++
    $cells = Parse-Row $line
    if (-not $cells -or $cells[0] -eq 'Date') { continue }
    if ($cells.Count -lt 9) { throw "$lPath line ${lineNo}: expected 9 cells, got $($cells.Count)" }
    $log += [pscustomobject]@{
        Date  = Parse-Date $cells[0]
        Topic = $cells[1]
        Mode  = $cells[2]
        Slug  = $cells[3]
    }
}

# ---------------------------------------------------------------- weekly

$lastWeekly = Get-ChildItem (Join-Path $Root 'review/weekly') -Filter '*.md' -File -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending | Select-Object -First 1

# ---------------------------------------------------------------- compute

$allSessions       = $topics | ForEach-Object { $_.Sessions }
$interviewSessions = @($allSessions | Where-Object { $_.Mode -eq 'interview' } | Sort-Object Date)
$recent8           = @($interviewSessions | Select-Object -Last 8)

$weakButHigh = @()
foreach ($s in $interviewSessions) {
    foreach ($g in $s.Grades) {
        if ($g.Weak -and $null -ne $g.Awarded -and $g.Awarded -ge 3) {
            $weakButHigh += [pscustomobject]@{ Session = $s.File; Q = $g.Q; Concept = $g.Concept; Awarded = $g.Awarded }
        }
    }
}

$overdue  = @($queue | Where-Object { $_.Next -and $_.Next -le $Now } | Sort-Object Next)
$dueSoon  = @($queue | Where-Object { $_.Next -and $_.Next -gt $Now -and $_.Next -le $Now.AddDays(7) } | Sort-Object Next)

$last7  = @($log | Where-Object { $_.Date -and $_.Date -gt $Now.AddDays(-7) })
$last30 = @($log | Where-Object { $_.Date -and $_.Date -gt $Now.AddDays(-30) })

# ---------------------------------------------------------------- write

$sb = [System.Text.StringBuilder]::new()
function W([string]$s = '') { [void]$sb.AppendLine($s) }

W "# Progress"
W
W "Generated $($Now.ToString('yyyy-MM-dd')) by ``scripts/progress.ps1``. Do not edit — regenerate."
W
W "**Focus:** $focusTopic · cluster: $focusCluster"
W

# --- calibration
W "## Calibration checkpoint"
W
$n = $interviewSessions.Count
W "Interview sessions: **$n / 5**."
if ($weakButHigh.Count -eq 0) {
    W "Self-flagged-weak answers graded L3+: **0**."
} else {
    W "Self-flagged-weak answers graded L3+: **$($weakButHigh.Count)** — the checkpoint condition is met; tighten the rubric anchors."
    W
    W "| Session | Q | Concept | Awarded |"
    W "|---|---|---|---|"
    foreach ($w in $weakButHigh) { W "| [[$($w.Session)]] | $($w.Q) | [[$($w.Concept)]] | L$($w.Awarded) |" }
}
W

# --- softness
W "## Softness — last $($recent8.Count) interview sessions"
W
if ($recent8.Count -lt 2) {
    W "Not enough interview sessions to compare. Needs 2; has $($recent8.Count)."
} else {
    W "| Session | Date | Target avg | Awarded avg | Gap | Disputes |"
    W "|---|---|---|---|---|---|"
    foreach ($s in $recent8) {
        $gap = if ($null -ne $s.AvgTarget -and $null -ne $s.AvgAwarded) { '{0:N2}' -f ($s.AvgTarget - $s.AvgAwarded) } else { '—' }
        W "| [[$($s.File)]] | $(Fmt-Date $s.Date) | $('{0:N2}' -f $s.AvgTarget) | $('{0:N2}' -f $s.AvgAwarded) | $gap | $($s.Disputes) |"
    }
    $half = [math]::Floor($recent8.Count / 2)
    $first = @($recent8 | Select-Object -First $half); $second = @($recent8 | Select-Object -Last ($recent8.Count - $half))
    $tFirst = ($first | ForEach-Object { $_.AvgTarget } | Measure-Object -Average).Average
    $tSecond = ($second | ForEach-Object { $_.AvgTarget } | Measure-Object -Average).Average
    $aFirst = ($first | ForEach-Object { $_.AvgAwarded } | Measure-Object -Average).Average
    $aSecond = ($second | ForEach-Object { $_.AvgAwarded } | Measure-Object -Average).Average
    W
    W ("Older half → newer half: target {0:N2} → {1:N2} ({2:+0.00;-0.00;0.00}), awarded {3:N2} → {4:N2} ({5:+0.00;-0.00;0.00})." -f $tFirst, $tSecond, ($tSecond - $tFirst), $aFirst, $aSecond, ($aSecond - $aFirst))
    if (($aSecond - $aFirst) -gt 0.25 -and ($tSecond - $tFirst) -le 0) {
        W
        W "**Awarded is rising while target is not. That is the drift signal.**"
    }
}
W

# --- per topic
foreach ($t in $topics) {
    $all = @($t.Clusters | ForEach-Object { $_.Concepts })
    W "## $($t.Name)"
    W
    if ($all.Count -eq 0) { W "No concepts enumerated."; W; continue }

    $dist = 0..5 | ForEach-Object { $l = $_; @($all | Where-Object { $_.Level -eq $l }).Count }
    $lastEvidence = ($all | Where-Object { $_.Since } | Sort-Object Since -Descending | Select-Object -First 1)
    W "$($all.Count) concepts · average **L$(Fmt-Avg ($all | ForEach-Object { $_.Level }))** · last evidence $(if ($lastEvidence) { Fmt-Date $lastEvidence.Since } else { '—' })"
    W
    W "| L0 | L1 | L2 | L3 | L4 | L5 |"
    W "|---|---|---|---|---|---|"
    W "| $($dist -join ' | ') |"
    W
    W "| Cluster | Concepts | Avg | L0 | ≥L3 | Last evidence |"
    W "|---|---|---|---|---|---|"
    foreach ($c in $t.Clusters) {
        $cs = @($c.Concepts)
        if ($cs.Count -eq 0) { continue }
        $l0 = @($cs | Where-Object { $_.Level -eq 0 }).Count
        $ge3 = @($cs | Where-Object { $_.Level -ge 3 }).Count
        $le = ($cs | Where-Object { $_.Since } | Sort-Object Since -Descending | Select-Object -First 1)
        W "| $($c.Name) | $($cs.Count) | L$(Fmt-Avg ($cs | ForEach-Object { $_.Level })) | $l0 | $ge3 | $(if ($le) { Fmt-Date $le.Since } else { '—' }) |"
    }
    W

    # gaps
    $g = @($t.Gaps)
    $byStatus = 'open', 'studying', 'taught', 'verified', 'regressed' | ForEach-Object {
        $st = $_; "$st $(@($g | Where-Object { $_.Status -eq $st }).Count)"
    }
    W "**Gaps:** $($byStatus -join ' · ')"
    $stale = @($g | Where-Object { $_.Status -eq 'open' -and $_.Date -and $_.Date -le $Now.AddDays(-7) })
    if ($stale.Count -gt 0) {
        W
        W "Open for more than 7 days:"
        W
        foreach ($x in $stale) { W "- [[$($x.Concept)]] — $($x.Miss) (since $(Fmt-Date $x.Date))" }
    }
    $regressed = @($g | Where-Object { $_.Status -eq 'regressed' })
    if ($regressed.Count -gt 0) {
        W
        W "**Regressed** — taught, then failed:"
        W
        foreach ($x in $regressed) { W "- [[$($x.Concept)]] — $($x.Miss) (regressed $(Fmt-Date $x.Updated))" }
    }
    W
}

# --- queue
W "## Review queue"
W
W "$($queue.Count) scheduled · **$($overdue.Count) overdue** · $($dueSoon.Count) due in the next 7 days."
if ($overdue.Count -gt 0) {
    W
    W "| Concept | Topic | Due | Days overdue |"
    W "|---|---|---|---|"
    foreach ($q in ($overdue | Select-Object -First 15)) {
        W "| [[$($q.Concept)]] | $($q.Topic) | $(Fmt-Date $q.Next) | $([int]($Now - $q.Next).TotalDays) |"
    }
}
if ($dueSoon.Count -gt 0) {
    W
    W ("Due soon: " + (($dueSoon | Select-Object -First 10 | ForEach-Object { "[[$($_.Concept)]] $(Fmt-Date $_.Next)" }) -join ' · '))
}
W

# --- activity
W "## Activity"
W
$modes = 'interview', 'teach', 'study', 'review'
$row7  = $modes | ForEach-Object { $m = $_; @($last7  | Where-Object { $_.Mode -eq $m }).Count }
$row30 = $modes | ForEach-Object { $m = $_; @($last30 | Where-Object { $_.Mode -eq $m }).Count }
$rowAll = $modes | ForEach-Object { $m = $_; @($log | Where-Object { $_.Mode -eq $m }).Count }
W "| Window | Interview | Teach | Study | Review |"
W "|---|---|---|---|---|"
W "| Last 7 days | $($row7 -join ' | ') |"
W "| Last 30 days | $($row30 -join ' | ') |"
W "| All time | $($rowAll -join ' | ') |"
W
$excursions = @($interviewSessions | Where-Object { $_.Excursion }).Count
W "Excursions: $excursions of $($interviewSessions.Count) interview sessions."
$lastLog = $log | Where-Object { $_.Date } | Sort-Object Date -Descending | Select-Object -First 1
W "Last session: $(if ($lastLog) { "$(Fmt-Date $lastLog.Date) — $($lastLog.Mode) — $($lastLog.Slug)" } else { 'none' })."
W "Last weekly review: $(if ($lastWeekly) { "[[$($lastWeekly.BaseName)]]" } else { 'none' })."

[System.IO.File]::WriteAllText($OutFile, $sb.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Host "Wrote $OutFile"
