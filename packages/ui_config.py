from __future__ import annotations

from dataclasses import dataclass
import os

from config import env as env_config


@dataclass(frozen=True)
class UIConfig:
    dms_base_url: str
    channel_base_url: str
    login_path: str
    channel_login_path: str
    home_url_keyword: str
    password_error_keywords: tuple[str, ...]

    @staticmethod
    def from_runtime(*, userdata: dict[str, str] | None = None) -> "UIConfig":
        userdata = userdata or {}

        # DMS system (auth/authorization management)
        dms_base_url = (
            userdata.get("dms_base_url")
            or userdata.get("base_url")
            or os.getenv("DMS_BASE_URL")
            or env_config.URL_DMS
        ).strip().rstrip("/")

        # Channel system (inout/sales chain)
        channel_base_url = (
            userdata.get("channel_base_url")
            or os.getenv("CHANNEL_BASE_URL")
            or os.getenv("DMS_CHANNEL_BASE_URL")
            or env_config.URL_INOUT
        ).strip().rstrip("/")

        login_path = (userdata.get("login_path") or os.getenv("DMS_LOGIN_PATH") or "/").strip() or "/"
        if not login_path.startswith("/"):
            login_path = "/" + login_path

        channel_login_path = (
            userdata.get("channel_login_path")
            or os.getenv("CHANNEL_LOGIN_PATH")
            or os.getenv("DMS_CHANNEL_LOGIN_PATH")
            or "/user/login"
        ).strip() or "/user/login"
        if not channel_login_path.startswith("/"):
            channel_login_path = "/" + channel_login_path

        home_url_keyword = (userdata.get("home_url_keyword") or os.getenv("DMS_HOME_URL_KEYWORD") or "").strip()
        # Default to empty: HomePage will use a generic fallback assertion.
        # Configure this explicitly if you want a strict URL check after login.

        password_error_keywords_raw = (
            userdata.get("password_error_keywords")
            or os.getenv("DMS_PASSWORD_ERROR_KEYWORDS")
            or "密码,错误,不正确"
        )
        password_error_keywords = tuple(
            k.strip() for k in password_error_keywords_raw.split(",") if k.strip()
        )

        return UIConfig(
            dms_base_url=dms_base_url,
            channel_base_url=channel_base_url,
            login_path=login_path,
            channel_login_path=channel_login_path,
            home_url_keyword=home_url_keyword,
            password_error_keywords=password_error_keywords,
        )

