# EP001 — Candidate Footage Asset Ledger (v1)

**Status:** Five NOAA source clips downloaded from the listed direct links and passed automated technical QC on 2026-11-10. Representative frames were visually sampled; mid-clip frames for A04 and A05 were also inspected. Full-clip editorial review and final per-asset credit/reuse confirmation remain open; these are not yet final edit approvals.

## Candidate assets

| Asset ID | Scene use | Source page | Direct HD download | Credit shown on source page | Published size / resolution clue | Verification status |
|---|---|---|---|---|---|---|
| FB-EP001-A01 | Chapter 3 — marine snow | https://oceanexplorer.noaa.gov/multimedia/explorations-19gulfofalaska-logs-aug1-media-video-marine-snow/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2013/10/marine-snow-1920x1080-1.mp4 | NOAA/UAF/Oceaneering | 6.9 MiB | Downloaded; H.264, 1280×720, 30 fps, 9.700 s; sampled frame shows suspended particles; SHA-256 `47a7b32490ef2a84780779946c5fe31a38368d9d3fa882782a5842182eb13551` |
| FB-EP001-A02 | Chapter 3 — deep-sea animal and marine snow | https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2304-gallery-media-dive08-fish/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2023/07/dive08-fish-1280x720-1.mp4 | NOAA Ocean Exploration, Seascape Alaska | 31.7 MiB | Downloaded; H.264, 1280×720, 29.97 fps, 60.394 s; source slate identifies giant grenadier (*Albatrossia pectoralis*) at 1,433 m; SHA-256 `f8afd0055c74b8893c1fd62f8cdd9619a25df66e42d80137c120e9ba7ff41778` |
| FB-EP001-A03 | Chapter 5 — hydrothermal vent reveal | https://oceanexplorer.noaa.gov/multimedia/edu-themes-vents-and-volcanoes-media-video-multimedia-hydrothermal/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2019/06/0501-hydrothermal-vents-1920x1080-1.mp4 | NOAA Ocean Exploration, 2016 Deepwater Exploration of the Marianas | 72.1 MiB | Downloaded; H.264, 1920×1080, 29.97 fps, 65.707 s; sampled frame shows vent-associated seafloor fauna; SHA-256 `f99f735f520b93706c029f4b5f24df99d07bc9ae07d3afe527dd587375b7a438` |
| FB-EP001-A04 | Chapter 4 — deep-sea sponge / seafloor life | https://oceanexplorer.noaa.gov/multimedia/largest-sponge-ever-found/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2026/10/largest-sponge-ever-found.mp4 | NOAA Ocean Exploration, 2015 Hohonu Moana | 60.1 MiB; HD download | Downloaded; H.264, 1920×1080, 29.97 fps, 121.488 s; mid-clip frame confirms large sponge at 2,117 m; initial sample contains a title slate; SHA-256 `5a4c71fb9571a4a1e5c7a5bf9be4bc162af8fc49afa7efc5f3a3e062decd2b84` |
| FB-EP001-A05 | Chapter 4 — deep-sea octopus / color adaptation | https://oceanexplorer.noaa.gov/multimedia/okeanos-explorations-seascape-alaska-ex2306-gallery-media-dive08-changingcolors/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2023/10/dive08-changingColors-1280x720-1.mp4 | NOAA Ocean Exploration, Seascape Alaska | 60.7 MiB; HD download | Downloaded; H.264, 1280×720, 29.97 fps, 59.459 s; mid-clip frame confirms octopus close-up; initial sample contains a title card; SHA-256 `c970cda14b181ded733ad3e9f5f74d13867b2e3ac68a185d663d80f94fa0792d` |
| FB-EP001-A06 | Chapter 4 — bioluminescence science/visual candidate | https://oceanexplorer.noaa.gov/multimedia/edu-resources-dsd-bioluminescence/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2021/10/bioluminescence-640x360-1.mp4 | NOAA Ocean Exploration | SD, 77.5 MB per source page; download step completed, technical QC pending in run 42844464898 |
| FB-EP001-A07 | Chapter 7 — ROV exploration candidate | https://oceanexplorer.noaa.gov/technology/subs-deep-discoverer/ | https://oceanexplorer.noaa.gov/wp-content/uploads/2018/09/d2-1280x720-2.mp4 | NOAA Ocean Exploration, Gulf of Mexico 2017 | 119.2 MB per source page; download step completed, technical QC pending in run 42844464898 |


## Rights and attribution gate

NOAA Ocean Exploration's media guidance says all video in its Ocean Exploration Video Portal is public domain and should be credited to NOAA Ocean Exploration. The five candidates above are linked from NOAA Ocean Exploration multimedia pages, but this ledger does not silently assume that every third-party contributor's material or every site-hosted asset has identical terms. Before final export, verify the reuse basis for each exact asset and preserve the credit exactly as supplied by its source page.

Reference: https://oceanexplorer.noaa.gov/about/media-kit/

## Acquisition / QC checklist

- [x] Download A01–A05 without recompression.
- [x] Record actual byte size and SHA-256 checksum for A01–A05.
- [x] Run ffprobe and record exact width, height, frame rate, codec, duration, and pixel format for A01–A05.
- [ ] Watch the complete clips; select only relevant time ranges.
- [x] Sample representative frames; confirm A01 particle field, A02 giant grenadier source slate/animal, A03 vent-associated fauna, A04 large sponge, and A05 octopus close-up. Mid-clip samples for A04/A05 avoid their opening title slates.
- [ ] Confirm credit and reuse terms for each exact asset before final export.
- [ ] Do not upscale and describe it as native 4K.
- [ ] Keep any clip that fails a check out of the edit.

## Current production implication

These five clips now provide verified technical candidates for marine snow, a giant grenadier, a hydrothermal vent, a large deep-sea sponge, and an octopus. Their combined measured duration is approximately 316.75 seconds (5 minutes 17 seconds), still short of the planned 8–10 minute episode and lacking several transitions and visual categories. Additional footage is still needed for surface descent, twilight-zone animals, bioluminescence, ROV operations, and broad seafloor establishing shots.


## Verified acquisition run — 2026-11-10

- GitHub Actions workflow: [Fact Bites EP001 — NOAA Asset Intake & QC](https://github.com/shanqiti601/free-video-generator/actions/runs/42840298045)
- Run ID: `42840298045`; commit: `05bff9deeac80c5eb08d1072267e4efe5e777283`; run and job conclusion: success.
- Artifact: `Fact-Bites-EP001-NOAA-Asset-QC` (113,625,042 bytes), retained until 2026-11-17T15:10:45Z.
- Archive contains the three original MP4 files, ffprobe report, SHA-256 manifest, and representative JPG frames.
- Archive was downloaded and inspected locally. Total video duration is approximately 135.8 seconds. This is a starter library only, not enough for the full episode.
- A01 is 720p despite the source filename containing 1920x1080; trust measured media properties, not filename clues.
- A03's sampled first frame is an NOAA title slate; the sampled mid-clip frame shows vent-associated animals. Edit must trim title slate where appropriate and inspect the entire clip.
- The asset package is technical-QC passed, not yet editorially or rights-cleared for final publication.


## Expanded verified acquisition run — 2026-11-10

- Workflow: [Fact Bites EP001 — NOAA Asset Intake & QC](https://github.com/shanqiti601/free-video-generator/actions/runs/42843773071)
- Run ID: `42843773071`; commit: `4704f1c598143587c0837eaa195729b65e0c975e`; run and job conclusion: success.
- All five download, ffprobe/frame extraction, and artifact upload steps completed successfully.
- Artifact: `Fact-Bites-EP001-NOAA-Asset-QC` (240,219,914 bytes), retained until 2026-11-17T15:23:51Z.
- Artifact contains five original MP4 files, ffprobe report, SHA-256 manifest, and representative JPG frames.
- New A04/A05 mid-clip frames were separately extracted and visually inspected: A04 shows the large sponge structure; A05 shows an octopus close-up. Their initial 3-second samples are title overlays, so the editor must use clean mid-clip ranges after full review.
- Measured combined duration across A01–A05: approximately 316.75 seconds. A04 is native 1920×1080; A05 is 1280×720. No 4K footage has been acquired.
- Technical QC passed does not mean the complete clips have been watched or final editorial/rights clearance has been granted.


## Pending candidate intake — 2026-11-10

- Added A06 (NOAA Deep-Sea Dialogues: Bioluminescence, SD 640×360 download) and A07 (NOAA Deep Discoverer ROV, 1280×720 download) to the intake workflow. NOAA source pages state their credits and published download sizes.
- Workflow run [42844464898](https://github.com/shanqiti601/free-video-generator/actions/runs/42844464898) completed its download step successfully; ffprobe and representative-frame extraction are still running. Do not count A06/A07 as QC-passed or picture-approved until that run finishes and the frames/metadata are inspected.
- A06 is standard-definition; it may be useful only for a short, appropriately framed insert if its visual quality is acceptable. Do not upscale and call it HD/4K.
- A07 is a candidate ROV shot; its source page says Deep Discoverer can dive to 6,000 m and records HD video, but exact downloaded clip content must be visually checked before use.
