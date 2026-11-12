# Technology Status Audit — 2026-11-12

This is a point-in-time audit of sources relevant to the Week 8/9 retrieval and
MCP work. Preview/GA labels apply only to the cited product surface; they are
not endorsements or architecture decisions.

| Area | Verified source state | Curriculum consequence |
|---|---|---|
| MCP specification | The published revision is `2026-07-28`. HTTP authorization is optional at protocol level; when used, HTTP implementations should follow the authorization specification. The specification recommends OAuth Client ID Metadata Documents; Dynamic Client Registration remains optional. | Keep identity host-supplied. Do not claim the stdio learning adapter implements remote HTTP authorization. Re-check the specification before a production deployment. |
| MCP Python SDK | The official `v2.3.0` release is dated 2026-10-02 and uses the v2 `MCPServer` API. The Week 9 project targets `<3`; older Week 3/4 projects still use v1-era APIs. | Keep Week 9 in its own dependency environment until older projects are deliberately migrated. Do not upgrade shared environments as a side effect of this exercise. |
| Microsoft Agent Framework | The `python-1.25.0` release is dated 2026-11-07 and requires Python 3.11 or later. This audit did not establish an overall GA/maturity classification for every integration. | Treat it as a candidate for later runtime comparison, not a selected Week 9 dependency. Confirm the specific feature's support status before adoption. |
| Azure AI Search | Microsoft lists `2026-04-01` as the latest stable data-plane API and `2026-08-01-preview` as the latest preview API. Foundry IQ documentation says some features are GA and others remain preview, depending on API version; portal access remains preview-only for agentic retrieval. | Separate stable classic search capabilities from preview agentic retrieval features. Check region, API version, and feature availability at design time. |
| OpenAI Evals platform | The official guide says the platform became read-only on 2026-10-31 and is scheduled to shut down on 2026-11-30. It directs new evaluation work toward Datasets. | Do not make the legacy Evals platform a required curriculum dependency; preserve evaluation cases in versioned, portable data. |
| OpenTelemetry GenAI conventions | GenAI conventions live in a separate repository. Its README still lists the Schema URL as `TODO`. | Use a project-owned telemetry contract and map to OTel conventions with explicit versioning; do not treat the GenAI schema as a stable app contract without rechecking. |

## Official sources

- [MCP 2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28)
- [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
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

