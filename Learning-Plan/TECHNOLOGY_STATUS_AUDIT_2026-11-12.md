# Technology Status Audit — 2026-11-12

This is a point-in-time audit of sources relevant to the Week 8/9 retrieval and
MCP work. Preview/GA labels apply only to the cited product surface; they are
not endorsements or architecture decisions.

| Area | Verified source state | Curriculum consequence |
|---|---|---|
| MCP specification | The published revision checked is `2026-07-28`. It defines stateless requests and Streamable HTTP/stdio; HTTP authorization is optional at protocol level, but HTTP implementations that use authorization should follow the spec. The deprecated registry lists HTTP+SSE (deprecated `2025-03-26`, migrate to Streamable HTTP) and Dynamic Client Registration (deprecated `2026-07-28`, migrate to CIMD; earliest removal `2027-07-28`). The feature lifecycle policy normally requires a 12-month minimum window. | Do not build on initialization/session-bound behavior or deprecated HTTP+SSE/DCR. Keep identity host-supplied. The Week 9 stdio learning adapter does not implement remote HTTP authorization. Re-check before production. |
| MCP feature lifecycle | The official extension index separates Stable, Beta, and Experimental. At audit: MCP Apps is Stable; MCP Tasks is Beta (destination Core); Skills over MCP and Server Cards are Beta with destination not stated. Experimental extensions may change or disappear. The current official extension list does not identify a stable general file-transfer extension. | Treat experimental extensions as optional, explicitly negotiated and version-pinned; do not make a file-transfer extension a dependency without a newly verified specification and need. |
| A2A specification | The official latest release checked is `1.0.0`; its model covers agent cards, messages, tasks, artifacts and protocol bindings. | Use the official specification for discovery/delegation contracts; keep peer output untrusted and do not assume shared internal state or authority. |
| MCP Python SDK | The official `v2.3.0` release is dated 2026-10-02 and uses the v2 `MCPServer` API. The Week 9 project targets `<3`; older Week 3/4 projects still use v1-era APIs. | Keep Week 9 in its own dependency environment until older projects are deliberately migrated. Do not upgrade shared environments as a side effect of this exercise. |
| Microsoft Agent Framework | The `python-1.25.0` release is dated 2026-11-07 and requires Python 3.11 or later. This audit did not establish an overall GA/maturity classification for every integration. | Treat it as a candidate for later runtime comparison, not a selected Week 9 dependency. Confirm the specific feature's support status before adoption. |
| Azure AI Search | Microsoft lists `2026-04-01` as the latest stable data-plane API and `2026-08-01-preview` as the latest preview API. Foundry IQ documentation says some features are GA and others remain preview, depending on API version; portal access remains preview-only for agentic retrieval. | Separate stable classic search capabilities from preview agentic retrieval features. Check region, API version, and feature availability at design time. |
| OpenAI Evals platform | The official guide says the platform became read-only on 2026-10-31 and is scheduled to shut down on 2026-11-30. It directs new evaluation work toward Datasets. | Do not make the legacy Evals platform a required curriculum dependency; preserve evaluation cases in versioned, portable data. |
| OpenTelemetry GenAI conventions | GenAI conventions live in a separate repository. Its README still lists the Schema URL as `TODO`. | Use a project-owned telemetry contract and map to OTel conventions with explicit versioning; do not treat the GenAI schema as a stable app contract without rechecking. |

## Official sources

- [MCP 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
- [MCP deprecated features registry](https://modelcontextprotocol.io/specification/draft/deprecated)
- [MCP feature lifecycle and deprecation policy](https://modelcontextprotocol.io/community/feature-lifecycle)
- [MCP Python SDK v2.3.0 release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.3.0)
- [Microsoft Agent Framework Python 1.25.0 release](https://github.com/microsoft/agent-framework/releases/tag/python-1.25.0)
- [Azure AI Search stable and preview API versions](https://learn.microsoft.com/en-us/rest/api/searchservice/search-service-api-versions)
- [What is Foundry IQ?](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq)
- [OpenAI evals guide and deprecation notice](https://developers.openai.com/api/docs/guides/evals)
- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)

## CI action pins

The repository workflow pins third-party actions to the following commit SHAs,
verified from their official release tag references on the audit date:

| Action | Release | Commit |
|---|---|---|
| [actions/checkout](https://github.com/actions/checkout/releases/tag/v7.0.1) | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| [actions/setup-python](https://github.com/actions/setup-python/releases/tag/v7.1.0) | `v7.1.0` | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| [gitleaks/gitleaks-action](https://github.com/gitleaks/gitleaks-action/releases/tag/v3.0.0) | `v3.0.0` | `e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e` |
| [actions/dependency-review-action](https://github.com/actions/dependency-review-action/releases/tag/v5.0.0) | `v5.0.0` | `a1d282b36b6f3519aa1f3fc636f609c47dddb294` |

Recheck the primary sources before upgrading dependencies or relying on
preview-only features. This audit does not claim that any provider or framework
was tested in production.

## Repository workflow configuration

The executable workflow is
[`.github/workflows/security-check.yml`](../.github/workflows/security-check.yml).
Its current configured gates are:

- Third-party actions use the immutable commit SHAs in the table above.
- The Week 9 project runs with Python `3.11` in its own
  `Week-9-RAG-Implementation/.venv`; it installs only that project's
  `.[test]` dependencies and does not change older Week 3/4 environments.
- Blocking checks run Ruff on Week 9 source/tests, Week 9 pytest with branch
  coverage and an 80% configured minimum, `pip-audit` on the isolated installed
  environment, and Bandit on Week 9 source.
- The repository-history secret scan and tracked `.env`/key checks are
  blocking. Pull requests also run the dependency-review action with a
  high-severity failure threshold.
- No `continue-on-error` or silent dependency/security fallback is configured.
  The local validation performed for this edit is reported separately; this
  audit does not claim a GitHub Actions run passed.

The audit verifies the action commit objects and release references listed in
the pin table. Workflow execution still depends on repository settings,
available runners, and the actual GitHub Actions run.

