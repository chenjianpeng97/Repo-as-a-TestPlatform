from __future__ import annotations


class ApiMockError(Exception):
    pass


class MockSpecError(ApiMockError):
    """A mock definition file is malformed or violates the schema."""


class RouteNotFoundError(ApiMockError):
    """No mock definition exists for the requested ``method + path``."""


class ScenarioNotFoundError(ApiMockError):
    """The route exists but has no scenario under that name."""
