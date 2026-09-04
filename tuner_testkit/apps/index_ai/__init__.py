"""index_ai — scan .cursor/** AI components and render a human-readable registry.

The rules / skills / agents / hooks under ``.cursor/`` are this platform's
"backend service" (business rules + handlers). This tool treats them as
first-class, versioned assets and deterministically renders
``.cursor/REGISTRY.md`` so human engineers can see, at a glance, which
components exist, how they trigger, and what version they are.
"""
