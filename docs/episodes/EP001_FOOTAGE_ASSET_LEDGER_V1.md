# EP001 — Candidate Footage Asset Ledger (v1)

**Status:** Three NOAA source clips downloaded from the listed direct links and passed automated technical QC on 2026-11-10. Representative frames were visually sampled. Full-clip editorial review and exact reuse/credit confirmation remain open; these are not yet final edit approvals.

## Candidate assets

| Asset ID | Scene use | Source page | Direct HD download | Credit shown on source page | Published size / resolution clue | Verification status |
|---|---|---|---|---|---|---|
| FB-EP001-A01 | Chapter 3 — marine snow | https://oceanexplorer.noaa.gov/multimedia/explorations-19gulfofalaska-logs-aug1-media-video-marine-snow/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2013/10/marine-snow-1920x1080-1.mp4 | NOAA/UAF/Oceaneering | 6.9 MiB | Downloaded; H.264, 1280×720, 30 fps, 9.700 s; sampled frame shows suspended particles; SHA-256 `47a7b32490ef2a84780779946c5fe31a38368d9d3fa882782a5842182eb13551` |
| FB-EP001-A02 | Chapter 3 — deep-sea animal and marine snow | https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2304-gallery-media-dive08-fish/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2023/07/dive08-fish-1280x720-1.mp4 | NOAA Ocean Exploration, Seascape Alaska | 31.7 MiB | Downloaded; H.264, 1280×720, 29.97 fps, 60.394 s; source slate identifies giant grenadier (*Albatrossia pectoralis*) at 1,433 m; SHA-256 `f8afd0055c74b8893c1fd62f8cdd9619a25df66e42d80137c120e9ba7ff41778` |
| FB-EP001-A03 | Chapter 5 — hydrothermal vent reveal | https://oceanexplorer.noaa.gov/multimedia/edu-themes-vents-and-volcanoes-media-video-multimedia-hydrothermal/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2019/06/0501-hydrothermal-vents-1920x1080-1.mp4 | NOAA Ocean Exploration, 2016 Deepwater Exploration of the Marianas | 72.1 MiB | Downloaded; H.264, 1920×1080, 29.97 fps, 65.707 s; sampled frame shows vent-associated seafloor fauna; SHA-256 `f99f735f520b93706c029f4b5f24df99d07bc9ae07d3afe527dd587375b7a438` |

| FB-EP001-A04 | Chapter 4 — bioluminescence | https://oceanexplorer.noaa.gov/video-series/deep-sea-dialogues/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2021/10/bioluminescence-1920x1080-1.mp4 | Video courtesy of NOAA Ocean Exploration | HD, 584.3 MB; linked HD download | Exact download URL confirmed from NOAA page; file not yet downloaded/inspected |
| FB-EP001-A05 | Chapter 5 — hydrothermal vent expert context | https://oceanexplorer.noaa.gov/video-series/deep-sea-dialogues/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2025/04/hydrothermal-vents-1920x1080-1.mp4 | Video courtesy of NOAA Ocean Exploration | HD, 335.0 MB; linked HD download | Exact download URL confirmed from NOAA page; file not yet downloaded/inspected |
| FB-EP001-A06 | Chapter 6 — ROV and underwater exploration context | https://oceanexplorer.noaa.gov/video-series/deep-sea-dialogues/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2020/10/robots-1920x1080-1.mp4 | Video courtesy of NOAA Ocean Exploration | HD, 346.3 MB; linked HD download | Exact download URL confirmed from NOAA page; file not yet downloaded/inspected |


## Rights and attribution gate

NOAA Ocean Exploration's media guidance says all video in its Ocean Exploration Video Portal is public domain and should be credited to NOAA Ocean Exploration. The three candidates above are linked from NOAA Ocean Exploration multimedia pages, but this ledger does not silently assume that every third-party contributor's material or every site-hosted asset has identical terms. Before final export, verify the reuse basis for each exact asset and preserve the credit exactly as supplied by its source page.

Reference: https://oceanexplorer.noaa.gov/about/media-kit/

## Acquisition / QC checklist

- [x] Download A01–A03 without recompression.
- [x] Record actual byte size and SHA-256 checksum for A01–A03.
- [x] Run ffprobe and record exact width, height, frame rate, codec, duration, and pixel format for A01–A03.
- [ ] Watch the complete clips; select only relevant time ranges.
- [x] Sample representative frames; confirm A01 particle field, A02 giant grenadier source slate/animal, and A03 vent-associated fauna.
- [ ] Confirm credit and reuse terms for each exact asset before final export.
- [ ] Do not upscale and describe it as native 4K.
- [ ] Keep any clip that fails a check out of the edit.

## Current production implication

These three clips are useful verified starting points for marine snow, a deep-sea fish, and a hydrothermal vent. They do not yet provide enough visual variety for an 8–10 minute documentary. Additional footage is still needed for surface descent, twilight-zone animals, bioluminescence, ROV operations, and broad seafloor establishing shots.


## Verified acquisition run — 2026-11-10

- GitHub Actions workflow: [Fact Bites EP001 — NOAA Asset Intake & QC](https://github.com/shanqiti601/free-video-generator/actions/runs/42840298045)
- Run ID: `42840298045`; commit: `05bff9deeac80c5eb08d1072267e4efe5e777283`; run and job conclusion: success.
- Artifact: `Fact-Bites-EP001-NOAA-Asset-QC` (113,625,042 bytes), retained until 2026-11-17T15:10:45Z.
- Archive contains the three original MP4 files, ffprobe report, SHA-256 manifest, and representative JPG frames.
- Archive was downloaded and inspected locally. Total video duration is approximately 135.8 seconds. This is a starter library only, not enough for the full episode.
- A01 is 720p despite the source filename containing 1920x1080; trust measured media properties, not filename clues.
- A03's sampled first frame is an NOAA title slate; the sampled mid-clip frame shows vent-associated animals. Edit must trim title slate where appropriate and inspect the entire clip.
- The asset package is technical-QC passed, not yet editorially or rights-cleared for final publication.
