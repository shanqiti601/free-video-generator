# Fact Bites agent operating guide

The coordinating assistant is editor-in-chief. Use available tools and configured free models for bounded tasks, then reconcile results. Model consensus is not evidence.

## Skills
- Fact checking: `.agents/skills/fact-bites-fact-check/SKILL.md` and `.claude/skills/fact-bites-fact-check/SKILL.md`
- Documentary scripts: `.agents/skills/fact-bites-documentary-script/SKILL.md` and `.claude/skills/fact-bites-documentary-script/SKILL.md`
- MP4 quality assurance: `.agents/skills/fact-bites-video-qa/SKILL.md` and `.claude/skills/fact-bites-video-qa/SKILL.md`
- YouTube metadata: `.agents/skills/fact-bites-youtube-publishing/SKILL.md` and `.claude/skills/fact-bites-youtube-publishing/SKILL.md`

Keep paired skill files synchronized.

## Fact Bites visual identity
- First 3–5 seconds: strongest relevant real footage and a defensible spoken hook.
- Bright, legible, full-bleed vertical 9:16; use restrained motion and clean cuts.
- On-screen text is limited to FACT BITES branding and concise FACT BITE cards with verified facts.
- No opening titles, slogans, generic subtitles, calls to action, or end cards unless explicitly requested.
- Spoken narration and subtle original ambience are allowed; do not burn full narration subtitles into the image.
- Keep all text within mobile-safe margins.

## Coordination and safety
- Use only explicitly free provider routes. Never infer that a model is free because a provider offers a free account tier.
- Never enable paid fallback, paid catalog features, subscriptions, or billing.
- Keep credentials in GitHub Actions secrets or encrypted local configuration. Never commit, print, or paste secrets into chat.
- If no free model is configured or quotas are exhausted, continue with deterministic checks and report skipped AI review accurately.
- Primary sources are required for factual claims.
- Do not publish to YouTube or perform irreversible external actions without explicit user authorization.
