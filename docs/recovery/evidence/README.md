# Original numerical evidence backup

These three ZIP files preserve the original downloaded Actions artifact bytes,
including their original JSON member bytes. They are committed in Git, rather
than links to expiring artifacts. The manifest records sizes, SHA-256 digests,
reviewed heads, workflow/artifact identifiers and original hosted expiry dates.
The archived reports contain their source identities. The Q-ball report's CI
merge identity differs from its PR head; preserve the identity embedded in the
report rather than silently replacing it with a later commit.

The scope is the three reviewed result packages from PR159, PR163 and PR166.
This is not a backup of every historical experiment, source document, supplied
image, dependency environment or machine. Existing local originals remain intact.
The archive preserves evidence, not a claim of physical validity, broad stability
or successful completion of every research task.

From a checkout containing this commit, verify without a scientific environment:

```text
python scripts/verify_recovery_evidence.py
```

To restore, copy any ZIP to a separate destination and open it with a ZIP reader.
Verify its archive and member hashes against `manifest.json`. Do not overwrite
scientific source or working reports as part of restoring evidence. The verifier
checks the entire member inventory and JSON readability without extraction or
simulation. A fresh checkout plus this command is also a backup restore check.

Reproduction entry points in the manifest are for the corresponding recorded
source revision and its dependency environment. Rerunning an experiment is not
byte-for-byte recovery: floating-point output may differ across environments.
In particular, the graph JSON working copy used during review was reserialized;
the ZIP here preserves the original member bytes instead.

Keep these files and hashes immutable. Future evidence should use a new archive
and a separately reviewed manifest/version. Once published, ordinary Git clones
provide an additional copy independent of Actions retention. That does not make
GitHub immune to deletion or replace a separate organizational disaster-recovery
policy; retain the local copies as well.
