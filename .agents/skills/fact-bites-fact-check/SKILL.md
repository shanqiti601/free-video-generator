---
name: fact-bites-fact-check
description: Verify factual claims, dates, numbers, scientific statements, and source quality for Fact Bites documentary videos.
---

# Fact Bites Fact-Check

Use this skill before approving any factual documentary narration.

## Rules
- Break the narration into atomic, checkable claims.
- Prefer primary sources: peer-reviewed papers, government science agencies, universities, museums, official datasets, and original research releases.
- For scientific claims, locate the original paper and verify the exact wording, sample size, method, uncertainty, and publication date.
- Distinguish measured results from estimates, hypotheses, and popular summaries.
- Check whether a statistic is current and whether its denominator, units, and timeframe are clear.
- Never invent a citation, quote, source title, URL, or researcher.
- If web access is unavailable, mark the claim UNVERIFIED; do not silently approve it.
- Flag sensational hooks that overstate what the evidence shows.
- For each claim, return: status (SUPPORTED / QUALIFIED / UNVERIFIED / CONTRADICTED), evidence, source URL, and a safer replacement if needed.
- A second model's agreement is not evidence. Independent source verification is required.

## Output
1. Claim-by-claim verdict table.
2. Three strongest primary sources.
3. Corrections required before publication.
4. Overall decision: PASS / PASS WITH CHANGES / HOLD.
