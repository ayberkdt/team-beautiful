"""References for the 2026 final-challenge work on the canopy task (owned by one parallel session; add entries here only).

Every entry here was opened and read in the EASA canopy session on 4 Nov 2026; the evidence notes with page numbers are in
``02_EASA/research/`` (``R0_*`` read by the main session, ``R1_``–``R4_`` by subagents).
"""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    Reference("aaib_2024_g_miil", "Air Accidents Investigation Branch", 2024,
              "Accident Extra NG, G-MIIL, Upper Heyford, 2 April 2022 (AAIB-28120)",
              "AAIB Bulletin 4/2024, published 22 February 2024",
              url="https://assets.publishing.service.gov.uk/media/65d61630188d77001103883c/Extra-NG_G-MIIL_04-24.pdf",
              note="canopy and shoot-bolt latch description, handle gaps 70/60 mm, forces 136/60/90 N (pp. 8-10, 20); "
                   "cause, SR 2024-004/005, BFU dissent (pp. 25-28)"),
    Reference("nasa_fth_2002", "Stamatelatos, M.; Vesely, W.; Dugan, J.; Fragola, J.; Minarick, J.; Railsback, J.", 2002,
              "Fault Tree Handbook with Aerospace Applications",
              "NASA Office of Safety and Mission Assurance", edition="Version 1.1",
              url="https://extapps.ksc.nasa.gov/reliability/Documents/"
                  "Fault_Tree_Handbook_with_Aerospace_Applications_August_2002.pdf",
              note="rare-event approximation (sec. 7.1, App. B Eq. B.8); standby unavailability q ~ lambda*T/2 (Eq. 7.6); "
                   "importance measures FV, RRW, RAW, Birnbaum (pp. 90-91)"),
    Reference("easa_2025_ad_2025_0156", "European Union Aviation Safety Agency", 2025,
              "Airworthiness Directive 2025-0156: EXTRA NG, Placards and Markings / AFM Amendment",
              "EASA, issued 21 July 2025, effective 4 August 2025",
              url="https://ad.easa.europa.eu/ad/2025-0156",
              note="reason: in-flight canopy openings, in most cases a partially or improperly locked canopy (p. 2); "
                   "placards per SB-NG-1-24 + AFM rev. 16; no warning system required"),
    Reference("pkbwl_2024_sp_hmm", "State Commission on Aircraft Accidents Investigation (PKBWL)", 2024,
              "Final Report 2023-0061: Extra NG SP-HMM, canopy opened in flight, 4 August 2023",
              "PKBWL, Warsaw, dated 11 June 2024", url="https://www.pkbwl.gov.pl",
              note="pawls only partially engaged, not precluded by design (p. 6); passenger may have loosened locks; "
                   "ECO-NG-22-09/23-07, NG061+, AI-NG-02-23 (pp. 7-8)"),
    Reference("exida_2004_pf_namur", "Aschenbrenner, S. (exida.com GmbH)", 2004,
              "FMEDA and proven-in-use assessment, inductive NAMUR sensors, Report P+F 03/11-10 R015",
              "exida for Pepperl+Fuchs", edition="V1 R1.1, 25 July 2004",
              url="https://files.pepperl-fuchs.com/webcat/navi/productInfo/cert/cert0707.pdf",
              note="Table 2 p. 3: 15.4 FIT safe / 9.63 FIT dangerous; with fail-safe (line-monitoring) interface "
                   "24.9 / 0.09 FIT; SN 29500 basis"),
    Reference("dod_1995_mil_hdbk_217f", "U.S. Department of Defense", 1995,
              "MIL-HDBK-217F Notice 2, Reliability Prediction of Electronic Equipment", "DoD",
              edition="Notice 2, 28 February 1995",
              url="https://www.dinfo.unifi.it/upload/sub/laboratori/labmaq/labme_1/mil_hdbk_217f_2.pdf",
              note="sec. 14.1 switches: lambda_b sensitive 0.49, limit 4.3, reed 0.0010 per 1e6 h; pi_E GB 1, AIF 18 "
                   "(read by subagent R4 from page images)"),
    Reference("bliss_gilson_deaton_1995", "Bliss, J. P.; Gilson, R. D.; Deaton, J. E.", 1995,
              "Human probability matching behaviour in response to alarms of varying reliability",
              "Ergonomics 38(11), 2300-2312", doi="10.1080/00140139508925269",
              note="abstract only (subagent R4): ~90 % of participants matched response rate to alarm reliability"),
    Reference("wickens_dixon_2007", "Wickens, C. D.; Dixon, S. R.", 2007,
              "The benefits of imperfect diagnostic automation: a synthesis of the literature",
              "Theoretical Issues in Ergonomics Science 8(3), 201-212", doi="10.1080/14639220500370105",
              note="abstract only (subagent R4): below ~0.70 reliability automation is worse than none"),
    Reference("faa_2011_ac23_1309_1e", "Federal Aviation Administration", 2011,
              "AC 23.1309-1E, System Safety Analysis and Assessment for Part 23 Airplanes", "FAA",
              url="https://www.faa.gov/regulations_policies/advisory_circulars/",
              note="Fig. 2 p. 23 Class I probability ceilings per FH; sec. 11.b no misleading safe indication "
                   "(read by subagent R4)"),
    Reference("swain_guttmann_1983", "Swain, A. D.; Guttmann, H. E.", 1983,
              "Handbook of Human Reliability Analysis with Emphasis on Nuclear Power Plant Applications (NUREG/CR-1278)",
              "U.S. Nuclear Regulatory Commission", edition="Final report, August 1983",
              url="https://www.osti.gov/servlets/purl/5752058",
              note="Table 20-7 (from 15-3): omission HEP per procedure item 0.001-0.01, 0.05 if procedure not used"),
)
