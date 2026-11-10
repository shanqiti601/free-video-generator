# Fact Bites agent operating guide

Load the relevant portable Agent Skill before working on this channel:
- Fact checking: `.agents/skills/fact-bites-fact-check/SKILL.md`
- Documentary scripts: `.agents/skills/fact-bites-documentary-script/SKILL.md`
- MP4 quality assurance: `.agents/skills/fact-bites-video-qa/SKILL.md`
- YouTube publishing metadata: `.agents/skills/fact-bites-youtube-publishing/SKILL.md`

## Coordination and safety
- The coordinating assistant acts as editor-in-chief and reconciles bounded work from available models/tools.
- Model consensus is not evidence; factual claims require primary-source verification.
- Use only explicitly free provider routes. Never infer that a model is free because a provider offers a free account tier.
- Never enable paid fallback, paid catalog features, subscriptions, or billing.
- Keep credentials in repository Actions secrets or encrypted local configuration. Never commit, print, or paste secrets into chat.
- If no free model is configured or quotas are exhausted, continue with deterministic checks and report skipped AI review accurately.
- Do not publish to YouTube or perform irreversible external actions without explicit user authorization.
