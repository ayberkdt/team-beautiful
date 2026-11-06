"""One-off text edits of main.tex (round 2: fit 5 pages, shorter sentences)."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "latex" / "main.tex"
s = p.read_text(encoding="utf-8")
PAIRS = [
    (r"""Advionics asks us to automate this chain: radar data in,
heading and glidepath corrections out, and a clear cue to the pilot, with no controller \cite{brief}.""",
     r"""Advionics asks us to automate this chain with no controller. Radar data goes
in, and heading and glidepath corrections go out as a clear cue to the pilot \cite{brief}."""),
    (r"""A display updates with every radar plot. Voice speaks only for
important changes. A 5 s voice rhythm is a limit of the human talk-down. A display can update each second and does not
block the radio. The words are FAA words, so a pilot who knows a PAR talk-down can read them at once.""",
     r"""A display updates with every radar plot, and voice speaks only for
important changes. A 5 s voice rhythm is a limit of the human talk-down, and a display does not block the radio. The words are
FAA words, so a pilot who knows a PAR talk-down can read them at once."""),
    (r"""The test follows the brief: start at 5 NM, 150 m right and 30 m high, 3 m/s crosswind, light turbulence, 100 seeds. The first
pilot model""",
     r"""The test follows the brief. The aircraft starts at 5 NM, 150 m right and 30 m high, with 3 m/s crosswind and light turbulence. We
ran 100 seeds. The first pilot model"""),
    (r"""For the heading target, a 4 s reaction gives 95 of 100, 90 \% detection gives 96, a radar twice as good gives 100
and moderate turbulence gives 77 (ring: 76). A 300 m start at 5 m/s crosswind gives 65.""",
     r"""The heading target gives 95 of 100 with a 4 s reaction and 96 at 90 \% detection. It gives 100 with a radar twice as good
and 77 in moderate turbulence (ring: 76). A 300 m start at 5 m/s crosswind gives 65."""),
    (r"""\subsection{Agreement with Zurich}""", r"""\subsection{Zurich: agreement and replay}"""),
    (r"""\subsection{Replay of the cue}
Each track went""", r"""Each track then went"""),
    (r"""\subsection{A radar talk-down: Smolensk 2010}""", r"""\subsection{Smolensk 2010: a radar talk-down}"""),
    (r"""ICAO treats the axes differently: in azimuth the pilot gets a heading, and in elevation the pilot corrects from position
information \cite{icao4444}. The law follows this and uses radar position only.""",
     r"""ICAO treats the axes differently \cite{icao4444}. In azimuth the pilot gets a heading. In elevation the pilot corrects from position
information. The law follows this and uses radar position only."""),
    (r"""Below 1 dot the level is quiet. At 1 dot it is advise (stable approach limit \cite{fsf}), at 1.3 dots caution (EGPWS Mode 5 soft alert
\cite{egpws}), and in a missed approach state warning.""",
     r"""Below 1 dot the level is quiet. At 1 dot it is advise (stable approach limit \cite{fsf}). At 1.3 dots it is caution (EGPWS Mode 5 soft
alert \cite{egpws}). In a missed approach state it is warning."""),
    (r"""\caption{Each fault has one display state and one call. The pilot never sees old data without a mark.}""",
     r"""\caption{Each fault has one display state and one call. The pilot never sees old data without a mark. 3 s and 4 NM are UK values \cite{ra3291}; 5 s is the longest ICAO silence \cite{icao4444} and the FAA lost communications interval.}"""),
    (r"""Plots late & 3 s & Diamonds hollow, ring off, no new heading & ``Radar data delayed'' & RA 3291 \cite{ra3291}\\""",
     r"""Plots late & 3 s & Diamonds hollow, ring off, no new heading & ``Radar data delayed'' & RA 3291\\"""),
    (r"""& JO 5-10-14c; RA 3291, Doc 4444 for times\\""", r"""& JO 5-10-14c\\"""),
    (r"""In 100 seeded runs, a 4 s delay and a radar stop were each told after 3 s in all runs, and a 400 m jump after 1 s in 90 runs. No frame
showed guidance without valid data.""",
     r"""In all 100 seeded runs, the cue told a 4 s delay and a radar stop after 3 s. It told a 400 m jump after 1 s in 90 runs. No frame
showed guidance without valid data."""),
    (r"""Our work is the logic behind the display:
FAA fault rules, a silent path and a voice that yields to aircraft alerts, tested in a replay of 1000 recorded tracks.""",
     r"""Our work is the logic behind the display:
FAA fault rules, a silent path and a voice that yields to aircraft alerts. We tested it in a replay of 1000 recorded tracks."""),
    (r"""The next steps are a pilot-in-the-loop simulator trial, recorded PAR plots to replace the assumed error
model, link latency tests and an independent height check against wrong plots.""",
     r"""The next step is a pilot-in-the-loop simulator trial. Recorded PAR plots, link latency tests and an
independent height check follow."""),
]
for a, b in PAIRS:
    if a not in s:
        raise SystemExit("not found: " + a[:60])
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("ok", len(PAIRS))
