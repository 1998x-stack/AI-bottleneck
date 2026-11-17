# AGENTS.md — AI Bottleneck Observatory

## Mission
Keep an extensible, source-traceable cross-domain research library of AI production bottlenecks. Do not fabricate research, benchmark outcomes, product pricing, policy requirements, or publication success.

## Guardrails
- Source of truth: Markdown reports and structured catalog JSON in Git.
- Do not change domain schemaVersion without adjusting validator, migration plan and UI.
- A new issue must have stable ID, category, root cause, at least one actionable solution, limitations, acceptance metrics and >=1 existing source ID.
- Never label a planned domain as published. Never conflate engineering priority with statistical prevalence.
- No remote calls needed to render the published website; maintain relative asset paths for GitHub Pages subdirectory URLs.
- Escape untrusted strings in DOM. External links must use HTTPS, target=_blank, rel=noopener noreferrer.
- Changes must pass `node scripts/validate.mjs`, `node --check app.js`, `node --check markdown.js`, and `python scripts/build_site.py` after python-docx install.
- Preserve original report files; publish new dated versions rather than silently rewriting factual historical studies.
- Deployment is only confirmed after the GitHub Pages action succeeds AND the public URL responds successfully.

## Suggested workflow
1. Read catalog/index.json and docs/data-contract.md.
2. Create/update a domain file and sources file, add full Markdown in reports/.
3. Validate links and evidence strength, preserve uncertainty.
4. Run tests/build; inspect mobile viewport and dark/light modes.
5. Open PR with issue scope, source list, QA results, and impact on previous domains.
