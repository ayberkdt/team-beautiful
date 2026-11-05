# S_intersoft_res_page: SSR/IFF Environment Simulator (RES®) page

- **URL:** https://intersoft-electronics.com/cns-test-equipment/simulators-and-signal-generators/ssr-iff-environment-simulator/
- **Date read:** 2026-11-04 (WebFetch)

## What the page says [D-ag]
- **What it is:** the Radar Environment Simulator (RES®), an "Industry standard MSSR & IFF environment simulator". It is aimed at ANSPs, manufacturers and DoDs, and is part of the RASS® portfolio.
- **What it simulates:**
  - "Up to 2048" independent MSSR or Mode S targets, generated at RF level.
  - Modes: Mode S, Mode 1, Mode 2, Mode 3/A, Mode C, NSM, Mode 5, ADS-B and TIS-B.
  - Environment: FRUIT, reflectors, antenna behaviour, and non-standard antenna systems.
  - AIMS Mode 5 capabilities.
  - A moving platform with motion compensation.
- **Uses, as listed on the page:**
  - **Performance testing:** load capacity, sensitivity, Mode S performance, Mode 1/2 performance, resolution, accuracy, **probability of reply**, low PRF, high rotation speed, jammer frequencies.
  - **Acceptance testing:** FAT/SAT of SSR and Mode S radars.
  - **System testing:** box-level testing, and combined PSR + SSR + ADS-B evaluation.
  - **Regression testing:** before/after a settings, environment or firmware change, and channel-to-channel comparison.
- **Not on this page:** frequencies, power levels and accuracy specs. These are in the catalogue: Tx 1090 MHz ± 10 MHz and Rx 1030 MHz ± 10 kHz (see S_intersoft_rass_catalogue.md).
- **Customers:** none named.

## Relevance to us [Y]
- RES is how the sponsor proves that a secondary radar works: inject a known scenario, then compare the output.
- For any SSR/Mode S/ADS-B-based approach-guidance idea, our **validation plan should say "RES scenario injection with N targets, including reflectors and FRUIT, then compare against truth"**. That is their native language.
- The motion-compensated moving-platform capability fits naval or ship-deck approach ideas.
