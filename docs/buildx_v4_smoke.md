# Non-publishing Buildx v4 check

PR #118 updates Buildx only in the existing publication job, which is skipped
on pull requests. Its green PR checks therefore do not exercise the changed
action. This separate workflow makes the missing execution reviewable without
changing publication behavior.

On a relevant PR to main or recovery, or a manual run, the hosted Ubuntu job
creates a builder with `docker/setup-buildx-action@v4` and passes that builder
to the existing `docker/build-push-action@v7`. It builds the actual root
Dockerfile, including the Python/uv multi-stage copy and API dependencies,
loads one linux/amd64 image locally, checks its non-root user and API import,
and starts the API for a localhost health check.

The build uses `push: false` and `load: true`. There is no registry login,
registry secret, image publication, or package-write permission. Public base
images and dependencies still require network downloads. Existing Dockerfile
and scientific implementation remain unchanged. The publication workflow keeps
PR #118's original one-line Buildx v3-to-v4 upgrade; its triggers, credentials,
permissions and publishing behavior are unchanged.

This check covers builder setup, a representative real application build and
local runtime startup. It does not validate registry authentication or pushes,
multi-platform output, SBOM/provenance attestation publication, or a physical
deployment. The local image load explicitly disables attestations. A successful
run provides execution evidence for the action upgrade, not proof of those
separate publication capabilities.

Local preparation included static workflow checks only. Docker and actionlint
were unavailable in the preparation environment; no local or hosted Buildx
success is claimed until this workflow actually runs.
