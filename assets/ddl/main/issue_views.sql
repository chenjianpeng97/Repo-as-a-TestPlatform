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

