-- auto-generated definition
create table module_user_properties
(
    created_at         timestamptz not null,
    updated_at         timestamptz not null,
    id                 uuid        not null
        primary key,
    filters            jsonb       not null,
    display_filters    jsonb       not null,
    display_properties jsonb       not null,
    created_by_id      uuid        null,
    module_id          uuid        not null,
    project_id         uuid        not null,
    updated_by_id      uuid        null,
    user_id            uuid        not null,
    workspace_id       uuid        not null,
    deleted_at         timestamptz null,
    rich_filters       jsonb       not null
);

CREATE INDEX module_user_properties_created_by_id_bdd98440 ON module_user_properties USING btree (created_by_id);

CREATE INDEX module_user_properties_module_id_e95b158a ON module_user_properties USING btree (module_id);

CREATE INDEX module_user_properties_project_id_3c5a4972 ON module_user_properties USING btree (project_id);

CREATE INDEX module_user_properties_updated_by_id_b7dafc77 ON module_user_properties USING btree (updated_by_id);

CREATE INDEX module_user_properties_user_id_e83a1c2c ON module_user_properties USING btree (user_id);

CREATE INDEX module_user_properties_workspace_id_ddaf807c ON module_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX module_user_properties_module_id_user_id_delete_3269582d_uniq ON module_user_properties USING btree (module_id, user_id, deleted_at);

CREATE UNIQUE INDEX module_user_properties_unique_module_user_when_deleted_at_null ON module_user_properties USING btree (module_id, user_id) WHERE (deleted_at IS NULL);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "module_user_properties" ("created_at", "updated_at", "id", "filters", "display_filters", "display_properties", "created_by_id", "module_id", "project_id", "updated_by_id", "user_id", "workspace_id", "deleted_at", "rich_filters") VALUES ('2026-08-15 14:05:06.814341+00:00', '2026-08-15 14:05:06.814353+00:00', '51932f3d-02ad-4cab-876a-6ce73e159e75', '{''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}', '{''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}', '{''key'': True, ''link'': True, ''state'': True, ''labels'': True, ''assignee'': True, ''due_date'': True, ''estimate'': True, ''priority'': True, ''created_on'': True, ''start_date'': True, ''updated_on'': True, ''sub_issue_count'': True, ''attachment_count'': True}', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6cb88123-3e5b-4ae8-b621-1831d41152ba', 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL, '{}');
