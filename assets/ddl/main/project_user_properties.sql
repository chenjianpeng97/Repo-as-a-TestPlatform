-- auto-generated definition
create table project_user_properties
(
    created_at         timestamptz      not null,
    updated_at         timestamptz      not null,
    id                 uuid             not null
        primary key,
    display_properties jsonb            not null,
    created_by_id      uuid             null,
    project_id         uuid             not null,
    updated_by_id      uuid             null,
    user_id            uuid             not null,
    workspace_id       uuid             not null,
    display_filters    jsonb            not null,
    filters            jsonb            not null,
    deleted_at         timestamptz      null,
    rich_filters       jsonb            not null,
    preferences        jsonb            not null,
    sort_order         double precision not null
);

CREATE INDEX issue_property_created_by_id_8e92131c ON project_user_properties USING btree (created_by_id);

CREATE INDEX issue_property_project_id_30e7de7b ON project_user_properties USING btree (project_id);

CREATE INDEX issue_property_updated_by_id_ff158d4d ON project_user_properties USING btree (updated_by_id);

CREATE INDEX issue_property_user_id_0b1d1c8f ON project_user_properties USING btree (user_id);

CREATE INDEX issue_property_workspace_id_17860d65 ON project_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX issue_user_properties_user_id_project_id_delet_2217dce5_uniq ON project_user_properties USING btree (user_id, project_id, deleted_at);

CREATE UNIQUE INDEX project_user_property_unique_user_project_when_deleted_at_null ON project_user_properties USING btree (user_id, project_id) WHERE (deleted_at IS NULL);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "project_user_properties" ("created_at", "updated_at", "id", "display_properties", "created_by_id", "project_id", "updated_by_id", "user_id", "workspace_id", "display_filters", "filters", "deleted_at", "rich_filters", "preferences", "sort_order") VALUES ('2026-08-17 11:44:50.031158+00:00', '2026-08-17 11:44:50.031169+00:00', 'e361af9d-d88f-48c5-a95e-2e156bacf856', '{''key'': True, ''link'': True, ''state'': True, ''labels'': True, ''assignee'': True, ''due_date'': True, ''estimate'': True, ''priority'': True, ''created_on'': True, ''start_date'': True, ''updated_on'': True, ''sub_issue_count'': True, ''attachment_count'': True}', NULL, '20f8ab45-bce1-44c8-854c-78972f51ed62', NULL, '631d3cce-56d5-4ab5-bbe4-8b3cc850a6bf', '82345500-e469-419d-843d-92902ffac9db', '{''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}', '{''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}', NULL, '{}', '{''pages'': {''block_display'': True}, ''navigation'': {''default_tab'': ''work_items'', ''hide_in_more_menu'': []}}', 55535.0);
