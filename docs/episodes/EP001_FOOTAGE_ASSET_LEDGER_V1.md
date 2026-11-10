# EP001 — Candidate Footage Asset Ledger (v1)

**Status:** Source pages and download links identified. Files have NOT yet been downloaded or technically inspected. These are candidates, not final edit approvals.

## Candidate assets

| Asset ID | Scene use | Source page | Direct HD download | Credit shown on source page | Published size / resolution clue | Verification status |
|---|---|---|---|---|---|---|
| FB-EP001-A01 | Chapter 3 — marine snow | https://oceanexplorer.noaa.gov/multimedia/explorations-19gulfofalaska-logs-aug1-media-video-marine-snow/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2013/10/marine-snow-1920x1080-1.mp4 | NOAA/UAF/Oceaneering | HD, 6.9 MB; filename indicates 1920×1080 | Link resolved from page; dimensions/codec/duration still require ffprobe |
| FB-EP001-A02 | Chapter 3 — deep-sea animal and marine snow | https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2304-gallery-media-dive08-fish/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2023/07/dive08-fish-1280x720-1.mp4 | NOAA Ocean Exploration, Seascape Alaska | HD, 31.7 MB; filename indicates 1280×720; animal identified as giant grenadier (*Albatrossia pectoralis*) at 1,433 m | Link resolved from page; dimensions/codec/duration still require ffprobe |
| FB-EP001-A03 | Chapter 5 — hydrothermal vent reveal | https://oceanexplorer.noaa.gov/multimedia/edu-themes-vents-and-volcanoes-media-video-multimedia-hydrothermal/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2019/06/0501-hydrothermal-vents-1920x1080-1.mp4 | NOAA Ocean Exploration, 2016 Deepwater Exploration of the Marianas | HD, 72.1 MB; filename indicates 1920×1080 | Link resolved from page; dimensions/codec/duration still require ffprobe |

| FB-EP001-A04 | Chapter 4 — bioluminescence | https://oceanexplorer.noaa.gov/video-series/deep-sea-dialogues/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2021/10/bioluminescence-1920x1080-1.mp4 | Video courtesy of NOAA Ocean Exploration | HD, 584.3 MB; linked HD download | Exact download URL confirmed from NOAA page; file not yet downloaded/inspected |
| FB-EP001-A05 | Chapter 5 — hydrothermal vent expert context | https://oceanexplorer.noaa.gov/video-series/deep-sea-dialogues/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2025/04/hydrothermal-vents-1920x1080-1.mp4 | Video courtesy of NOAA Ocean Exploration | HD, 335.0 MB; linked HD download | Exact download URL confirmed from NOAA page; file not yet downloaded/inspected |
| FB-EP001-A06 | Chapter 6 — ROV and underwater exploration context | https://oceanexplorer.noaa.gov/video-series/deep-sea-dialogues/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2020/10/robots-1920x1080-1.mp4 | Video courtesy of NOAA Ocean Exploration | HD, 346.3 MB; linked HD download | Exact download URL confirmed from NOAA page; file not yet downloaded/inspected |


## Rights and attribution gate

NOAA Ocean Exploration's media guidance says all video in its Ocean Exploration Video Portal is public domain and should be credited to NOAA Ocean Exploration. The three candidates above are linked from NOAA Ocean Exploration multimedia pages, but this ledger does not silently assume that every third-party contributor's material or every site-hosted asset has identical terms. Before final export, verify the reuse basis for each exact asset and preserve the credit exactly as supplied by its source page.

Reference: https://oceanexplorer.noaa.gov/about/media-kit/

## Acquisition / QC checklist

- [ ] Download each candidate without recompression.
- [ ] Record actual byte size and SHA-256 checksum.
- [ ] Run ffprobe and record exact width, height, frame rate, codec, duration, and pixel format.
- [ ] Watch the complete clip; select only relevant time ranges.
- [ ] Confirm the visual content matches the narration and species/location metadata.
- [ ] Confirm credit and reuse terms for the exact asset.
- [ ] Do not upscale and describe it as native 4K.
- [ ] Keep any clip that fails a check out of the edit.

## Current production implication

These three clips are useful verified starting points for marine snow, a deep-sea fish, and a hydrothermal vent. They do not yet provide enough visual variety for an 8–10 minute documentary. Additional footage is still needed for surface descent, twilight-zone animals, bioluminescence, ROV operations, and broad seafloor establishing shots.
