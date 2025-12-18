param (
    [string]$RootPath,
    [string]$OutputFile = "Folder_Structure_Report.docx"
)

# Load Word
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add()

function Add-Text($text, $bold=$false, $indent=0) {
    $para = $doc.Paragraphs.Add()
    $para.Range.Text = (" " * $indent) + $text
    $para.Range.Font.Name = "Courier New"
    $para.Range.Font.Size = 10
    $para.Range.Font.Bold = if ($bold) { 1 } else { 0 }
    $para.Format.SpaceAfter = 0
    $para.Range.InsertParagraphAfter()
}

Add-Text "FULL FOLDER STRUCTURE & CODE REPORT", $true

# Gather all files first
Write-Host "Scanning files for progress tracking..."
$allFiles = Get-ChildItem -Path $RootPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $_.Extension -match "\.py$|\.txt$|\.js$|\.html$|\.bat$|\.ps1$|\.json$|\.xml$|\.md$"
} | Where-Object {
    $_.FullName -notmatch "(__pycache__|\.git|venv|node_modules)"
}

$total = $allFiles.Count
$count = 0

function Process-Directory($path, $indent=0) {
    Add-Text "`nFOLDER: $path", $true, $indent

    Get-ChildItem -Path $path -File | Where-Object {
        $_.Extension -match "\.py$|\.txt$|\.js$|\.html$|\.bat$|\.ps1$|\.json$|\.xml$|\.md$"
    } | ForEach-Object {
        $file = $_.FullName
        Add-Text "FILE: $_", $false, $indent + 2
        try {
            $lines = Get-Content $file
            foreach ($line in $lines) {
                Add-Text "$line", $false, $indent + 4
            }
        } catch {
            Add-Text "[Error reading file]", $false, $indent + 4
        }
        $global:count++
        Write-Progress -Activity "Exporting Code to Word" -Status "$count / $total files" -PercentComplete (($count / $total) * 100)
    }

    Get-ChildItem -Path $path -Directory | Where-Object {
        $_.FullName -notmatch "(__pycache__|\.git|venv|node_modules)"
    } | ForEach-Object {
        Process-Directory $_.FullName ($indent + 2)
    }
}

Process-Directory $RootPath

$doc.SaveAs([ref] (Join-Path -Path $PSScriptRoot -ChildPath $OutputFile))
$doc.Close()
$word.Quit()

Write-Host "Done. Export saved to $OutputFile"
