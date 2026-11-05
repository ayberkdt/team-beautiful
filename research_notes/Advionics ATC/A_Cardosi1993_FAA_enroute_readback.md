# A_Cardosi1993_FAA_enroute_readback — FAA tape analysis of en-route pilot–controller voice communications

## Citation
Cardosi, K. M. (1993). "An Analysis of En Route Controller-Pilot Voice Communications." Report DOT/FAA/RD-93/11 (DOT-VNTSC-FAA-93-2), U.S. DOT Volpe National Transportation Systems Center, for FAA.
URL: https://rosap.ntl.bts.gov/view/dot/8659 (PDF dot_8659_DS1.pdf)

Date read: 2026-11-04. Read: Executive Summary in full (PDF text extracted with PyMuPDF). Body tables not read line by line. [D-ag]

## Data [D-ag]
47 h of voice tapes from 8 US ARTCCs (en route). 5032 controller-to-pilot transmissions: 3576 clearances and 1456 other (information requests, salutations...).

## Metric
Errors were counted in pilot readbacks (full or partial), as callsign discrepancies, as requests for repeat, and as controller failures to catch readback errors (hearback).

## Numbers [D-ag]
- Readback error: < 1% of full readbacks and 2% of partial readbacks. 27 readback errors in total.
- Complexity effect: readback error rate doubled from 0.7% to 1.4% going from 3 to 4 elements per clearance. Clearances with ≥ 5 elements are 4% of clearances but hold 26% of errors. The miscommunication rate (errors + requests for repeat) is 1–3% for 1–4 elements and 8% for ≥ 5 elements.
- Error type: frequency changes are 37% of readback errors; crossing restrictions 18%.
- Callsign: the full callsign was given in only 58% of erroneous readbacks, and none in 27%. 29 cases (0.8% of clearances) of a pilot answering with a different callsign; only 39% of those were corrected.
- Repeat requests: 51 cases (1.4% of clearances); from 1–2.5% for 1–4 elements up to almost 4% for ≥ 5 elements.
- Hearback: the controller did not notice the readback error in 3 cases, which is 11% of readback errors and < 0.1% of clearances. So en-route controllers caught ~89%, matching the "90%" cited by HAAWAII.

## Failure modes reported [D-ag]
- Long or complex clearances (≥ 5 elements).
- Frequency-change digits (37%) and crossing restrictions (18%).
- Missing or wrong callsign in readbacks. Callsign confusion is mostly left uncorrected (61%).
- The author's advice: pilots should ask for clarification rather than rely on the controller catching readback errors.

## Relevance to us [Y]
- This is the base rate for alert design: ~1% readback errors in en-route, and readback errors are dominated by frequencies and crossing restrictions. A cockpit display that shows frequency and constraint values visually targets the top 55% of readback errors.
- The callsign-confusion statistic (0.8% of clearances answered by the wrong aircraft, 61% uncorrected) supports an "is this for me?" callsign check on our display.
- Complex clearances (≥ 5 elements) are where a visual memory aid has the largest effect, with 8% miscommunication.
