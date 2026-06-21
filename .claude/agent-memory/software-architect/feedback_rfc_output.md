---
name: rfc-output-convention
description: How to deliver architecture RFCs for AIAPI
metadata:
  type: feedback
---

Architecture deliverables for AIAPI are RFC documents written to `docs/rfc/` named
`YYYYMMDD-<feature>.md`, in English, using Mermaid for diagrams and OpenAPI 3.x YAML
for API contracts.

**Why:** the role is software architect — deliverable is the design (RFC + artifacts),
never production Python. Implementation is deferred to the dev team/agent.
**How to apply:** when asked to "add a feature", produce the RFC; do not write src/ code.
