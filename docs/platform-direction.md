# Dooley World Platform Direction

## Purpose

dooley.world is the stable public front door and project directory for Sean
Dooley's software projects. It is not a single runtime, backend, or security
boundary containing every project.

## Platform Structure

- dooley.world is a stable, independently deployable landing page.
- www.dooley.world redirects to dooley.world.
- Substantial applications use their own subdomains, repositories, and Google
  Cloud projects.
- Small, browser-only experiments may share a labs project when they have no
  meaningful backend, data-isolation, billing, or security requirements.
- Experimental applications must not be able to disrupt the landing page or
  access another application's secrets, sessions, or data.

## Technology Direction

- Google Cloud is the underlying infrastructure platform.
- Firebase may be enabled selectively when it removes unnecessary web-platform
  plumbing, especially for static hosting and authentication.
- Firebase is a convenience layer, not an architectural requirement for every
  application.
- Workloads choose services according to their needs: Firebase Hosting for
  static content, App Hosting for supported full-stack frameworks, Cloud Run
  for configurable application backends, and other Google Cloud services as
  justified.
- Prefer managed, scale-to-zero services and the smallest practical
  architecture.
- Do not introduce persistent infrastructure or operational complexity for
  hypothetical future requirements.

## Identity Direction

- User identity will eventually be centralized in a dedicated identity project.
- auth.dooley.world is reserved as the central authentication entry point.
- A user receives one stable global identity.
- Authorization remains application-specific; a global account does not
  automatically grant access or roles in every application.
- Applications may remain in separate Google Cloud projects and verify tokens
  issued by the central identity service.
- Browser sessions must be host-specific. Do not use a master session cookie
  scoped to all of dooley.world.
- Seamless cross-subdomain SSO, when implemented, will use a trusted redirect
  and session-exchange flow rather than exposing tokens in URLs or sharing a
  domain-wide cookie.
- Direct client access to Firebase data in another project must not be assumed
  to work with central identity tokens; use an application API or an explicitly
  designed token exchange.

## Security and Cost Principles

- Each substantial application has an independent security, billing, quota,
  deployment, and failure boundary.
- Secrets never live in client code or source control.
- Billed projects require budgets, spending controls where supported, quotas,
  and runtime scaling limits.
- The public hub must remain available even if an experimental application
  fails or exhausts its resources.

## Initial Release

The first release is only a fast, responsive public landing page and project
directory. It does not implement authentication, application backends, a
database, or the future SSO system. It should preserve obvious extension points
for those capabilities without building them prematurely.
