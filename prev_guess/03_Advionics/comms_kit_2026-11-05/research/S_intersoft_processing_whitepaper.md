# S_intersoft_processing_whitepaper: "Advanced Processing Technologies" whitepaper (IE-CD-01571-001)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2024/11/IE-CD-01571-001-Advanced-Processing-Technologies-Whitepaper.pdf
- **Date read:** 2026-11-04. I loaded the PDF into memory with PyMuPDF and read the extracted text.

## What it says [D-ag]
- **VCC (Vertical Clutter Cancellation).** A patented algorithm that removes stable and unstable clutter.
  - Operational "Since 2013" on ASR and en-route systems.
  - For each range/azimuth cell, it virtually combines two beams into a **vertical suppression notch**.
  - Effect on windfarms: stationary clutter from the tower and nacelle drops "by 20-30 dB"; dynamic clutter from the blades drops "by up to 20 dB".
  - Gives sub-clutter visibility.
- **VCC².** Extends VCC to the transmit side.
  - Uses a power- and phase-controlled multi-beam transmitter, the **NGTX** (Next Generation Transmitter).
  - This gives "Elevation based power control".
- **Median filtering.** An image-processing median filter adapted to complex I/Q data.
  - Suppresses 4G/5G interference.
  - With (micro-)stagger, it cancels second-time-around returns.
- **SCC (Slow Clutter Cancellation).** Uses previous scans to subtract anomalous-propagation clutter, applied only in cells where anaprop is detected.
- **True 3D Height.** Measures PSR height without an SSR, using the phase and amplitude difference between two COSEC² fan beams.
  - The paper argues that relying on SSR height "can cause tragedy in case of transponder failure or bad intensions. Remember 9/11."
  - Height also enables RCS estimation, which separates aircraft from birds and drones.

## Relevance to us [Y]
- The sponsor explicitly frames **non-cooperative height measurement** as a safety backup for **transponder failure**.
- That framing maps directly onto a **lost-comm / lost-transponder approach** interpretation of the challenge.
- In the pitch, quote the "20-30 dB" windfarm figure only if it is relevant to our concept.
