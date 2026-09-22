"""Fallback kind for action-word categories that do not yet have a specialized page."""

LABELS = {
    "db_seed": "造数",
    "db_assert": "库断言",
    "api_request": "接口请求",
    "api_assert": "接口断言",
    "ui_action": "页面操作",
    "ui_assert": "页面断言",
}

KIND = {
    "kind_id": "word",
    "label": "动作词",
    "item_type": "word",
    "category": None,
    "destructive_default": False,
    "list_path": "/words/db_assert",
    "list_template": "words.html",
    "detail_template": "word.html",
    "home_card": True,
}
