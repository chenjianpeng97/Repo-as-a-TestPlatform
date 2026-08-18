-- auto-generated definition
create table workspace_user_properties
(
    created_at                    timestamptz not null,
    updated_at                    timestamptz not null,
    id                            uuid        not null
        primary key,
    filters                       jsonb       not null,
    display_filters               jsonb       not null,
    display_properties            jsonb       not null,
    created_by_id                 uuid        null,
    updated_by_id                 uuid        null,
    user_id                       uuid        not null,
    workspace_id                  uuid        not null,
    deleted_at                    timestamptz null,
    rich_filters                  jsonb       not null,
    navigation_control_preference varchar(25) not null,
    navigation_project_limit      integer     not null
);

CREATE INDEX workspace_user_properties_created_by_id_6d8d1c4e ON workspace_user_properties USING btree (created_by_id);

CREATE INDEX workspace_user_properties_updated_by_id_910a2cc5 ON workspace_user_properties USING btree (updated_by_id);

CREATE INDEX workspace_user_properties_user_id_b1079e07 ON workspace_user_properties USING btree (user_id);

CREATE INDEX workspace_user_properties_workspace_id_1dc3e2a6 ON workspace_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX workspace_user_propertie_workspace_id_user_id_del_a7cf15bc_uniq ON workspace_user_properties USING btree (workspace_id, user_id, deleted_at);

CREATE UNIQUE INDEX workspace_user_properties_unique_workspace_user_when_deleted_at ON workspace_user_properties USING btree (workspace_id, user_id) WHERE (deleted_at IS NULL);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "workspace_user_properties" ("created_at", "updated_at", "id", "filters", "display_filters", "display_properties", "created_by_id", "updated_by_id", "user_id", "workspace_id", "deleted_at", "rich_filters", "navigation_control_preference", "navigation_project_limit") VALUES ('2026-07-10 12:38:05.412978+00:00', '2026-07-10 12:38:05.412989+00:00', 'a5240627-728d-4294-8b32-9e41e0e9b739', '{''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}', '{''display_filters'': {''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}}', '{''display_properties'': {''key'': True, ''link'': True, ''state'': True, ''labels'': True, ''assignee'': True, ''due_date'': True, ''estimate'': True, ''priority'': True, ''created_on'': True, ''start_date'': True, ''updated_on'': True, ''sub_issue_count'': True, ''attachment_count'': True}}', '9d1f264d-7dee-48c5-ab98-087db907b8a1', NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL, '{}', 'ACCORDION', 10);
