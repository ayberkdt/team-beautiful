# R1 — CAA UK safety material and EASA SIBs on canopy/door unlatching

- read by: subagent R1
- date read: 2026-11-04
- Tags: [D-ag] = read from source; [Y] = inference.

## Sources
| File (D:\tmp_ideathon\easa\dl\reg\) | URL | sha256(16) |
|---|---|---|
| caa_ssl.html: CAA Safety Sense leaflet index | https://www.caa.co.uk/general-aviation/safety-topics/safety-sense-leaflets/ | — |
| caa_ssl\caa9396_safetysense_aerobatics-v5.pdf: SSL "Aerobatics in Light Aircraft", CAA July 2023 | https://www.caa.co.uk/media/jkxlnrvv/caa9396_safetysense_aerobatics-v5.pdf | a8cf3b51c14d22f5 |
| caa_ssl\caa8230_safetysense_31_distraction_aw9.pdf: SSL 31 Distraction, May 2023 | https://www.caa.co.uk/media/apcbiav3/caa8230_safetysense_31_distraction_aw9.pdf | 80bf13ce0282d822 |
| caa_ssl\20130121ssl01.pdf: SSL 1 Good Airmanship | https://www.caa.co.uk/media/do4h50i0/20130121ssl01.pdf | 569bb444afe1b52e |
| caa_ssl\safety-sense-ss002-care-of-passengers-version-8.pdf: SSL 2 | https://www.caa.co.uk/media/ovwcto24/safety-sense-ss002-care-of-passengers-version-8.pdf | e0a3e7ee7767552a |
| caa_14181.pdf: CAA FACTOR F8/2011 (Magni M24C G-CGTI) | https://caa.co.uk/publication/download/14181 | 594dd6770eba21c5 |
| caa_19421.pdf: CAA Mandatory Permit Directive 2022-003 (Europa) | https://www.caa.co.uk/publication/download/19421 | 3906c33006f35414 |
| archive_sib.html: EASA SIB/SD archive list (975 rows) | https://www.easa.europa.eu/en/domains/aircraft-products/airworthiness-directives-ad/archive-safety-information-bulletin-and-safety-directives | — |

## CAA Safety Sense leaflets [D-ag]
- The index lists SSLs 1, 2, 3, 5, 6, 9, 10, 12–17, 20–25, 28–31 and 33–36. **No leaflet is dedicated to canopy or door opening in flight.**
- Canopy and door content appears only in passing:
  - **SSL Aerobatics** (July 2023), PDF p.14: the HASELL check includes "Security – harnesses fastened, canopy/doors secure and no loose articles."
  - **SSL 31 Distraction** (May 2023), PDF p.8: gives "the door opening in flight" as a distraction example. Trying to close it at low level "could have fatal consequences". Advises "Always fly the aircraft."
  - **SSL 1 Good Airmanship**, PDF p.9: brief passengers on doors and exits; "Personally secure doors and luggage hatches."
  - **SSL 2 Care of Passengers**: brief on how to open doors and canopies for evacuation.
- SSL 30 Loss of Control: no canopy or door hits.

## CAA regulatory precedents [D-ag]
- **CAA FACTOR F8/2011** (published 18 Nov 2011):
  - Event: Magni M24C G-CGTI, 28 Apr 2011. The gull-wing door "appeared to be closed but the latching mechanism had not locked".
  - AAIB **SR 2011-082**: amend **BCAR Section T** "to minimise the likelihood of an aircraft door inadvertently opening in flight".
  - CAA accepted and planned the change by March 2013. CAA status: Open as of that FACTOR.
  - Whether BCAR T was actually amended: NOT VERIFIED.
- **CAA MPD 2022-003** (issued 03 Feb 2022, effective 17 Feb 2022), Europa aircraft, all models and serial numbers:
  - Reason (p.2): **eight** inadvertent canopy-door openings in the UK since 2003, including G-FLOR on 23 Jun 2021 (door detached and hit the tailplane).
  - Mechanism: the door "appears to be closed and locked but has only engaged on the forward" shoot-bolt guide.
  - The pilot cannot easily check the misalignment from the seat.
  - Fix: LAA mod **SM15833**, an aerodynamic "stop" that baulks the shoot bolt so the lever cannot reach "locked" unless the door is correctly closed. This is a mechanical interlock that makes the lock indication truthful.
  - Compliance: within 5 FH or the next Permit revalidation. Refs LAA/AWA/21/08 and MOD/247/012.
  - [Y] Strong analogue for the Extra NG (shoot bolt and roller partial engagement). It shows the UK regulator accepting a *retrofit that ties the indicated lock state to the real engagement*.

## EASA SIBs [D-ag, archive list]
- I searched the archive list for canopy, door and latch. Hits:
  - SIB 2023-07 (B757 main cargo door opening in flight)
  - SAIB-2025-02 (B757 cargo door)
  - SAFO24001 (737-9 door plug)
  - SIB 2019-02 (explosive door openings)
  - CE-10-16 (Liberty XL-2 doors)
  - CE-13-09 (Cessna 425 cargo door)
  - Various transport-category items, and SIB 2007-51 (parachute canopies, not aircraft)
- **No EASA SIB on GA or aerobatic canopy unlatching, and none on the Extra NG.**
- Related item seen in ASRR 2026: SIB-2019-07R1 on sailplane rigging, not canopies.

## Other national material found but NOT LOADED
- CASA AWB "Inadvertent door opening in flight": https://www.casa.gov.au/index.php/aircraft/airworthiness/airworthiness-bulletins/inadvertent-door-opening-flight. Timeouts via curl and WebFetch. NOT READ.
- ATSB safety issue AO-2014-164-SI-01, "Potential adverse effects of a tip-up canopy opening in-flight": https://www.atsb.gov.au/safety-issues/AO-2014-164-SI-01. Timeout. NOT READ.
- Dutch Safety Board, Aerospool response on canopy-opening recommendations (onderzoeksraad.nl): seen in search, NOT READ.
- AAIB Sling 4 G-LDSA (12/17), Flight Design CTSW G-CFFJ (03/25), Spitfire IXT G-BMSB (11/24): seen in search results only, NOT READ. The search summaries say the lever could be "partly locked without being fully in its over-centre position" (G-LDSA). This is unverified until read.
- Swiss SUST HB-3214 (glider canopy opened during sideslip, fuselage deformation): seen in search only, NOT READ.

## NOT FOUND / NOT VERIFIED
- A CAA safety notice (SN) or Safety Sense leaflet specifically on canopies: none found in the index.
- Whether BCAR Section T now contains a door-security requirement post-2013.
- An EASA GA safety-promotion leaflet on canopy locking: none found.
