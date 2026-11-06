# R_eurocontrol_stca_spec — EUROCONTROL Specification for Short Term Conflict Alert

## Citation
EUROCONTROL, *EUROCONTROL Specification for Short Term Conflict Alert*, EUROCONTROL-SPEC-0108, Edition 1.0, 22 November 2007, Released Issue. Contact: Ben Bakker (DAP/ATS). 23 PDF pages.
URL: https://www.eurocontrol.int/sites/default/files/2019-08/20071122-stca-spe-v1.0_0.pdf
Landing page: https://www.eurocontrol.int/publication/eurocontrol-specifications-short-term-conflict-alert-stca
Date read: 2026-11-04 (PDF text extracted; §2, §3.1, §4.3 read). Doc page = printed page.
Source class: PRIMARY. A later draft, SPEC-122 Ed 1.1 (19 May 2009), exists per a search snippet [A] and was not read.
Labels: [D-ag] read this session; [A] snippet.

## Facts [D-ag]
- §2 definitions (doc p.4): STCA is "a ground-based safety net" that alerts the controller in a timely manner to a potential or actual infringement of separation minima. **Warning time** is the time between the first alert indication and the predicted violation of separation minima. It depends on geometry, and its maximum may be capped to limit nuisance alerts.
- §3.1 (doc p.6): STCA works in the short term, "providing warning times up to 2 minutes". STCA was introduced in the mid-1980s; full-synthetic displays are now the norm.
- §4.3.1 (doc p.13): STCA-08/09 require detecting and alerting operationally relevant conflicts involving at least one eligible aircraft. STCA "should not be expected to alert all" conflicts.
- STCA-10 (doc p.14): alerts must attract attention and identify the aircraft involved; they "shall be at least visual". An audible element is optional (with an acknowledgement that silences it).
- STCA-11 / STCA-12: nuisance and false alerts must be kept to "an effective minimum".
- STCA-13 (§4.3.2 Warning Time): where geometry permits, warning time must be enough for every step from the controller noticing the alert to the aircraft completing the manoeuvre. STCA-14: alerts continue while the alert conditions exist.
- STCA-15/16 (§4.3.3): inhibition is possible per airspace volume and per flight, and inhibitions must be made known to controllers. STCA-17 (§4.3.4): status is shown if STCA is unavailable.
- Related display requirement [D-ag, from R_eurocontrol_radar_std_1997.md §5.2.2 note 4]: STCA and MSAW warnings are displayed to the controller when in use. ASTERIX CAT004 carries safety-net messages (R_eurocontrol_artas_asterix.md).

## Not covered
MSAW numeric parameters and data-block layout conventions (callsign / FL / GS / CFL, history dots, speed vector) were **not** found in a primary source this session. Partial support: radar std §5.2.1 lists position+history, identification, vertical position, ground speed and track status; §5.2.2 recommends "track prediction vectors". ESASSP lists the data items (R_esassp.md). Exact label layout is local HMI practice, not standardised in the sources read.

## Relevance to us [Y]
If our approach-guidance concept raises alerts (e.g. deviation from the final approach path, or a spacing violation), STCA's requirements are the template: visual and identifying alerts, a warning time sufficient for the controller and pilot to react (STCA itself works up to 2 min ahead), nuisance alerts minimised, and an inhibition capability. This frames a "safety-net" slide.
