-- auto-generated definition
create table project_members
(
    created_at    timestamptz      not null,
    updated_at    timestamptz      not null,
    id            uuid             not null
        primary key,
    comment       text             null,
    role          smallint         not null,
    created_by_id uuid             null,
    member_id     uuid             null,
    project_id    uuid             not null,
    updated_by_id uuid             null,
    workspace_id  uuid             not null,
    view_props    jsonb            not null,
    default_props jsonb            not null,
    sort_order    double precision not null,
    preferences   jsonb            not null,
    is_active     boolean          not null,
    deleted_at    timestamptz      null
);

CREATE INDEX project_member_created_by_id_8b363306 ON project_members USING btree (created_by_id);

CREATE INDEX project_member_member_id_9d6b126b ON project_members USING btree (member_id);

CREATE INDEX project_member_project_id_11ea1a9e ON project_members USING btree (project_id);

CREATE INDEX project_member_updated_by_id_cf6aaac4 ON project_members USING btree (updated_by_id);

CREATE INDEX project_member_workspace_id_88bb9a97 ON project_members USING btree (workspace_id);

CREATE UNIQUE INDEX project_member_unique_project_member_when_deleted_at_null ON project_members USING btree (project_id, member_id) WHERE (deleted_at IS NULL);

CREATE UNIQUE INDEX project_members_project_id_member_id_deleted_at_0299122d_uniq ON project_members USING btree (project_id, member_id, deleted_at);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "project_members" ("created_at", "updated_at", "id", "comment", "role", "created_by_id", "member_id", "project_id", "updated_by_id", "workspace_id", "view_props", "default_props", "sort_order", "preferences", "is_active", "deleted_at") VALUES ('2026-08-17 11:44:50.032364+00:00', '2026-08-17 11:44:50.032373+00:00', 'fb4fb65e-7318-480b-8654-f924e29d0d20', NULL, 20, NULL, '631d3cce-56d5-4ab5-bbe4-8b3cc850a6bf', '20f8ab45-bce1-44c8-854c-78972f51ed62', NULL, '82345500-e469-419d-843d-92902ffac9db', '{''filters'': {''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}, ''display_filters'': {''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}}', '{''filters'': {''state'': None, ''labels'': None, ''priority'': None, ''assignees'': None, ''created_by'': None, ''start_date'': None, ''subscriber'': None, ''state_group'': None, ''target_date'': None}, ''display_filters'': {''type'': None, ''layout'': ''list'', ''group_by'': None, ''order_by'': ''-created_at'', ''sub_issue'': True, ''show_empty_groups'': True, ''calendar_date_range'': ''''}}', 65535.0, '{''pages'': {''block_display'': True}, ''navigation'': {''default_tab'': ''work_items'', ''hide_in_more_menu'': []}}', TRUE, NULL);
