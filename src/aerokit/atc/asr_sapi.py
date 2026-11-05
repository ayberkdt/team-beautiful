"""Real speech in the loop on Windows with no download: SAPI text-to-speech and the SAPI desktop recogniser.

``System.Speech`` (part of .NET Framework on Windows) gives a text-to-speech voice and the
"Microsoft Speech Recognizer 8.0 for Windows (English - US)" (both found installed on the team laptop,
2026-11-04). We drive them through PowerShell:

* :func:`synthesize` -- ATC phrase -> 16 kHz mono WAV (the "controller").
* :func:`recognize` -- WAV -> best text, overall confidence, per-word confidences and the n-best alternates, with
  either free **dictation** or a **phraseology grammar** (constrained vocabulary, the way command-recognition
  systems in ATC restrict what can be heard).

The recogniser is a general-purpose desktop engine, not an ATC-trained model: its numbers say nothing about
ATC-grade ASR. It exists so the demo can show the whole chain voice -> text -> structured advisory with real
recognition errors and real confidences. If PowerShell/System.Speech is missing, :func:`available` is False and
the text-input path is used instead.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

__all__ = ["available", "synthesize", "recognize", "recognize_batch", "PHRASE_GRAMMAR_PS", "PAR_GRAMMAR_PS"]

_PS = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File"]


def _tmpdir() -> Path:
    base = Path(os.environ.get("TEMP", tempfile.gettempdir())) / "sapi"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _run_ps(script: str, timeout: float = 120.0) -> str:
    path = _tmpdir() / f"sapi_{os.getpid()}_{abs(hash(script)) % 10**8}.ps1"
    path.write_text(script, encoding="utf-8-sig")
    res = subprocess.run(_PS + [str(path)], capture_output=True, text=True, timeout=timeout, encoding="utf-8",
                         errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"PowerShell failed: {res.stderr.strip()[:500]}")
    return res.stdout


def available() -> bool:
    """True if System.Speech TTS and an en-US recogniser can be loaded."""
    if os.name != "nt":
        return False
    try:
        out = _run_ps("Add-Type -AssemblyName System.Speech\n"
                      "$r=[System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() | "
                      "Where-Object { $_.Culture.Name -eq 'en-US' }\n"
                      "if ($r) { 'YES' } else { 'NO' }", timeout=60)
        return "YES" in out
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        return False


def synthesize(text: str, wav_path: str | Path, voice: str = "Microsoft David Desktop", rate: int = 1) -> Path:
    """Speak ``text`` into a 16 kHz 16-bit mono WAV."""
    wav_path = Path(wav_path)
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    safe = text.replace("'", "''")
    _run_ps(f"""Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {{ $s.SelectVoice('{voice}') }} catch {{ }}
$s.Rate = {int(rate)}
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$s.SetOutputToWaveFile('{str(wav_path).replace("'", "''")}', $fmt)
$s.Speak('{safe}')
$s.Dispose()
""")
    return wav_path


#: PowerShell that builds an ATC phraseology grammar (callsign + 1-3 instructions). Kept small and explicit.
PHRASE_GRAMMAR_PS = r"""
function Ch([string[]]$w) { return New-Object System.Speech.Recognition.Choices(,$w) }
function ChB([System.Speech.Recognition.GrammarBuilder[]]$b) { return New-Object System.Speech.Recognition.Choices(,$b) }
function GB() { $g = New-Object System.Speech.Recognition.GrammarBuilder; $g.Culture = $cult; return $g }
$digits = Ch @('zero','one','two','three','four','five','six','seven','eight','niner','nine','tree','fife')
function Dn($n) { $g = GB; for ($k=0; $k -lt $n; $k++) { $g.Append($digits) }; return $g }
$cs = GB; $cs.Append((Ch @('beetle','example','student','nova'))); $cs.Append($digits, 1, 4)
$alt = GB; $alt.Append($digits, 1, 2); $alt.Append('thousand'); $h = GB; $h.Append($digits); $h.Append('hundred'); $alt.Append($h, 0, 1); $alt.Append('feet', 0, 1)
$fl = GB; $fl.Append('flight level'); $fl.Append((Dn 3))
$lvl = ChB @($alt, $fl)
$hdg = GB; $hdg.Append((Ch @('turn left heading','turn right heading','fly heading'))); $hdg.Append((Dn 3))
$vert = GB; $vert.Append((Ch @('descend and maintain','climb and maintain','descend to','climb to','maintain'))); $vert.Append($lvl)
$spd = GB; $spd.Append((Ch @('reduce speed','increase speed','maintain speed'))); $spd.Append((Dn 3)); $spd.Append('knots')
$sqk = GB; $sqk.Append('squawk'); $sqk.Append((Dn 4))
$frq = GB; $frq.Append((Ch @('contact approach','contact tower','contact radar'))); $frq.Append((Dn 3)); $frq.Append('decimal'); $frq.Append($digits, 1, 3)
$qnh = GB; $qnh.Append('qnh'); $qnh.Append((Dn 4))
$side = Ch @('left','right','center')
$rwy = GB; $rwy.Append((Ch @('cleared ils approach runway','cleared to land runway'))); $rwy.Append((Dn 2)); $rwy.Append($side, 0, 1)
$ga = GB; $ga.Append('go around')
$instr = ChB @($hdg, $vert, $spd, $sqk, $frq, $qnh, $rwy, $ga)
$top = GB; $top.Append($cs); $top.Append($instr, 1, 3)
$grammar = New-Object System.Speech.Recognition.Grammar($top)
"""


#: PowerShell grammar for PAR talk-down transmissions (atc.par phrase set)
PAR_GRAMMAR_PS = r"""
function Ch([string[]]$w) { return New-Object System.Speech.Recognition.Choices(,$w) }
function ChB([System.Speech.Recognition.GrammarBuilder[]]$b) { return New-Object System.Speech.Recognition.Choices(,$b) }
function GB() { $g = New-Object System.Speech.Recognition.GrammarBuilder; $g.Culture = $cult; return $g }
$digits = Ch @('zero','one','two','three','four','five','six','seven','eight','niner','nine')
$cs = GB; $cs.Append((Ch @('beetle','example','student','nova'))); $cs.Append($digits, 1, 4)
$oncrs = GB; $oncrs.Append('on course')
$offcrs = GB; $offcrs.Append((Ch @('slightly','well'))); $offcrs.Append((Ch @('left','right'))); $offcrs.Append('of course turn'); $offcrs.Append((Ch @('left','right'))); $offcrs.Append('heading'); $offcrs.Append($digits, 3, 3)
$crs = ChB @($oncrs, $offcrs)
$ongp = GB; $ongp.Append('on glidepath')
$offgp = GB; $offgp.Append((Ch @('slightly','well'))); $offgp.Append((Ch @('above','below'))); $offgp.Append('glidepath')
$gp = ChB @($ongp, $offgp)
$tr = GB; $tr.Append((Ch @('going up','coming down'))); $tr.Append((Ch @('rapidly','slowly')))
$mi = GB; $mi.Append($digits); $mi.Append((Ch @('miles from touchdown','mile from touchdown')))
$body = GB; $body.Append($crs); $body.Append($gp); $body.Append($tr, 0, 1); $body.Append($mi, 0, 1)
$dh = GB; $dh.Append('at decision height')
$top = GB; $top.Append($cs); $top.Append((ChB @($body, $dh)), 1, 1)
$grammar = New-Object System.Speech.Recognition.Grammar($top)
"""


def _grammar_ps(mode: str) -> str:
    if mode == "grammar":
        return PHRASE_GRAMMAR_PS
    if mode == "par":
        return PAR_GRAMMAR_PS
    if mode == "dictation":
        return "$grammar = New-Object System.Speech.Recognition.DictationGrammar\n"
    raise ValueError("mode is 'grammar', 'par' or 'dictation'")


def recognize(wav_path: str | Path, mode: str = "grammar", max_alternates: int = 5) -> dict:
    """Recognise one utterance in a WAV file.

    Returns ``{"text", "confidence", "words": [(word, conf)], "alternates": [(text, conf)]}``; ``text`` is ``None``
    when the recogniser rejects the audio (that is information too: nothing reliable was heard).
    """
    grammar = _grammar_ps(mode)
    wav = str(Path(wav_path).resolve()).replace("'", "''")
    out = _run_ps(f"""Add-Type -AssemblyName System.Speech
$cult = New-Object System.Globalization.CultureInfo('en-US')
$eng = New-Object System.Speech.Recognition.SpeechRecognitionEngine($cult)
{grammar}
$eng.LoadGrammar($grammar)
$eng.MaxAlternates = {int(max_alternates)}
$eng.SetInputToWaveFile('{wav}')
$r = $eng.Recognize()
$o = @{{ text = $null; confidence = 0.0; words = @(); alternates = @() }}
if ($r -ne $null) {{
  $o.text = $r.Text; $o.confidence = [double]$r.Confidence
  $o.words = @($r.Words | ForEach-Object {{ ,@($_.Text, [double]$_.Confidence) }})
  $o.alternates = @($r.Alternates | ForEach-Object {{ ,@($_.Text, [double]$_.Confidence) }})
}}
$eng.Dispose()
$o | ConvertTo-Json -Depth 5 -Compress
""")
    line = [ln for ln in out.splitlines() if ln.strip().startswith("{")]
    if not line:
        raise RuntimeError(f"no JSON from recogniser: {out[:300]}")
    d = json.loads(line[-1])
    d["words"] = [tuple(w) for w in (d.get("words") or []) if isinstance(w, list) and len(w) == 2]
    d["alternates"] = [tuple(a) for a in (d.get("alternates") or []) if isinstance(a, list) and len(a) == 2]
    return d


def recognize_batch(wav_paths: list[str | Path], mode: str = "grammar", max_alternates: int = 5) -> list[dict]:
    """:func:`recognize` for many files in one PowerShell process (the engine and grammar are built once)."""
    grammar = _grammar_ps(mode)
    lst = _tmpdir() / f"batch_{os.getpid()}.txt"
    lst.write_text("\n".join(str(Path(w).resolve()) for w in wav_paths), encoding="utf-8")
    out = _run_ps(f"""Add-Type -AssemblyName System.Speech
$cult = New-Object System.Globalization.CultureInfo('en-US')
$eng = New-Object System.Speech.Recognition.SpeechRecognitionEngine($cult)
{grammar}
$eng.LoadGrammar($grammar)
$eng.MaxAlternates = {int(max_alternates)}
foreach ($wav in (Get-Content -Encoding UTF8 '{str(lst).replace("'", "''")}')) {{
  $eng.SetInputToWaveFile($wav)
  $r = $eng.Recognize()
  $o = @{{ file = $wav; text = $null; confidence = 0.0; words = @(); alternates = @() }}
  if ($r -ne $null) {{
    $o.text = $r.Text; $o.confidence = [double]$r.Confidence
    $o.words = @($r.Words | ForEach-Object {{ ,@($_.Text, [double]$_.Confidence) }})
    $o.alternates = @($r.Alternates | ForEach-Object {{ ,@($_.Text, [double]$_.Confidence) }})
  }}
  $eng.SetInputToNull()
  'JSON ' + ($o | ConvertTo-Json -Depth 5 -Compress)
}}
$eng.Dispose()
""", timeout=60 + 20 * len(wav_paths))
    res = []
    for ln in out.splitlines():
        if ln.startswith("JSON "):
            d = json.loads(ln[5:])
            d["words"] = [tuple(w) for w in (d.get("words") or []) if isinstance(w, list) and len(w) == 2]
            d["alternates"] = [tuple(a) for a in (d.get("alternates") or []) if isinstance(a, list) and len(a) == 2]
            res.append(d)
    if len(res) != len(wav_paths):
        raise RuntimeError(f"recogniser returned {len(res)} results for {len(wav_paths)} files")
    return res
