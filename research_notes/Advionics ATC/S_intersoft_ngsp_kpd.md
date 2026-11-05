# S_intersoft_ngsp_kpd: "NGSP® Key Performance Differentiators" (IE-CD-01366-001)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2023/09/IE-CD-01366-001-NGSP-Key-Performance-Differentiators.pdf (linked from the Mid-Life Upgrades page)
- **Date read:** 2026-11-04. I loaded the PDF into memory with PyMuPDF and read the extracted text.

## What it says [D-ag]
- **Role.** NGSP® is "the brain in all new Primary Surveillance Radar systems Intersoft delivers". It is also used for upgrades of 2D and 3D, short- and long-range radars. It can be fitted to PSR-only systems and to combined PSR/SSR(IFF) systems, both civil and military.
- **Features.** The document restates the NGSP intro:
  - concurrent receivers
  - "typ. dual band 4Mhz LFM"
  - a 16-filter MTD with reduced "scalloping losses"
  - super-resolution by beam fitting
  - SCC (anomalous-propagation clutter removal)
  - classification based on RCS and height
- **VCC.** VCC "combines two beams to create a virtual receive beam with a suppression notch which is variable in elevation", which puts a null at the clutter's elevation.
- **ECCM.** A slow-time median filter plus frequency agility, together with a jammer strobe.
- **RF pulse repair.** The title is visible, but the text was cut off in the extraction.

## Relevance to us [Y]
- The jury's PSR engineers know elevation-notch beamforming and two-beam height finding well.
- An approach concept that uses **two receive beams to estimate elevation angle**, as their True 3D Height does, would speak their language.
