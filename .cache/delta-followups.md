The single Sol delta review for the public checker refresh identified two additional coverage follow-ups, deferred under the agreed cap:

- Scan every container launch on a shell line. A pinned first launch followed by an unpinned second launch currently stops scanning after the first match (`scripts/check-container-images.mjs:329`).
- Scan multiline Testcontainers constructors against the complete source. A `new GenericContainer(` call whose literal image starts on the following line is currently missed (`scripts/check-container-images.mjs:271`).

Done when: hosted regression coverage rejects an unpinned second launch and a multiline unpinned Testcontainers image while retaining pinned controls. Refresh the public vendored checker with the shared fix.

The review also suggested relocating the source header (P3). That advice is rejected because this task explicitly requires a provenance header for the vendored copy.
