-- auto-generated definition
create table cycle_user_properties
(
    created_at         timestamptz not null,
    updated_at         timestamptz not null,
    id                 uuid        not null
        primary key,
    filters            jsonb       not null,
    display_filters    jsonb       not null,
    display_properties jsonb       not null,
    created_by_id      uuid        null,
    cycle_id           uuid        not null,
    project_id         uuid        not null,
    updated_by_id      uuid        null,
    user_id            uuid        not null,
    workspace_id       uuid        not null,
    deleted_at         timestamptz null,
    rich_filters       jsonb       not null
);

CREATE INDEX cycle_user_properties_created_by_id_501f371c ON cycle_user_properties USING btree (created_by_id);

CREATE INDEX cycle_user_properties_cycle_id_1f8bdf35 ON cycle_user_properties USING btree (cycle_id);

CREATE INDEX cycle_user_properties_project_id_4efc0f07 ON cycle_user_properties USING btree (project_id);

CREATE INDEX cycle_user_properties_updated_by_id_1b5ac27b ON cycle_user_properties USING btree (updated_by_id);

CREATE INDEX cycle_user_properties_user_id_9e9ef97d ON cycle_user_properties USING btree (user_id);

CREATE INDEX cycle_user_properties_workspace_id_62d65d71 ON cycle_user_properties USING btree (workspace_id);

CREATE UNIQUE INDEX cycle_user_properties_cycle_id_user_id_deleted_at_fbe00cf4_uniq ON cycle_user_properties USING btree (cycle_id, user_id, deleted_at);

CREATE UNIQUE INDEX cycle_user_properties_unique_cycle_user_when_deleted_at_null ON cycle_user_properties USING btree (cycle_id, user_id) WHERE (deleted_at IS NULL);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "cycle_user_properties" ("created_at", "updated_at", "id", "filters", "display_filters", "display_properties", "created_by_id", "cycle_id", "project_id", "updated_by_id", "user_id", "workspace_id", "deleted_at", "rich_filters") VALUES ('2026-07-14 09:01:24.715920+00:00', '2026-07-14 09:01:24.715928+00:00', 'e2ed978c-096e-4fc4-846d-787640af084d', '{''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}', '{''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}', '{''key'': True, ''link'': True, ''state'': True, ''labels'': True, ''assignee'': True, ''due_date'': True, ''estimate'': True, ''priority'': True, ''created_on'': True, ''start_date'': True, ''updated_on'': True, ''sub_issue_count'': True, ''attachment_count'': True}', '9d1f264d-7dee-48c5-ab98-087db907b8a1', '2b651f63-062f-4632-83cf-267dee34a667', 'dc06dab7-13f5-40de-9d63-79d71315d44b', NULL, '9d1f264d-7dee-48c5-ab98-087db907b8a1', '6f2f3ff8-62de-4127-978b-54991c166df3', NULL, '{}');
