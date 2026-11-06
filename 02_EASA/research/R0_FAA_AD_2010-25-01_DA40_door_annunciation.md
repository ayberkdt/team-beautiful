# R0 · FAA AD 2010-25-01 (Diamond DA 40 / DA 40F) — the shared "door open" annunciation, a real cry-wolf case

- **Source:** Federal Register Vol. 75, No. 234, Tuesday 7 December 2010, Rules and Regulations, pp. 75868–75869 (document
  2010-30199), Docket FAA-2010-0845, Directorate Identifier 2010-CE-044-AD; AD effective **11 January 2011**.
  PDF downloaded by subagent R2 to `D:\tmp_ideathon\easa\dl\occ\2010-30199.pdf`.
- **Read by:** main session, 4 Nov 2026 (UTC+3), via `pdftotext`. Only the comment sections below were read closely; the
  three-column layout made the rest hard to parse. Tags [D].

## What it says

- Subject: the DA 40 / DA 40F **rear passenger door** can depart in flight. The AD requires a new emergency "open doors" AFM
  procedure and replacement of the rear-door retaining bracket on certain aircraft. A commenter also states that the DA 42
  has the same door design (p. 75868).
- **Comment "Request To Separate the Canopy Latch Sensor From the Door Open Indicator"** (Thielert Engine Owners Group,
  pp. 75868–69):
  - The door-open annunciation lights whether the front canopy or the rear door is unlatched.
  - These aircraft have no air conditioning, so it is common practice to taxi with the canopy in the partially open setting,
    which lights the door-open annunciation.
  - "As a result, the pilot ignores the annunciation" and is unaware that the rear door might not be properly latched.
  - The commenter proposes rewiring so the annunciation lights only for the rear door.
- The FAA's response to that comment (agree/disagree) was not fully parsed from the column layout. **Not verified.**

## Design lessons we take [Y]

1. **One opening, one indication.** Do not aggregate the canopy and a second door (or the "open" and "not locked" states)
   into one light. That is why our unit separates CANOPY OPEN (white advisory while taxiing, where it is normal) from
   CANOPY UNLOCKED (amber/red).
2. **A light that is legitimately on during normal operations trains pilots to ignore it.** That is why parked/taxi with an
   open canopy is dark or white advisory, never amber/red, in `aerokit.canopy.logic`.
3. This is a field example of the probability-matching / cry-wolf mechanism used in the Monte Carlo (Bliss et al. 1995,
   abstract).
