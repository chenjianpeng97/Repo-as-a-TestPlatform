-- auto-generated definition
create table issue_views
(
    created_at         timestamptz      not null,
    updated_at         timestamptz      not null,
    id                 uuid             not null
        primary key,
    name               varchar(255)     not null,
    description        text             not null,
    query              jsonb            not null,
    access             smallint         not null,
    filters            jsonb            not null,
    created_by_id      uuid             null,
    project_id         uuid             null,
    updated_by_id      uuid             null,
    workspace_id       uuid             not null,
    display_filters    jsonb            not null,
    display_properties jsonb            not null,
    sort_order         double precision not null,
    logo_props         jsonb            not null,
    is_locked          boolean          not null,
    owned_by_id        uuid             not null,
    deleted_at         timestamptz      null,
    rich_filters       jsonb            not null,
    archived_at        timestamptz      null
);

CREATE INDEX issue_views_created_by_id_0d2e456b ON issue_views USING btree (created_by_id);

CREATE INDEX issue_views_owned_by_id_5e261e5d ON issue_views USING btree (owned_by_id);

CREATE INDEX issue_views_project_id_55ee009f ON issue_views USING btree (project_id);

CREATE INDEX issue_views_updated_by_id_28cd9870 ON issue_views USING btree (updated_by_id);

CREATE INDEX issue_views_workspace_id_8785e03d ON issue_views USING btree (workspace_id);

-- 最新一条数据示例（latest id），已排除生成列，仅供数据构造参考
-- INSERT INTO "issue_views" ("created_at", "updated_at", "id", "name", "description", "query", "access", "filters", "created_by_id", "project_id", "updated_by_id", "workspace_id", "display_filters", "display_properties", "sort_order", "logo_props", "is_locked", "owned_by_id", "deleted_at", "rich_filters", "archived_at") VALUES ('2026-08-03 12:45:42.022473+00:00', '2026-08-03 12:45:42.022482+00:00', 'fe36dca3-24ba-4948-bf75-eb06da4b27d1', 'Project Urgent Tasks', 'Project Urgent Tasks', '{}', 1, '{}', '284b6766-d3bb-4a5d-a14f-de5d364cc3c4', '20f8ab45-bce1-44c8-854c-78972f51ed62', NULL, '82345500-e469-419d-843d-92902ffac9db', '{''layout'': ''list'', ''calendar'': {''layout'': ''month'', ''show_weekends'': False}, ''group_by'': ''state'', ''order_by'': ''sort_order'', ''sub_issue'': False, ''sub_group_by'': None, ''show_empty_groups'': False}', '{''key'': True, ''link'': True, ''cycle'': True, ''state'': True, ''labels'': True, ''modules'': True, ''assignee'': True, ''due_date'': True, ''estimate'': True, ''priority'': True, ''created_on'': True, ''issue_type'': True, ''start_date'': True, ''updated_on'': True, ''customer_count'': True, ''sub_issue_count'': True, ''attachment_count'': True, ''customer_request_count'': True}', 75535.0, '{}', FALSE, '284b6766-d3bb-4a5d-a14f-de5d364cc3c4', NULL, '{''priority__in'': ''urgent''}', NULL);
