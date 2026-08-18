from __future__ import annotations


class ApiTestError(Exception):
    pass


class SchemaValidationError(ApiTestError):
    pass


class HeadersPolicyError(ApiTestError):
    pass


class AuthPolicyError(ApiTestError):
    pass


class FilesPolicyError(ApiTestError):
    """Raised when multipart file fields are missing or misused."""


class ApiAssertError(ApiTestError):
    pass

