"""Fallback kind for ``@tool`` apps (``/tools``)."""

KIND = {
    "kind_id": "apps",
    "label": "工具",
    "item_type": "tool",
    "category": None,
    "destructive_default": False,
    "list_path": "/tools",
    "list_template": "tools.html",
    "detail_template": "tool.html",
    "home_card": True,
}
