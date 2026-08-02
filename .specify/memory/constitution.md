<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Adopted baseline: Dooley World Constitution 1.0.0
- Added principles:
  - I. Stable Hub, Independent Applications
  - II. Central Identity, Local Authority
  - III. Least Privilege and Protected Boundaries
  - IV. Managed Simplicity and Cost Control
  - V. Accessible, Testable Delivery
  - VI. Reproducible, Source-Linked Data
  - VII. Honest Coverage and Temporal Semantics
- Added sections:
  - Platform Constraints
  - Development and Quality Gates
- Removed sections: none
- Follow-up TODOs: none
-->
# CVUSD Calendar Atlas Constitution

## Core Principles

### I. Stable Hub, Independent Applications

The public Dooley World hub MUST remain a stable, independently deployable
front door and project directory. CVUSD Calendar Atlas MUST own its deployment,
security, data, billing, quota, and failure boundaries. It MUST NOT be able to
impair the hub or access another application's secrets, sessions, or data. This
isolation lets the project evolve and fail without widening the blast radius.

### II. Central Identity, Local Authority

CVUSD Calendar Atlas is anonymous and public unless a later specification
introduces identity. If identity is introduced, users MUST receive one stable
global identity from the dedicated Dooley World identity boundary while
authorization remains application-specific. Browser sessions MUST be
host-specific. Credentials or bearer tokens MUST NOT appear in URLs, and no
master cookie may be scoped to every subdomain. Cross-project data access MUST
use an explicit application API or deliberately designed token exchange.

### III. Least Privilege and Protected Boundaries

Secrets MUST NOT appear in client-delivered code, source control, logs, URLs, or
public artifacts. Every workload and human operator MUST receive only the
permissions required for the current responsibility. Trust boundaries, data
flows, and externally supplied input MUST be identified in the plan and covered
by proportionate validation and security tests. Public endpoints MUST use
secure transport and appropriate browser security controls. Security exceptions
require a documented owner, rationale, scope, and removal condition.

### IV. Managed Simplicity and Cost Control

Plans MUST prefer the smallest practical architecture and managed,
scale-to-zero services when they meet verified requirements. Persistent
infrastructure, frameworks, data stores, background processing, and
cross-application coupling MUST NOT be introduced for hypothetical future
needs. Every billed project MUST define budgets, enforceable spending controls
where supported, quotas, and runtime scaling limits before public operation.
Service choices MUST be justified by current workload needs, operational risk,
and total cost rather than uniformity.

### V. Accessible, Testable Delivery

Public experiences MUST support keyboard operation, meaningful structure,
readable contrast, responsive layouts, and assistive-technology use consistent
with WCAG 2.2 AA. Each feature MUST have independently testable user scenarios,
measurable technology-agnostic success criteria, and automated tests appropriate
to its risk. Changes MUST pass applicable functional, accessibility, security,
and integration checks before deployment. Operational features MUST define the
signals needed to diagnose user-visible failures.

### VI. Reproducible, Source-Linked Data

The public dataset MUST be reproducible from the checked-in collection process
and documented supplements. Every event MUST retain its underlying source and
all known publication paths. Normalization, recurrence expansion,
de-duplication, manual supplements, and source-specific workarounds MUST be
deterministic and documented. The dated archive and deployable UI mirror MUST
remain identical. A data refresh that cannot satisfy these invariants MUST NOT
replace the last validated dataset.

### VII. Honest Coverage and Temporal Semantics

The project MUST distinguish missing or unavailable public sources from an
absence of events and MUST retain coverage gaps and collection errors instead
of silently dropping them. The requested collection window is inclusive;
all-day event end dates are exclusive. Timed events MUST retain an explicit
timezone offset, and unknown end times MUST remain explicitly unknown. Source
uncertainty MUST be visible in the data or documentation and MUST NOT be
presented as verified fact.

## Platform Constraints

- Google Cloud is the underlying infrastructure platform unless this
  constitution is amended with a documented migration rationale.
- The application uses a dedicated Firebase/Google Cloud project and
  `cvusd.dooley.world`; it does not share the hub's runtime or cloud project.
- The public viewer remains a static, read-only client over a generated JSON
  artifact unless verified requirements justify a backend or data store.
- A service used by the Dooley World hub or another application does not become
  the default for this project.
- `docs/platform-direction.md` records the adopted Dooley World architectural
  direction. Feature specifications may refine it but MUST NOT silently
  contradict it.

## Development and Quality Gates

1. A specification MUST define user value, scope, exclusions, acceptance
   scenarios, edge cases, and measurable outcomes without prescribing an
   implementation.
2. Material ambiguities MUST be resolved before planning. Assumptions used in
   place of clarification MUST be explicit and testable.
3. A plan MUST document architecture, security boundaries, accessibility,
   verification, cost controls, data provenance, and any complexity that needs
   justification.
4. Tasks MUST trace to the approved specification and plan. Implementation MUST
   stop when either artifact would need a material change and obtain review.
5. A refresh MUST pass the validation checklist in `KNOWLEDGE.md`, including
   unique IDs, metadata counts, window bounds, ordering, documented errors, and
   byte-identical archive and UI output.
6. Reviews MUST verify constitutional compliance and preserve independent
   deployment and failure boundaries. Any exception follows the documented
   amendment or exception process.

## Governance

This constitution governs all CVUSD Calendar Atlas repository work and adopts
Dooley World Constitution 1.0.0 as its non-waivable baseline. The local
principles may add stricter constraints but cannot waive a baseline requirement.
The platform-direction document, feature specifications, plans, tasks, and
knowledge base may add constraints but cannot contradict this constitution.

Amendments require a documented proposal explaining the reason, affected
principles, compatibility impact, and migration work. The repository owner must
approve the change before dependent implementation proceeds. Version changes
follow semantic versioning: MAJOR for incompatible governance changes or
removed principles, MINOR for new principles or materially expanded
obligations, and PATCH for non-semantic clarification. A newer Dooley World
baseline MUST be reviewed and adopted explicitly; it is never inherited through
an unversioned local path.

Specification, plan, task, review, refresh, and release checkpoints MUST include
a constitution check. A temporary exception must identify its owner, narrow
scope, reason, expiration or removal condition, and tracked remediation.
Undocumented exceptions are invalid.

**Project Version**: 1.0.0 | **Dooley World Baseline**: 1.0.0 | **Ratified**: 2026-08-02 | **Last Amended**: 2026-08-02
