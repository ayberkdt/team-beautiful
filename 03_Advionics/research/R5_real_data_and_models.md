# R5 — Real approach data and sourced models for the PAR cue

Written 6 Nov 2026 for case 10 (`03_Advionics/cases/case_10_par_hybrid_cue/TECHNICAL.md`, `src/aerokit/atc/parcue.py`; both read this session).

**Tags.** [D] read at source this session. [A] search snippet only, not opened. [Y] our inference or calculation.
Every [D] carries its read date. Calculations were run on 6 Nov in scratch scripts. Nothing in `src/` or `tests/` was changed.

**Short answer.**
- Replay data: Figshare `landing_dataset.parquet`, 19,480 real Zurich landings, MIT licence, 553 MB, no login.
- Real event: Tu-154M 101 at Smolensk North, 10 Apr 2010. It is the one candidate where a ground radar talk-down was the actual guidance. The official report gives true deviation beside each "on course, on glide path" call.
- Biggest model gaps in today's simulator: gust size (0.4 m/s against about 1.1 m/s for light turbulence at 300 ft), no wind growth with height, no turn-rate limit, no plot loss, and white noise only.

---

## Part A. Real data

### A1. Candidates at a glance

Only row 1 gives many real tracks, a known runway, a usable licence and no login.

| # | Candidate | Licence | Size | Login | Real deviation? | Use |
|---:|:---|:---|---:|:---|:---|:---|
| 1 | Figshare landing set, Zurich 2019 | MIT | 553 MB | No | Yes, computed | **Replay, first choice** |
| 2 | Zenodo 7148117 go-around labels | CC BY 4.0 | 93 MB (minimal) | No | No tracks | **Labels for row 1** |
| 3 | Smolensk final report (event) | Public report, see A4 | 8.4 MB | No | Yes, stated | **Event test** |
| 4 | NTSB AAR-14/01, Asiana 214 | US Government report | 4.9 MB | No | Partly | Second event |
| 5 | 4TU five-airport arrivals | CC BY-NC-SA 3.0 | 131–462 MB each | No | Yes, computed | Avoid: non-commercial |
| 6 | `traffic` library samples | MIT (repository) | 14 KB–5.6 MB | No | Maybe | Smoke test only |
| 7 | NASA DASHlink flight data | Not stated | Unknown | No (page says public) | Yes, recorded | Host unreachable |
| 8 | NTSB docket DCA06MA009 | US Government | Unknown | No | Yes, recorded | Not opened |
| 9 | OpenSky Trino database | Application needed | Query | **Yes** | Yes, computed | Not needed now |
| 10 | Zenodo 10210178 metadata | CC BY 4.0 | 331 MB | No | No tracks | Not needed |
| 11 | Zenodo 18916312 LHR–ZRH | CC BY 4.0 | 364 MB | No | Doubtful | Smoothed: do not use |
| 12 | Turkish 1951 final report | Not read | Not read | Not read | Not read | Report not reached |

### A2. Details per candidate

**1. Figshare "Reference data sets ... historical aircraft trajectory data" (landing set).**
- Page: https://figshare.com/articles/dataset/Reference_data_sets_for_detection_and_identification_of_significant_events_in_historical_aircraft_trajectory_data_/11406735
- Metadata API: https://api.figshare.com/v2/articles/11406735 [D 6 Nov]. Licence MIT. DOI 10.6084/m9.figshare.11406735.v1.
- File: `landing_dataset.parquet`, 553,337,088 bytes, https://ndownloader.figshare.com/files/20291079 [D 6 Nov]. It redirects to S3; no login was asked.
- MD5 `c5577f450424fa74ca673ed8a168c67f`, from `traffic` source https://raw.githubusercontent.com/xoolive/traffic/master/src/traffic/data/datasets/__init__.py [D 6 Nov].
- Content: 19,480 trajectories landing at LSZH, October–November 2019, labelled with OpenSky [D 6 Nov, same API].
- Format and fields, from a range read of the Parquet footer only (no data downloaded) [D 6 Nov]: 18,177,597 rows, 20 columns. `timestamp` (UTC, 1 Oct to 30 Nov 2019), `altitude`, `geoaltitude`, `groundspeed`, `latitude`, `longitude`, `track`, `vertical_rate`, `distance` (0.02–40), `callsign`, `icao24`, `origin`, `onground`, `lastseen`, `flight_id`, `runway`, `initial_bearing`, `initial_flow`, `simple`.
- Sample rate: **not read at source** (preprint gave 403). 18,177,597 / 19,480 = 933 rows per track. That fits about 1 row per second over a 15-minute arrival from 40 NM [Y]. Check on first load with `df.groupby("flight_id").timestamp.diff()`.
- Runway threshold: known. The `runway` column names the runway, and OurAirports gives the runway ends:
  - https://davidmegginson.github.io/ourairports-data/runways.csv, 3,973,977 bytes, public domain per https://ourairports.com/data/ [D 6 Nov].
  - RWY 14: end 47.483101, 8.53473, 1402 ft, true heading 137°, displaced threshold 492 ft.
  - RWY 28: end 47.4566, 8.57045, 1416 ft, heading 276°.
  - RWY 34: end 47.4454, 8.55673, 1388 ft, heading 335°, displaced threshold 1542 ft. All [D 6 Nov].
- Glide path: known from Zenodo `go_arounds_agg.csv.gz` (15 KB, read in full) [D 6 Nov]: LSZH 14 = 3.0°, 16 = 3.0°, 28 = 3.3°, 34 = 3.3°. RWY 14 had 70,671 landings in 2019 and a go-around rate of 3.2 per 1000, so use RWY 14 first. A flight-sim briefing also says 3.3° for RWY 28 [A]. The Swiss AIP was not read.
- Real deviation: yes, computed from position. See A3 for limits.

**2. Zenodo 7148117 "Large Landing Trajectory Data Set for Go-Around Analysis".** https://zenodo.org/records/7148117; API https://zenodo.org/api/records/7148117 [D 6 Nov].
- CC BY 4.0, DOI 10.5281/zenodo.7148117. Almost 9 million landings at 176 airports in 2019, over 33,000 go-arounds.
- Files: `go_arounds_minimal.csv.gz` 92,836,941 B; `go_arounds_augmented.csv.gz` 172,668,264 B; `go_arounds_agg.csv.gz` 15,104 B; `validation_sample.zip` 1,436,435,646 B (plots only).
- Fields: time, icao24, callsign, airport, runway, has_ga, n_approaches, n_rwy_approached. Augmented adds type, `glide_slope_angle`, METAR wind and gust, QNH.
- No trajectories. Its value: join on icao24 + time to row 1, to find real go-arounds at Zurich in Oct–Nov 2019 [Y]. Its QNH column helps correct barometric altitude [Y].
- The authors' paper was refused (403 at mdpi.com; ZHAW host not found). Go-around detection method not read.

**5. 4TU "Arrival trajectories at five major European airports".** https://data.4tu.nl/v2/articles/4e042fbc-4f76-4f28-ac4b-a0120558ceba [D 6 Nov]. DOI 10.4121/20411868.v1. **CC BY-NC-SA 3.0.** The non-commercial clause fits badly with a sponsor challenge, so avoid it [Y].
- Files [D 6 Nov]: EGLC 130,604,738 B; EIDW 403,245,479 B; EHAM 415,961,928 B; EGLL 447,201,969 B; LFPG 462,074,559 B.
- EIDW footer [D 6 Nov]: 17,819,328 rows; timestamp, altitude, groundspeed, latitude, longitude, track, vertical_rate, flight_id. I saw no runway column in the fields I filtered for.

**6. `traffic` library.** Repository licence MIT (GitHub API), read 6 Nov [D]. File list from the repository tree [D 6 Nov]: `calibration/brussels_ils.json.gz` 38 KB, `featured/belevingsvlucht.json.gz` 291 KB (Transavia 737 test flight, 30 May 2018, per https://raw.githubusercontent.com/xoolive/traffic/master/docs/data_sources/samples.rst [D 6 Nov]), `collections/quickstart.json.gz` 5.65 MB.
- Sample rate not checked. The docs warn of low sampling in one example [D 6 Nov].
- Useful tool: `landing(..., method="aligned_on_ils")` finds the ILS-aligned segment (defaults: angle tolerance 0.1, 1 min, 5000 ft above airport) per https://traffic-viz.github.io/api_reference/traffic.algorithms.navigation.html [D 6 Nov].

**7. NASA DASHlink Sample Flight Data.** https://catalog.data.gov/dataset/flight-data-for-tail-655 [D 6 Nov]: "public" access, Matlab files in 8 zips per tail, 186 parameters with sample rate and units. Licence not stated. Landing page https://c3.nasa.gov/dashlink/resources/633/ [D 6 Nov, harvest record].
- `c3.nasa.gov` and `c3.ndc.nasa.gov` did not answer on 6 Nov (timeout from here), so size, parameter list and rates are unknown.
- Search snippet [A]: 35 regional jets, three years; a labelled set of 160 × 20 windows includes glideslope and localizer deviation in DDM. https://c3.nasa.gov/dashlink/static/media/dataset/DASHlink_full_data_documentation.pdf
- This would be the best source of real needle traces. Airport identity is not confirmed [A].

**8. NTSB docket DCA06MA009 (Southwest 1248, Midway 2005).** FDR factual report [D 6 Nov]: https://data.ntsb.gov/Docket/Document/docBLOB?ID=40260622&FileExtension=.PDF&FileName=Flight+Data+Recorder+10+-+Factual+Report+of+Group+Chairman-Master.PDF
- Covers the accident flight plus five aircraft that landed in the previous 25 minutes.
- Glide slope and localizer recorded as DDM. 0.0875 DDM = 1 dot GS; 1 dot = 0.35°, full scale ±0.7°. This confirms our `vert_full_scale_deg = 0.7`.
- The report says a tabular listing is in electronic format in the public docket. I could not reach that file. Plots cover short final only.

**9. OpenSky.** Trino history is open to university-affiliated researchers, government bodies and aviation authorities after an application; companies need a licence. https://openskynetwork.github.io/opensky-api/trino.html [A]. Terms page gave 403. The sample bucket `s3.opensky-network.org/data-samples`, prefix `states/`, held only an empty placeholder on 6 Nov [D].

**11. Zenodo 18916312.** https://zenodo.org/records/18916312 [D 6 Nov]: LHR–ZRH 2025, CC BY 4.0, 364.1 MB. Its pipeline applies a 5 s rolling median and removes anomalies. That removes what we want to test [Y]. Zenodo 13683341 is synthetic [A].

### A3. Recommendation

**Download these two only:**

1. `https://ndownloader.figshare.com/files/20291079` — 553 MB, MIT. Real tracks.
2. `https://zenodo.org/api/records/7148117/files/go_arounds_minimal.csv.gz/content` — 93 MB, CC BY 4.0. Go-around labels.

Reasons: real traffic, no login, a licence we may use and cite, a runway label, and a known path angle. Go-around labels give off-path cases without a search by hand.

**What this replay can and cannot show** [Y]:
- It is **open loop**. The aircraft does not react to our cue. It tests the filter, gate, wording, false alarms and how early the cue flags a real excursion. It does not test closing the loop.
- ADS-B is not truth. Treat the track as "true", add the PAR error model, and feed `Plot` at 1 Hz.
- Vertical is the weak axis:
  - Barometric altitude moves in 25 ft steps [A, ADS-B search snippets]. Volpe's surveillance data had the same 25 ft steps, and different aircraft reported different altitudes at the threshold (Hall and Soares [D 6 Nov], B2.4).
  - The footer shows `altitude` down to 1050 ft at an airport near 1400 ft, so it is not QNH-corrected [Y].
  - Use `geoaltitude`. Remove one constant per runway, from the median at 2 NM. That shows real scatter but hides any bias common to all flights.
- The path origin (GPIP, threshold crossing height) was not read for Zurich. Fit it from the data.
- Displaced thresholds must be applied along the runway heading. OurAirports says its coordinates are the centre of the runway end [D 6 Nov, https://ourairports.com/help/data-dictionary.html].

**First three tests** [Y]: (a) false DELAYED / INVALID / OUTSIDE LIMITS rate over 1000 normal RWY 14 approaches; (b) how far out the 2-dot limit trips on real localizer intercepts; (c) lead time before real go-arounds.

### A4. The real event: Tu-154M 101, Smolensk North, 10 Apr 2010

**Source.** Polish Committee for Investigation of National Aviation Accidents, Final Report 192/2010/11, 328 pages, English information copy, 8.4 MB: https://doc.rmf.pl/rmf_fm/store/rkm_en.pdf [D 6 Nov]. Pages 13–15, 40, 214–216, 253–271.

**Why this one.** A landing zone controller used radar (RSP-6M2, with a precision approach radar element) to tell the crew their position against the path, at 8, 6, 4, 3 and 2 km. That is our function. Asiana and Turkish 1951 were cockpit-side events with no radar talk-down.

**What happened** [D 6 Nov, pp. 13–15, 214–216, 253–271].
- Path 2°40′. Limits ±30′ vertical, ±2° lateral. The controller could say "on course, on glide path" only inside one third of those limits.
- The aircraft did not start down at 10 km and went high. It left the one-third zone at 9.7 km and the ±30′ limit at 9 km.
- Five position calls said on course and on path. The report states the aircraft was outside the allowed zone each time.
- It crossed the path from above at about 2,700 m, 06:40:39, and kept descending at about twice the needed rate (report: 3.41 m/s needed at 280 km/h).
- First radar-side correction: "Horizon 101" at 06:40:55, 70 m below path. First tree strike 06:41:00.5, 1,099 m from the threshold.
- The report judged the call should have come 10 s sooner. A controller needs about 5–6 s to see and report a trend (2 s for two radar refreshes, 2 s to decide, 1 s to speak).
- Voice recordings suggest a gain fault on the radar. No recording of the radar screen exists; the Committee rebuilt the display with a later flight.

**Replay table.** Height is above airfield level. Time, distance and height are from pp. 214–216. "Stated" is the report's deviation. "Fit" is [Y]: height − (distance × tan 2°40′ + 14.8 m). The 14.8 m origin was fitted on the 7 stated points (SD 2.3 m); the fit reproduces each stated deviation within 3 m. Dots use our scale from the threshold, 0.35° per dot vertical [Y].

| Time | Distance (m) | Height (m) | Stated vertical (m) | Fit vertical (m) | Vertical dots | Stated left (m) | Radio call at that moment |
|:---|---:|---:|---:|---:|---:|---:|:---|
| 06:39:12 | 10,110 | 502 | — | +16 | +0.3 | 0 | Distance ten, entering path |
| 06:39:33 | 8,300 | 528 | +130 | +127 | +2.5 | 65 | Eight, on course, on path |
| 06:39:43.5 | 7,409 | 470 | — | +110 | +2.4 | — | |
| 06:39:52.5 | 6,649 | 444 | +120 | +120 | +2.9 | 115 | Distance six, on course, on path |
| 06:40:00.5 | 5,974 | 404 | — | +111 | +3.0 | — | |
| 06:40:09 | 5,251 | 341 | — | +82 | +2.5 | — | |
| 06:40:16.5 | 4,591 | 287 | +60 | +58 | +2.1 | 130 | Four, on course, on path |
| 06:40:29.5 | 3,456 | 210 | +35 | +34 | +1.6 | 100 | Three, on course, on path |
| 06:40:41.5 | 2,521 | 114 | −20 | −18 | −1.2 | 80 | Two, on course, on path |
| 06:40:44.5 | 2,291 | 98 | — | −24 | −1.7 | — | |
| 06:40:52 | 1,696 | 39 | — | −55 | −5.3 | — | |
| 06:40:55 | 1,459 | 14 | −70 | −69 | −7.7 | 70 | Horizon 101 |
| 06:40:57.5 | 1,265 | 2 | −75 | −72 | −9.3 | 65 | Height check, level |

Ground speed from these rows: 79–86 m/s. Sink: 4.3 to 7.4 m/s, against 3.9 m/s nominal at 84 m/s [Y].

**Report inconsistencies** (use with care):
- p. 215 says 20 m **above** at 2,521 m; pp. 14 and 265 say **below**. The fit gives −18 m, so "below" is right [Y].
- p. 14 prints 394 m above aerodrome where p. 216 has 39 m; use 39 m.
- The 445 m at 7,664 m on p. 214 does not fit its neighbours; dropped.
- p. 271 says left of centreline only from 7,400 m, yet 65 m left at 8,300 m on p. 214.

**What the cue should have said** [Y]. Interpolated between rows; 1 Hz plots assumed; seconds before the first tree strike.

| Time before first strike (s) | Distance (km) | Cue with current thresholds |
|---:|---:|:---|
| 108 | 10.1 | Leaves ON GLIDE PATH (0.3 dot). DESCEND MORE |
| 106 | 9.9 | Past 0.5 dot: voice "Descend more" |
| 92 | 8.7 | 2 dots: **"Outside limits. Go around."** Latched, about 520 m above the airfield |

The real radio said "on course, on glide path" at that stage, and the first correction came 5.5 s before the strike. The cue's latched call comes about 87 s earlier.

Second test, with the limit switched off, to exercise the wording near the ground:

| Time before first strike (s) | Distance (km) | Cue, limit off |
|---:|---:|:---|
| 22 | 2.74 | Crosses the path |
| 21 | 2.67 | Below 0.3 dot. DESCEND LESS |
| 15 | 2.21 | 2 dots: OUTSIDE LIMITS, about 90 m above the airfield |

**What this event will expose in our logic** [Y]:
- **Position-only blind spot.** From 4.6 km to the path crossing the aircraft is above path but sinking about 3 m/s too fast. The law looks only at position, so it gives no warning of closure until the crossing, 7 s before 2 dots low. A 10 s line fit on vertical plots has noise near 0.7 m/s at 3 km, so a 3 m/s excess is about 4.5σ. It could serve as a warning only, not as control. This does not contradict the failed rate laws, which used 1 s rates for control.
- **Minimums.** `decision_height_m` is 60.96 m; this approach had a 100 m limit, reached at 2.3 km. It must be a parameter.
- **Bad radar stays invisible.** The table assumes good plots. If the gain fault made the radar blip wrong, our cue would inherit it, because a plausible wrong plot passes the gate. The report notes crews gave no height read-back, which removed the cross-check. An independent height source is the real defence.

**Limits and care.**
- The report states it is for prevention, and its Polish text is the official one. Other findings exist:
  - MAK published a separate report (not read; file over the fetch limit).
  - A 2018 Polish re-investigation reached different conclusions (search snippet only) [A, https://www.smolenskcrashnews.com/2018-smolensk-crash-technical-report.html].
  - Flight Safety Foundation's summary of the 2011 report agrees on the calls and the 20 m below / 80 m left point [D 6 Nov, https://flightsafety.org/asw-article/another-look-at-smolensk/].
- All 96 people on board died, and the flight carried the Polish President [D 6 Nov, report pp. 2 and 12 area]. The event is still politically charged. On a slide, cite only the deviations and calls, and say nothing about blame.
- Only 7 stated deviation points exist; lateral between them must be interpolated. Annex 1 (trajectory graphic) was not read.

### A5. Backup event: Asiana 214, San Francisco, 6 Jul 2013

Source: NTSB/AAR-14/01, 4,858,993 bytes, https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1401.pdf [D 6 Nov], pp. 6–12 and Table 1.

Visual approach to 28L, ILS glide slopes out of service, so **no glide slope deviation exists**. Position comes from height and distance, and PAPI states.

- 5.0 NM, 1125:55: about 2,085 ft MSL, 174 kt, about 400 ft above the 3° path. That is 0.75° = 2.2 dots on our scale [Y], so the cue trips OUTSIDE LIMITS here, about 115 s before impact [Y].
- 2.1 NM, 1126:54.9: 1,000 ft RA, 151 kt, 1,500 ft/min, four white PAPI.
- 1.3 NM, 1127:14.8: 500 ft RA, 137 kt, 1,200 ft/min, three white one red. About 700 ft/min was needed.
- About 400 ft RA: 134 kt, 1,100 ft/min, on path.
- 1.0 NM, 1127:24.1: 331 ft RA, 130 kt, 1 white 3 red.
- 0.7 NM, 1127:31.0: 219 ft RA, 122 kt, four red. 0.45 NM, 1127:39.3: 124 ft RA, 114 kt.
- Impact about 1127:50 (recorder note: 1127:54 is about 4 s after). Thrust levers advanced at about 1127:43.

Same blind spot: sink too high while crossing the path. Also, speed fell 30 kt but radar sees only ground speed; our cue never looks at it [Y]. Report's 777 criteria: stabilised by 1,000 ft IMC, 500 ft VMC; speed target +10/−5 kt; sink ≤ 1,000 ft/min.

FDR: 260 verified parameters. Docket tabular file not reached (`data.ntsb.gov/Docket/?NTSBNumber=DCA13MA120` is a script page; API call gave nothing).

---

## Part B. Models

### B1. Turbulence, wind shear, crosswind

**Dryden, low altitude** (below 1000 ft) from https://www.mathworks.com/help/aeroblks/drydenwindturbulencemodelcontinuous.html [D 6 Nov], which cites MIL-F-8785C and MIL-HDBK-1797. The specification text itself was not read.
- Scale lengths: L_w = h; L_u = L_v = h / (0.177 + 0.000823 h)^1.2 (h in ft). The 1797 form states these as 2L, and the page says the result is the same.
- Intensities: σ_w = 0.1 W20; σ_u = σ_v = σ_w / (0.177 + 0.000823 h)^0.4.
- W20, wind at 20 ft: light 15 kt, moderate 30 kt, severe 45 kt.
- Filters (MIL-F-8785C style): H_u = σ_u √(2L_u/πV) / (1 + (L_u/V)s). H_w = σ_w √(L_w/πV) (1 + √3 (L_w/V)s) / (1 + (L_w/V)s)². The vertical form was confirmed by a search snippet of the same site [A]; the page's own equations were partly garbled in my fetch. Check before coding.
- 1000–2000 ft: the block interpolates to the high-altitude model.

Light turbulence is already about three times our gust value at 300 ft. Today's simulator: σ 0.4 m/s, τ 5 s, same on both axes. Values [Y], V = 70 m/s:

| Class | W20 (kt) | Height (ft) | sigma_w (m/s) | sigma_u (m/s) | L_w (m) | L_u (m) | L_u/V (s) |
|:---|---:|---:|---:|---:|---:|---:|---:|
| Light | 15 | 100 | 0.77 | 1.32 | 30 | 154 | 2.2 |
| Light | 15 | 300 | 0.77 | 1.09 | 91 | 256 | 3.7 |
| Light | 15 | 1 000 | 0.77 | 0.77 | 305 | 305 | 4.4 |
| Moderate | 30 | 100 | 1.54 | 2.65 | 30 | 154 | 2.2 |
| Moderate | 30 | 300 | 1.54 | 2.18 | 91 | 256 | 3.7 |
| Moderate | 30 | 1 000 | 1.54 | 1.54 | 305 | 305 | 4.4 |
| Severe | 45 | 100 | 2.31 | 3.97 | 30 | 154 | 2.2 |
| Severe | 45 | 300 | 2.31 | 3.26 | 91 | 256 | 3.7 |
| Severe | 45 | 1 000 | 2.31 | 2.31 | 305 | 305 | 4.4 |

Note: turbulence moves the air, and the aircraft follows only part of it. Adding gust velocity directly to position, as `fly_replay` does, overstates the drift [Y].

**Wind shear.** u(h) = W20 ln(h/z0) / ln(20/z0), 3 ft < h < 1000 ft, z0 = 0.15 ft for terminal flight phases, https://www.mathworks.com/help/aeroblks/windshearmodel.html [D 6 Nov], citing MIL-F-8785C.
- Ratio to the 20 ft wind [Y]: 1.33 at 100 ft, 1.47 at 200 ft, 1.66 at 500 ft, 1.80 at 1000 ft.
- Effect [Y]: a surface crosswind of 5 m/s is about 9 m/s at 1000 ft. Our constant crosswind hides this. The drift falls as the aircraft descends, so the 80 s trim term chases a moving target.
- ICAO shear classes (kt per 100 ft): **not confirmed**; Doc 9817 is sold, and no free page gave them. FAA staff once called about 5 kt per 100 ft significant [A, https://apps.dtic.mil/sti/pdfs/ADA056780.pdf].

**Crosswind limits.**
- Annex 14 planning values as copied by Fiji CAA: 37 km/h (20 kt) for reference field length 1500 m or more, 24 km/h (13 kt) if braking is often poor or for 1200–1500 m. https://www.caaf.org.fj/wp-content/uploads/2025/09/SD-Aerodromes-Appendix-3-Physical-Requirements-of-an-Aerodrome-Movement-Area.pdf [D 6 Nov]. The 19 km/h (10 kt) value below 1200 m is from the snippet [A]; text extraction mixed the lines.
- 14 CFR 25.237: at least 20 kt or 0.2 V_SR0, need not exceed 25 kt [A].
- A320 demonstrated value: not confirmed.
- Meaning [Y]: our 10 m/s case is 19 kt, at the planning limit at the surface. It is a real case, not an extreme one. With the log law it is 15–18 m/s on the approach. The TECHNICAL.md result (300 m offset, 10 m/s: 12 of 100) therefore matters.

### B2. Aircraft on approach

**B2.1 Speed.** Bands on V_AT: A < 91 kt, B 91–120, C 121–140, D 141–165, E 166–210. V_AT is the greater of 1.3 V_S0 or 1.23 V_S1g at maximum landing mass. https://skybrary.aero/articles/approach-speed-categorisation [D 6 Nov].

Eurocontrol performance database, indicative only, 6 Nov [D]:
- A320 V_AT 137 kt, category C: https://learningzone.eurocontrol.int/ilp/customs/ATCPFDB/details.aspx?ICAO=A320
- C-130H V_AT 130 kt, category C: same page, `ICAO=C130`.
- F-16 V_AT 150 kt, category D: same page, `ICAO=F16`.
- Its "approach" figures (IAS 150–250 kt, 1500 ft/min) describe an earlier phase [Y]. Do not use them for final.

T-6A about 105–110 kt on final [A: Navy table 110 kt, UK guide 105 kt]; flight manual not read. DC-8 simulator 135 kt [D 6 Nov, NASA CR-2019]. Our 70 m/s is 136 kt, so it stands for an A320 in calm air [Y].

Real speed is not constant. Asiana: 174 kt at 5 NM, 137 kt at 1.3 NM [D]. Tu-154M: 85 down to 79 m/s ground speed [Y].

**B2.2 Descent rate on 3°** [Y]: ROD = GS × tan 3°.

| Ground speed (kt) | Sink (m/s) | Sink (ft/min) |
|---:|---:|---:|
| 90 | 2.43 | 478 |
| 110 | 2.97 | 584 |
| 137 | 3.69 | 727 |
| 150 | 4.04 | 796 |
| 165 | 4.45 | 876 |

Stabilised limit ≤ 1000 ft/min, speed V_REF to V_REF + 20 kt, within 1 dot, stabilised by 1000 ft IMC: https://skybrary.aero/articles/stabilised-approach [D 6 Nov]; gates also [A] from FSF ALAR note 7.1.

**B2.3 Turn and path response.**
- Bank in instrument turns not above 30°: https://code7700.com/par.htm [D 6 Nov].
- Half standard rate (1.5°/s) on final for no-gyro PAR and ASR approaches [A, FAA JO 7110.65 and AIM snippets]. That equals 10.6° bank at 136 kt [Y]; 8.6° at 110 kt [Y].
- Airbus calls out bank above 7° on stabilised approach [A, FAA-hosted Airbus note]. AC 120-71A: generally not above 30° [A].
- Today's pilot lag (τ 3 s) on a 10° heading step starts at 3.3°/s. That is above half standard rate, so add a rate limit of 1.5°/s [Y].
- DC-8 simulation: attitude dynamics near 0.76 rad/s; phugoid damped lightly in closed loop [D 6 Nov, CR-2019; OCR noisy]. No source for a single "flight path time constant" was found. Keep τ 3–5 s as [Y] and vary it.

**B2.4 ILS tracking statistics.** Hall and Soares (US DOT Volpe), DASC 2008, https://rosap.ntl.bts.gov/view/dot/9095/dot_9095_DS1.pdf [D 6 Nov]. St Louis, Dec 2005–Feb 2006, 32,005 usable of 42,655 arrivals, large and heavy aircraft. Table 4: runway 30R in "hard" IMC.

Real ILS scatter shrinks in proportion to distance, from 20 m at 5 NM to 4 m at the threshold. Conversion to metres is [Y].

| Distance (NM) | Mean (ft) | Sigma (ft) | Sigma (m) |
|---:|---:|---:|---:|
| 5 | −9 | 66 | 20 |
| 4 | −7 | 50 | 15 |
| 3 | −1 | 44 | 13 |
| 2 | 4 | 30 | 9 |
| 1 | 2 | 20 | 6 |
| 0 | 1 | 14 | 4 |

- Beyond 5 NM the authors distrust their data (sensor error too large).
- Vertical: glide slope from track data was inconclusive. Laser heights at a point near the threshold: runway 12L mean 190.5 ft, σ 16.7 ft against 193 ft path; runway 12R mean 139.4 ft, σ 12.2 ft against 141 ft. So σ ≈ 4–5 m at about 150–190 ft.
- The paper quotes ICAO Doc 9613 values: about ±380 ft at 95 % coupled, ±760 ft manual, and finds real data far tighter.
- Against our result [Y]: 95 % error 25 m lateral, 9 m vertical at minimums means σ ≈ 13 m and 4.6 m. Real ILS σ near 0.6 NM is about 5 m lateral, 4–5 m vertical. Our vertical looks right; our lateral is 2–3 times worse, which is plausible for PAR-limited guidance, not an error.

Doc 9274 (CRM): manual is sold, not read. A paper says the CRM counts ILS system errors only [A]. **Its deviation tables are not confirmed.**

Radar talk-down tolerances from a real system [D 6 Nov, Smolensk report pp. 253, 257]: ±30′ vertical, ±2° lateral, "on path" within one third.

| Quantity | Smolensk system (deg) | Our cue (deg) |
|:---|---:|---:|
| Vertical limit | 0.50 | 0.70 |
| Lateral limit | 2.00 | 2.50 |
| On-path band, vertical | 0.17 | 0.11 |
| On-path band, lateral | 0.67 | 0.38 |

Annex 14 approach surface: table seen only in scrambled form [A]. **Dimensions not confirmed.**

### B3. Human pilot

- Crossover law: Y_p Y_c = ω_c e^(−τs) / s near crossover. Not for step inputs. Block range 1–10 rad/s, default 3; delay usually 0.1–0.2 s. https://www.mathworks.com/help/aeroblks/crossoverpilotmodel.html [D 6 Nov].
- Pilot adapts by plant: gain on K/s, lag on K, lead on K/s². Neuromuscular lag below 0.2 s. https://ocw.mit.edu/courses/16-400-human-factors-engineering-fall-2011/287583c524e3f1d9f6a34dd5c113d57d_MIT16_400F11_lec10.pdf [D 6 Nov].
- Those are fast single-axis tasks. Approach-specific data: Weir and McRuer, NASA CR-2019, 1972, https://ntrs.nasa.gov/api/citations/19720016437/downloads/19720016437.pdf [D 6 Nov; scanned, OCR noisy, so check numbers against the page]. Airline pilots, fixed-base DC-8, 135 kt, ILS from outer to middle marker:
  - Outer (glide slope) loop crossover **about 0.25–0.45 rad/s**, nearly the same for all pilots and tasks.
  - Inner (attitude) loop 0.33–1.4 rad/s in the multiloop task.
  - Single-loop attitude: 0.37 and 0.9 rad/s; 2.37 and 2.7 rad/s when told to push performance.
  - Effective delay near crossover 0.6–1 s, with a 3 s outlier on one loop. Display lag 0.3 s is included in some values.
  - Test inputs: vertical gust 5 ft/s rms, bandwidth 0.8 rad/s; beam bend 0.2 dot rms, 21 ft at 30,000 ft, bandwidth 0.3 rad/s.
- Bachelder et al. used a fixed 0.20 s pilot delay in a structural model [D 6 Nov, https://ntrs.nasa.gov/api/citations/20180001222/downloads/20180001222.pdf]. AGARD-AG-188 itself was not read (404 at STO, 403 at DTIC).

Meaning for us [Y]:
- Cue outer loop: 1/T = 0.05 rad/s with T = 20 s, six times slower than a pilot on a needle.
- Delay budget in our loop: reaction 1.5 s + pilot lag 3 s + zero-order hold on 5 s updates 2.5 s + filter about 3 s ≈ 10 s. Crossover must stay below about 0.16 rad/s to keep phase margin. So T = 20 s is sound. T near 6 s would not be.
- Proposed model: pure delay 1 s (range 0.6–3 s), heading rate limit, lag 3–5 s, plus small random error at the 0.2-dot level [Y]. No source covers a pilot following discrete 5 s voice steps. That remains a gap only a human trial can close.

### B4. Radar errors beyond white noise

**Accuracy baseline.** Annex 10 figures via ENRI: EL 6 m or 0.4 % of range + 10 % of offset; AZ 9 m or 0.6 % + 10 %; update within 1 s; X band 9080 MHz in an example spec; Pd above 90 % at RCS 2 m² as a high-performance requirement example. `R_par_enri_soumu.md`, re-read 6 Nov (read at source 4 Nov).

**Elevation multipath.**
- McAulay, MIT Lincoln Laboratory TN 1976-11, landing-monitor elevation sensor: https://www.ll.mit.edu/sites/default/files/publication/doc/optimum-elevation-angle-estimation-presence-mcaulay-tn-1976-11.pdf [D 6 Nov, OCR noisy]. Flat dry ground gives a reflection coefficient of −3 dB at 2.5° elevation. For small multipath ratio ρ, rms error is half peak error. Multipath phase is treated as random; the antenna's sidelobe suppression is the main defence. Design target: 1 mrad (0.057°) rms. It is an interferometer, not a PAR, so use it for order of size.
- Barton, "Low-Angle Radar Tracking", Proc. IEEE 1974: exists, not read [A]. A DTIC report describes multipath as a time-varying bias that falls as elevation rises [A, https://apps.dtic.mil/sti/tr/pdf/AD0781100.pdf]. The closed-form σ formula is **not confirmed**.

Two-ray geometry [Y]: phase φ = 4π h_a sin E / λ, with antenna height h_a and λ = 0.033 m. Lobe spacing λ/(2h_a) is 0.47°, 0.32°, 0.19° for h_a = 2, 3, 5 m. Key consequence: **on a constant-angle path, E hardly changes, so φ hardly changes.** An aircraft on path sees a near-constant bias, not an oscillation. The bias changes only when the aircraft moves off path, or near the runway where radar offset changes E.

Test on our alpha-beta filter (α 0.30, β 0.04, AR(1) noise, 400,000 steps) [Y]: once noise lasts 5 s or more the filter removes almost nothing.

| Noise correlation time (s) | Filtered/raw sigma |
|---:|---:|
| 0 | 0.47 |
| 2 | 0.77 |
| 5 | 0.93 |
| 10 | 1.00 |
| 20 | 1.02 |

So the gate will not catch multipath and the cue will steer to it. Suggested model [Y]: bias e(t) = A sin φ(t) + slow AR(1), with A = 0.03–0.1° (spans 1 mrad rms), growing as E falls. The value of A is an assumption until a measured PAR figure is found.

**Glint.** Search found only a qualitative view: worst during fades [A]. "RMS about 0.35 of target span" is from memory [Y]; **not confirmed**. For a 10–34 m aircraft that is 3–12 m, short correlation. Treat as a sensitivity case.

**Range-dependent SNR.** Standard radar equation: SNR ∝ R⁻⁴, thermal angle noise ∝ 1/√SNR, so linear error ∝ R³ [Y; textbook, not read]. Our 0.6 % of range is linear in R. Far out, SNR noise may grow faster. Suggested: add σ_snr(R) = σ₉ (R / 9 NM)³ with σ₉ chosen for SNR 13 dB at 9 NM [Y].

**Tracker.**
- Tracking index λ = σ_w T² / σ_v (σ_w process, σ_v measurement). α-β with gains from λ equals a steady Kalman filter. Conditions 0 < α < 1, 0 < β ≤ 2. https://en.wikipedia.org/wiki/Alpha_beta_filter [D 6 Nov]. Kalata 1984 confirmed as source by abstract [A].
- β = 2(2 − α) − 4√(1 − α) [A, conference paper snippet; same form as memory]. For α = 0.30 this gives β = 0.053; Benedict-Bordner gives 0.053 [Y]. Ours is 0.04, about 25 % lower.
- λ = β/√(1 − α) [Y, from memory] = 0.048 for ours. Implied manoeuvre σ_a = λσ_v/T²: 1.33 m/s² at 5 NM, 0.53 at 2 NM, 0.27 at 1 NM [Y].
- So fixed gains suit 5 NM but are too sluggish for the noise near the runway. Consider α scheduled with range, or a constant-velocity Kalman filter.
- Position noise ratio 0.47 from formula and simulation agree [Y].
- Kalman CV form: Q = q [[dt³/3, dt²/2], [dt²/2, dt]] [A, library docs]. A rule for q from peak acceleration exists (Blair) [A], not read. For reference, a half-standard turn at 70 m/s is 1.8 m/s² [Y].

**Plot loss.**
- Eurocontrol 1997 standard as tabulated by ICAO paper: PSR detection > 90 %, false reports < 20 per scan; SSR > 97 %. https://www.icao.int/sites/default/files/APAC/Meetings/2021/2021%20SURICG%206/4-Information%20Papers/IP04_ROK-AI.7-Practical-approach-to-assess-the-performance-of-surveillance-systems-r1.pdf [D 6 Nov]. En-route and terminal radar, not PAR. Standard itself not read.
- St Louis ASDE-X lost 25 % of tracks to quality problems: jumps, gaps of 6 s or more [D 6 Nov, Hall and Soares].
- Effect [Y]: with independent Pd = 0.90, three missed plots in a row (age above 2 s) has probability 0.001 per plot. That is about 16 % of 170 s approaches showing at least one false DELAYED. Our "0 false alarms in 100 runs" is true only at Pd = 1. Use a burst model too, because losses cluster.

---

## What we could not read

- **FAA JO 7110.65 chapters 5-10, 5-12, AIM 5-4:** faa.gov gave 403 to fetch. A 5 s PAR lost-communication interval appears in the JO 7110.65 search snippet and a Fort Hood chart snippet [A]. This supports `lost_after_s` but stays [A].
- **Built-in browser:** page opened, but every read returned "Policy check temporarily unavailable" (8 tries, 6 Nov). So nothing that needed it was read: FAA pages, NTSB docket, DTIC reports.
- One curl retry with a browser-like user agent was refused by the permission system. I did not try again. No bot check was passed.
- **MIL-F-8785C and MIL-HDBK-1797:** primary text not reached (host refused; DTIC 403). Dryden and shear numbers come through MathWorks.
- **ICAO Annex 10, Annex 14, Doc 9274, Doc 9817, Doc 8168:** paywalled or not found. Annex 14 surface numbers and ICAO shear classes are not confirmed, so they are left out of the table below.
- **McRuer AGARD-AG-188; McRuer and Jex 1967:** not reached. **Barton 1974; Skolnik; Bar-Shalom; Kalata 1984 full text; glint sources:** not reached.
- **Turkish 1951 DSB final report:** guessed URLs gave 404. Secondary snippets only: approach from above with a left radio altimeter fault [A]. Whether its tables hold glide slope deviation is unknown.
- **NTSB dockets DCA13MA120 and DCA06MA009 electronic tables; DASHlink host:** not reached.
- **MAK Smolensk report:** over the fetch size limit. **Smolensk Annex 1:** not read.
- **Monstein et al. paper, Olive and Basora preprint, ERAU ADS-B paper (Yoo), Airbus FCTM, A320 AFM, T-6 and C-130 flight manuals, OpenSky terms, Swiss AIP:** refused or not found.
- **Figshare sample rate:** inferred, not read.

Files actually fetched on 6 Nov: PDFs named above (fetch tool saved copies outside the project); `go_arounds_agg.csv.gz` (15 KB, scratchpad); `runways.csv` streamed through a filter; Parquet footers by range read. The two large files were **not** downloaded.

---

## Numbers to use

Sorted by model area. Tag is the weakest link for that value.

| Item | Value | Unit | Tag | Source |
|:---|:---|:---|:---|:---|
| **Turbulence** | | | | |
| W20 light / moderate / severe | 15 / 30 / 45 | kt | [D] | MathWorks Dryden |
| σ_w | 0.1 × W20 | same | [D] | MathWorks Dryden |
| σ_u = σ_v | σ_w / (0.177 + 0.000823h)^0.4 | h in ft | [D] | MathWorks Dryden |
| L_w | h | ft | [D] | MathWorks Dryden |
| L_u = L_v | h / (0.177 + 0.000823h)^1.2 | ft | [D] | MathWorks Dryden |
| σ_u, light, 300 ft | 1.09 | m/s | [Y] | Calculated |
| **Wind** | | | | |
| Shear law | W20 ln(h/z0) / ln(20/z0) | | [D] | MathWorks shear |
| z0, terminal phases | 0.15 | ft | [D] | MathWorks shear |
| Wind ratio 200 ft / 1000 ft | 1.47 / 1.80 | × W20 | [Y] | Calculated |
| Crosswind planning limit | 20 (13 if poor braking) | kt | [D] | Annex 14 text via Fiji CAA |
| **Aircraft** | | | | |
| V_AT A320 / C-130H / F-16 | 137 / 130 / 150 | kt | [D] | Eurocontrol, indicative |
| T-6A final | 105–110 | kt | [A] | Navy, UK guide snippets |
| Category C / D band | 121–140 / 141–165 | kt | [D] | SKYbrary |
| Sink, 3°, 137 kt | 727 | ft/min | [Y] | Calculated |
| Stabilised sink limit | 1000 | ft/min | [D] | SKYbrary; NTSB AAR-14/01 |
| Stabilised gate IMC | 1000 | ft | [D] | NTSB AAR-14/01 |
| Heading rate on final | 1.5 | deg/s | [A] | JO 7110.65, AIM snippets |
| Bank for that at 136 kt | 10.6 | deg | [Y] | Calculated |
| Bank callout | 7 | deg | [A] | Airbus note snippet |
| **ILS scatter** | | | | |
| Lateral σ at 5 / 3 / 1 / 0 NM | 20 / 13 / 6 / 4 | m | [D] | Hall and Soares 2008 |
| Vertical σ near threshold | 4–5 | m | [D] | Hall and Soares 2008 |
| GS full scale, 1 dot | ±0.7, 0.35 | deg | [D] | NTSB DCA06MA009 FDR report |
| Radar talk-down limits | ±0.5 vertical, ±2 lateral | deg | [D] | Smolensk report p. 257 |
| "On path" band | one third of limit | | [D] | Smolensk report p. 253 |
| Controller trend time | 5–6 | s | [D] | Smolensk report p. 267 |
| **Pilot** | | | | |
| Glide slope loop crossover | 0.25–0.45 | rad/s | [D] | NASA CR-2019 (OCR) |
| Attitude loop crossover | 0.33–1.4 | rad/s | [D] | NASA CR-2019 (OCR) |
| Effective delay, ILS task | 0.6–1 | s | [D] | NASA CR-2019 (OCR) |
| Delay, simple tracking | 0.1–0.2 | s | [D] | MathWorks crossover |
| Beam bend, ILS (for comparison) | 0.2 | dot rms | [D] | NASA CR-2019 (OCR) |
| Heading/sink lag | 3–5 | s | [Y] | Assumed, vary it |
| **Radar** | | | | |
| Reflection at 2.5° elevation | −3 | dB | [D] | MIT LL TN 1976-11 |
| Elevation error target, order of size | 1 | mrad rms | [D] | MIT LL TN 1976-11 |
| Multipath amplitude A | 0.03–0.1 | deg | [Y] | Assumed |
| Lobe spacing, h_a 3 m, 9.08 GHz | 0.32 | deg | [Y] | Two-ray geometry |
| Plot detection, PSR | above 90 | % | [D] | ICAO paper on Eurocontrol std |
| Plot detection, PAR example | above 90 at 2 m² | % | [D] | ENRI via R_par_enri_soumu |
| Kalman-matched β at α 0.30 | 0.053 | | [A] | Kalata relation snippet |
| Implied σ_a at 5 / 1 NM | 1.33 / 0.27 | m/s² | [Y] | Calculated |
| LOST interval, PAR final | 5 | s | [A] | JO 7110.65 snippet |
| **Replay data** | | | | |
| Zurich path angle 14 / 28 / 34 | 3.0 / 3.3 / 3.3 | deg | [D] | Zenodo 7148117 agg file |
| Smolensk path origin height | 14.8 ± 2.3 | m | [Y] | Fit to 7 stated points |
