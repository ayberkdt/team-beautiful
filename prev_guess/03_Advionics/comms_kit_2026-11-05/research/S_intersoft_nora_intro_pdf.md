# S_intersoft_nora_intro_pdf: "Introduction to NORA®" (IE-CD-01525-002)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2025/07/IE-CD-01525-002-Introduction-to-NORA-single-page.pdf
- **Date read:** 2026-11-04. WebFetch saved the PDF; I read it with pdftotext.

## What it says [D-ag]
- **Positioning:** non-rotating arrays (AESAs) were traditionally costly military systems. Intersoft develops them for civil and military markets at a price competitive with mechanically rotating antennas. NORA is part of the modular ASR-M® concept and can be the "final phase" of a radar upgrade, replacing the PSR transmitter and antenna.
- **Bands and roles:** S-band primary, L-band SSR/IFF (cooperative) and L-band primary.
  - "NORA® = Primary Radar L & S Band Non-Rotating Array antenna for land-based applications".
  - "L-IESA® = Secondary Radar L-Band … Scanning Array antenna for naval IFF applications".
- **Typical scalability:**
  - "16-64+ 'Antenna front end elements'";
  - "3-12m diameter";
  - "Transmit power from 2kW to 32kW per beam";
  - azimuth monopulse for accuracy (both PSR and SSR).
- **Why civil budgets can afford it:** low-cost microwave transmit/receive modules from the mobile base-station market.
- **Power:** an integrated distributed TX/RX amplifier removes feeder losses, so less total transmitter power is needed.
- **Scanning:** the array typically uses "90° of the full array" for one set of elevation beams.
  - The beam is scanned "±22.5°" about boresight; flat panels typically scan ">±60°".
  - The quarter array is then stepped by one element.
  - In non-continuous mode the beam can be pointed instantly to a new boresight.
- **Elevation beams:** two or more. Transmit can be on the low beam only, or on low and high beams.
  - Enables VCC, VCC2 and 3D primary height extraction.
- **Horizontal scan regimes:** continuous rotation; rotation with "confirmation" look-backs; **sector scanning**.
  - Sector scanning can focus on "runway areas" or raise the update rate on a "highly maneuvering aircraft".
- **Simultaneous beams:** a second surveillance beam can double dwell time or halve the update interval.
  - Typical update intervals are quoted as "4/5/10/12 seconds".
  - The halved examples are quoted as "2/2.5/15/16 seconds". This looks like a typo in the source, since half of 10/12 is 5/6.
  - Alternatively, a tracking beam gives more time on target for small, slow or manoeuvring targets.
- **Benefits list:** similar capital cost; lower lifecycle cost; light weight; no single point of failure; lower power; customizable beams; monopulse azimuth accuracy.
- **SSR integration:** NORA can be used "with virtually any standard SSR/IFF interrogator".

## Relevance to us [Y]
- This is the strongest sponsor-native hook for a **radar-supported approach concept**: a NORA L-band SSR ring or S-band PSR at the airfield, with a sector-scan or tracking beam on final approach.
- A tracking beam could cut the update interval from 4–5 s (conventional ASR) to well below 1 s on the approaching aircraft. That estimate is mine, not a published number.
- Quote the published numbers exactly: 3–12 m diameter, 16–64+ elements, 2–32 kW per beam, ±22.5° fine scan.
