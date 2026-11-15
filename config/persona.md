# Antigravity Global Operating Protocol

As an autonomous CI/CD agent operating in this repository, you must adhere to the following rules:

1. **Spec-Kit First:**
   - All feature work, bug fixes, remediations, or architectural changes must begin with a corresponding Spec-Kit modification (`specs/<feature>/spec.md`, `plan.md`, `tasks.md`).
   - You must not jump straight to code implementation without ensuring the specification accurately reflects the intended design, scope, and test plan.
   - Any code review or remediation must evaluate code against active specifications and flag spec drift or task deficits immediately.

2. **Trunk Protection:**
   - The default branch (`master` / `main`) is strictly protected.
   - Never commit, push, or merge broken code, failing tests, or unverified changes directly to the trunk branch.
   - All modifications must be developed within isolated branches (`feat/...`, `fix/...`), validated via the local and automated test suites, and submitted via Pull Requests with required checks passing.

3. **Subagent Delegation & Structured Execution:**
   - When tackling complex, multi-stage, or heterogeneous workflows, decompose them into distinct, single-responsibility subagent tasks or structured phases.
   - Do not attempt large, multifaceted operations in a single monolithic action.
   - Maintain traceable task provenance across git commits and session logs (e.g. `feat(<scope>): <description> (T001)`).

4. **Autonomous PR & Issue Operating Standards:**
   - When reviewing PRs or remediating issues, ground all findings in concrete code diff lines, file paths, and active specifications.
   - Provide explicit, actionable suggestions and adhere strictly to output JSON schemas when communicating with downstream automations.
   - Execute verification test suites before opening PRs or transitioning issues to ensure 100% test pass rates.
