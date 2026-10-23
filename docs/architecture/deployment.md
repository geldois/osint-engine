# Deployment — what it does

A single Ubuntu host is provisioned once, by a cloud-init script handed to the provider at creation time, then updated
only by the continuous-delivery workflow re-pulling and re-composing a newly published image — nothing after
provisioning ever re-runs cloud-init or touches the generated environment file again.

## Decisions

Docker is installed from its own official apt repository rather than the distribution's bundled package, pinned to one
explicit version string built from the release codename — the bundled package lags upstream, and the official
repository's layout is portable across Ubuntu codenames without hand-tracking one per release.

Automatic security patching is enabled with automatic rebooting explicitly disabled: an unexpected reboot arriving near
a demo is worse than a kernel patch sitting pending until the next manual one.

The container runtime's own log driver is capped by size and file count — without an explicit limit, container log
output grows without bound on a host nobody is otherwise rotating logs on.

The generated environment file's encryption key is produced as base64 translated into the URL-safe alphabet at
generation, rather than as hex — the key a stored external credential is encrypted with must be a URL-safe
base64-encoded value of the exact byte length that scheme requires, not an arbitrary secret string.

The generated database URL disables the driver's default requirement of a TLS connection — the schema-migration tool's
Postgres driver requires one unless told otherwise, and the compose-internal database it connects to has no TLS
configured at all; leaving the default in place fails every migration on first boot.

The published container image's tag is left unset by provisioning on purpose: cloud-init stops once the host has Docker,
the cloned repository and a generated environment file. The first pipeline run supplies the tag inline and brings the
stack up; the one-time repository secrets and variable the pipeline needs are the manual part, done in the same session,
not something a provisioning script should do unattended.

The application is never exposed directly: a reverse proxy container owns ports 80 and 443, obtains and renews the
certificate for the configured domain by itself, and forwards to the application on the compose-internal network only.
Production is the base compose file plus an overlay that adds the proxy, pins the application to a published image tag
passed in at deploy time, and feeds the database service its credentials from the host's environment file, so the same
base file still serves local development unchanged.

The overlay also makes the application trust the client address the proxy forwards. Without it every request appears to
come from the proxy itself, so every per-address rate limit — signup and login — collapses into one global bucket that a
single caller can exhaust for everyone. Trusting that header is safe only because nothing reaches the application except
through the proxy; exposing the application directly would let a caller forge its address and dodge those limits, which
makes this the first thing to revisit if that ever changes.

The image is built per architecture and pushed by digest, then a second job joins the digests into one multi-arch
manifest tagged both with the branch and with the commit SHA. The SHA tag is what the deploy pulls, so the running
container is always the exact commit the verification gate passed, never whatever a moving tag points at when the host
happens to pull. The host's own checkout, which supplies the compose files, is reset to exactly that commit on every
deploy, with no reconciliation: the files can never be ahead of, behind or different from the repository, and any local
edit to a tracked file on the host is discarded. Untracked files, such as the generated environment file, are left
untouched. The host also runs an intrusion-banning service for SSH, since it is exposed to the internet and nobody
watches its logs.

## Consequences

Because the Docker version string is built from the release codename at provisioning time, re-running this same script
against a newer Ubuntu release picks up whatever version that repository publishes for that codename automatically —
nothing here pins a single Docker version across every possible host release.

Leaving automatic reboot disabled means a pending kernel update stays pending indefinitely until someone reboots the
host by hand; nothing here ever revisits that decision on its own, so an operator has to actually check for and apply
that reboot, not assume automatic patching already closed the loop.

Since the internal database connection has TLS explicitly disabled, that connection's safety depends entirely on staying
compose-internal, never exposed beyond this host's own private network — extending this setup to a database reachable
from outside this host needs TLS revisited first, not inherited from this configuration as-is.

The manual steps this script deliberately leaves — setting the pipeline's repository secrets and variable for the new
host, and triggering the first run — are a standing prerequisite for every future provisioning of a new host from this
same script, not a one-time bootstrapping quirk: whoever runs it again still has to complete them themselves.

The schema-migration command resolves its migrations directory relative to the working directory, which only works
because the image sets that directory and copies the migrations into it; an installation from a built wheel run outside
the repository or container root cannot find them, since they are not package data. That is fine for a deployment target
that is only ever the container, and needs revisiting the day another install path appears.

## Open problems

- **The deploy secrets are repository secrets, not environment secrets.** `.github/workflows/publish-image.yml` reads
  the host address and the SSH key in a job tied to no GitHub environment, so any workflow in the repository can read
  them and no required reviewer can gate the deploy. The workflow analyser flags this only at its auditor persona.
  Create an environment named for production, move the two deploy secrets into it, set the deploy job's environment to
  it and, if wanted, add a required reviewer; do it before a second contributor or a second workflow can touch the
  repository
- **`main` has no branch protection or ruleset.** Without them, anything can still reach `main` without having passed
  the gate. In the GitHub web UI: repository Settings, Rules, Rulesets, New branch ruleset, target `main`; enable
  "Require status checks to pass" and add the check `test` (it must have run once on a pushed branch to appear), keep
  "Require linear history", "Block force pushes" and "Restrict deletions", and leave bypass empty so admins are bound
  too
- **The deploy is one VM running `compose.prod.yml`, with no orchestrator.** A crashed container only comes back through
  `restart`, there is no rolling update, no second replica and no fixed network addressing, and the in-memory snapshot
  (`MemStorage`) would make a second replica diverge from the first anyway. Move to Kubernetes (services, probes,
  network policies, a stable address for the ingress) when the persistence problem in the infrastructure document is
  closed and a second replica or a second host is wanted; until then compose is the proportionate choice
- **`FORWARDED_ALLOW_IPS: "*"` in `compose.prod.yml` trusts every peer, because the compose network has no fixed subnet
  and the Caddy address is not stable.** The per-IP limits (login, registration) key on `request.client.host`, so a
  published port in place of `expose` would let a direct caller forge the header past every bucket. Declare a network
  with a fixed subnet and trust only that CIDR when a service other than Caddy that can reach `app` joins the network or
  the `expose` line is touched
