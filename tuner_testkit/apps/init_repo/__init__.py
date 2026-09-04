"""init_repo — the template's release artifact.

This template repo *is* the platform. ``init_repo`` (1) scaffolds a new project
repo with the six-layer skeleton and the shared "platform DNA" (.cursor
components, docs/spec, common packages/apps/tools), and (2) carries a
**release manifest** (version + content hashes of the bundled common assets) so
drift can be detected: when common ``packages/**`` or ``.cursor/**`` change but
the manifest version was not bumped, the drift check flags it. The
``release-template`` skill consumes that signal to bump the semantic version and
refresh the manifest.
"""
