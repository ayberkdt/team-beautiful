# R6 — FAA JO 7110.65BB rules for PAR, and what they changed in our design

Read 6 Nov 2026. **Source:** Order JO 7110.65BB, effective 20 Feb 2025, with Change 1 and 2, PDF title dated 1-22-26, sections
5-10 and 5-12, read as text from a third-party copy: https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf

The official page is https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap5_section_12.html. It loaded in the
browser pane (title "Chapter 5. Radar"), but web fetch returned 403 and every browser read failed with a policy-check error.
So the text below was **not** compared with the live FAA page. Check for changes before quoting it as current.

## 1. Missed approach: 5-10-14 Final Approach Abnormalities

The controller instructs the aircraft, **if the runway environment is not in sight**, to execute a missed approach (if one
was given) or to climb and fly a specified course, whenever a safe approach is questionable because:

- (a) safety limits are exceeded or radical target deviations are observed;
- (b) position or identification of the aircraft is in doubt;
- (c) radar contact is lost or a malfunctioning radar is suspected.

Phrase for a, b, c: (reason) IF RUNWAY/APPROACH LIGHTS/RUNWAY LIGHTS NOT IN SIGHT, EXECUTE MISSED APPROACH/(alternative
instructions). Example reasons: "Radar contact lost." "Too high/low for safe approach." "Too far right/left for safe approach."

**(a), (b) and (c) do not apply after the aircraft passes decision height on a PAR approach.**

- (d) airport conditions or traffic preclude approach completion. Phrase: EXECUTE MISSED APPROACH/(alternative instructions),
  (reason). This one has no visual condition.

If the pilot asks, approval may be given to continue by ILS or another aid.

The specific missed approach is issued before final descent when any part of the final is in IFR conditions: YOUR MISSED
APPROACH PROCEDURE IS (procedure) (5-10-11).

## 2. Lost communications: 5-10-4

The pilot is told in advance: if radio communications are lost for not more than 1 minute on vector to final, **15 s on a
surveillance final, 5 s on a PAR final**, then:

1. attempt contact on a secondary or tower frequency;
2. proceed under visual flight rules if possible;
3. proceed with an approved non-radar approach, or fly the specific lost communications procedure.

This is not a missed approach instruction. For US Navy ACLS Modes I, IA and II the same 5 s runs from loss of data link. That
is the nearest published rule to a data-link cue.

## 3. Elevation failure: 5-12-10

If the elevation part fails during a precision approach: discontinue PAR instructions and tell the aircraft to take over
visually or, if unable, to execute a missed approach. Phrase: NO GLIDEPATH INFORMATION AVAILABLE. IF RUNWAY, APPROACH/RUNWAY
LIGHTS, NOT IN SIGHT, EXECUTE MISSED APPROACH/(alternative instructions). A surveillance approach may then be offered, using
PAR azimuth.

## 4. Talk-down: 5-12-1 to 5-12-8

- 5-12-1: APPROACHING GLIDEPATH, about 10 to 30 s before final descent. 5-12-3: BEGIN DESCENT.
- 5-12-2: decision height to any pilot who asks. 5-12-6: AT DECISION HEIGHT at the published DH.
- 5-12-4a: inform when on glidepath and on course; frequently inform of any deviation; transmissions about every 5 s.
  Words: HEADING (heading). ON GLIDEPATH. ON COURSE. SLIGHTLY/WELL ABOVE/BELOW GLIDEPATH. SLIGHTLY/WELL LEFT/RIGHT OF COURSE.
- 5-12-4b: trend as required, may be modified by RAPIDLY or SLOWLY: going above/below glidepath; going right/left of course;
  above/below glidepath and coming down/up; above/below glidepath and holding; left/right of course and holding/correcting.
- 5-12-5: distance from touchdown at least once each mile.
- 5-12-7: continue position information until over the threshold. Below DH it is advisory only; 14 CFR 91.175 is the pilot's.
  OVER APPROACH LIGHTS. OVER LANDING THRESHOLD, (position).
- 5-12-8: guidance ends when the pilot asks, when a safe approach is questionable, over the threshold, or when the pilot
  reports lights in sight and says they will proceed visually. "Runway in sight" alone is not such a request.
- 5-12-9: delay transfer until the landing roll-out, so as not to divert attention at touchdown.
- 5-10-10: DO NOT ACKNOWLEDGE FURTHER TRANSMISSIONS. 5-10-13: TOWER CLEARANCE CANCELED/NOT RECEIVED (alternative instructions).

The order prints no number for "slightly", "well", safety limits or "radical deviation", and no time for "radar contact lost".

## 5. What changed in our design

Was wrong, now fixed in `src/aerokit/atc/parcue.py`:

- A flat "go around" call. Now the reason, then the condition, from 5-10-14.
- Guidance stopped at minimums. Now advisory to the threshold, with AT DECISION HEIGHT once.
- Faults after DH still called. Now no a, b, c call after DH.
- Elevation failure waited like other faults. Now it ends guidance at once, with its own phrase.
- Silence was treated as go-around. Now a radar loss and a link loss are separate: the link loss shows the lost
  communications procedure.
- Words were our own (TURN, DESCEND MORE, ON GLIDE PATH). Now 5-12-4 words.
- 5-12-8a4 added: pilot proceeding visually ends guidance. 5-10-14d and 5-10-13: tower break, not conditional.

Still ours, stated as such:

- Limit values. +-0.5 deg and +-2 deg come from one report (Smolensk), not from the FAA. Real limits are per runway inputs.
- The time for "radar contact lost": 3 s and 4 NM are UK (RA 3291), 5 s is ICAO's longest silence.
- Voice is rare on purpose. The FAA asks for a transmission about every 5 s because the voice is the only channel. Our display
  updates every second, with a heartbeat. This departs from the rule and needs a pilot trial.
- Not modelled: APPROACHING GLIDEPATH, BEGIN DESCENT, mile calls by voice, OVER APPROACH LIGHTS, surveillance approach after
  elevation failure. The replay starts established on final. Distance is on the display.
