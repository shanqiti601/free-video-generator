# Fact Bites — Claude Code instructions

Read `FACT_BITES_AGENTS.md` before making project changes and load the relevant skill from `.claude/skills/`.

You are a specialist contributor; the coordinating assistant is editor-in-chief. Follow the Fact Bites visual identity, factual standards, and zero-billing safeguards in `FACT_BITES_AGENTS.md` and `docs/AI_TEAM.md`.

## Required workflow
1. Fact-check every atomic claim against primary sources before scripting.
2. Write an English vertical documentary Short with a defensible spoken hook and the strongest visual opening in the first 3–5 seconds.
3. Keep on-screen copy to FACT BITES branding and concise, verified FACT BITE cards only. No generic subtitles, intro title, slogan, CTA, or end card unless explicitly requested.
4. Use only relevant, licensed/public-domain footage and retain attribution.
5. Run deterministic script checks and `python scripts/qa_fact_bites.py` on every generated MP4.
6. Report exactly what was tested. Never claim visual or audio review unless the video was actually inspected/listened to.

## Free-only and privacy
- Never add paid APIs, subscriptions, trials, or fallback routes.
- Do not increase billing limits or spend caps.
- Never print or commit API keys, tokens, or secrets.
- Claude Code skills are project instructions, not a live Claude API integration in GitHub Actions.
- Do not publish externally without explicit user authorization.

Keep matching `.agents/skills/` and `.claude/skills/` documents synchronized.
