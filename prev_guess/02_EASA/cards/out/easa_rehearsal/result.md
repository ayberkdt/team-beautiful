# FICTIONAL rehearsal: unstabilised approach, long landing and runway excursion

**FICTIONAL PACK — rehearsal only.** Invented to rehearse the EASA slot. Not a real occurrence; every fact below is made up.

## What the track shows (computed; speeds are ground speeds — IAS needs the FDR)

- 1000 ft gate: 171 kt GS (VREF 135 kt), -1523 fpm, +320 ft above the 3° path, energy excess +809 ft (height + speed above VREF, as height)
- 500 ft gate: 162 kt GS (VREF 135 kt), -1635 fpm, +126 ft above the 3° path, energy excess +480 ft (height + speed above VREF, as height)
- Threshold crossed at 131 ft and 149 kt GS (nominal 50 ft)
- Touchdown 1142 m past the threshold
- Runway end passed at 63 kt GS; stopped 324 m beyond

## Timeline (192 position fixes merged with the pack's events)

| UTC | Source | Event |
|---|---|---|
| 21:09:30 | ATIS | wind 080/10 kt (tailwind on RWY 26), runway wet |
| 21:10:05 | ATC | cleared ILS RWY 26, maintain 180 kt to 4 NM |
| 21:11:10 | ATC | cleared to land RWY 26 |
| 21:11:33 | FDM (computed) | sink rate > 1000 fpm below 1000 ft: peak -1634.69, 28 s |
| 21:11:33 | FDM (computed) | ground speed > VREF + 20 kt below 1000 ft: peak 171.06, 42 s |
| 21:11:33 | FDM (computed) | above the glide path by > 1 dot (~0.35 deg) below 1000 ft: peak 3.31, 42 s |
| 21:11:33 | track (computed) | 1000 ft gate: 171 kt GS, -1523 fpm, +320 ft vs path |
| 21:11:54 | track (computed) | 500 ft gate: 162 kt GS, -1635 fpm, +126 ft vs path |
| 21:12:10 | CVR (summary) | PF: 'we will make it'; no go-around call |
| 21:12:16 | track (computed) | threshold crossed at 131 ft, 149 kt GS |
| 21:12:18 | FDM (computed) | ground speed > VREF + 20 kt below 1000 ft: peak 169.21, 4 s |
| 21:12:30 | track (computed) | touchdown -1142 m (negative = past the threshold) |
| 21:12:54 | track (computed) | runway end passed at 63 kt GS |
| 21:13:11 | track (computed) | stopped / last fix -2824 m |

## Human factors (HFACS; hypotheses until the final report)

| Level | Category | Finding |
|---|---|---|
| Unsafe acts | Decision errors | continued an approach unstable at 1000 ft and 500 ft |
| Preconditions for unsafe acts | Adverse mental states | plan continuation bias under schedule pressure |
| Preconditions for unsafe acts | Crew resource management | PM did not call 'go around' at the stabilisation gate |
| Preconditions for unsafe acts | Physical environment | tailwind and wet runway reduced the stopping margin |
| Unsafe supervision | Inadequate supervision | FDM had flagged unstable approaches on this route without follow-up |
| Organisational influences | Organisational climate | on-time performance targets emphasised in crew briefings |

## ERCS risk score

Key risk area **excursion**, potential loss class **S** (143 on board; assessed: a ~60 kt overrun into the runway end area makes a hull loss with 20-100 fatalities the credible worst outcome, not the loss of all 143 on board (judgement)). Barriers that stopped or remained: protections, low energy → weight sum 2 → score 1. **S1 — RED** (numerical equivalent 50000).

## Draft safety recommendations (one addressee each)

1. To the **operator**: add a mandatory 'stable / go around' call at 1000 ft and 500 ft with no-fault go-around policy; audit compliance through FDM within 6 months.
2. To the **operator**: close the loop on FDM unstable-approach events: crew debrief within 14 days and route-level trend review each quarter.
3. To the **aerodrome operator**: assess a runway end safety area or arresting system for RWY 26 within 12 months.
4. To the **EASA**: evaluate certification of on-board runway overrun awareness and alerting for new large aeroplanes (systemic; SRUR candidate).

Wording: causal and contributing factors, no blame (Reg. (EU) 996/2010 Art. 5). Still needed: FDR (IAS, thrust, brakes, spoilers), CVR transcript, runway friction, crew duty records.
