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

The generated environment file's encryption key is produced as base64 translated into the URL-safe alphabet, then
truncated at generation, rather than as hex — the key a stored external credential is encrypted with must be a URL-safe
base64-encoded value of the exact byte length that scheme requires, not an arbitrary secret string.

The generated database URL disables the driver's default requirement of a TLS connection — the schema-migration tool's
Postgres driver requires one unless told otherwise, and the compose-internal database it connects to has no TLS
configured at all; leaving the default in place fails every migration on first boot.

The published container image's tag is left unset by provisioning on purpose: cloud-init brings the host up to the point
of having Docker, the cloned repository, and a generated environment file, and deliberately stops there — the first
`compose up` with an actually-published tag, and the review of the generated admin password, are a manual step in the
same session, not something a provisioning script should do unattended.

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

The manual step this script deliberately stops before — publishing an image tag and bringing the stack up — is a
standing prerequisite for every future provisioning of a new host from this same script, not a one-time bootstrapping
quirk: whoever runs it again for a new host still has to complete that same manual step themselves.
